# -*- coding: utf-8 -*-
"""
=============================================================================
File: models/warranty_claim.py
Model: cmcts_warranty.warranty.claim  →  Bảng DB: cmcts_warranty_warranty_claim
=============================================================================
MỤC ĐÍCH:
  Lưu trữ Phiếu Yêu Cầu Bảo Hành (YCBH).
  Khi khách hàng mang thiết bị đến, nhân viên tiếp nhận tạo 1 record tại đây
  để theo dõi quy trình sửa chữa từ đầu đến cuối.

LUẬT NGHIỆP VỤ ĐƯỢC HIỆN THỰC TRONG FILE NÀY:
  [QT10] Mã tự động:         CLM/0001, CLM/0002, ... (không nhập tay)
  [QT11] 1 BH = 1 YCBH:     Mỗi phiếu BH chỉ được có đúng 1 YCBH (mọi trạng thái)
  [QT12] BH phải còn hạn:   is_valid = True nếu ngày tiếp nhận ≤ ngày hết hạn BH
  [QT13] Phân quyền UI:     Kỹ thuật viên chỉ điền kết quả + bấm nút trạng thái
                             (Nhân viên tiếp nhận mới được tạo/sửa các trường chính)
  [QT14] Quy trình 1 chiều: Tiếp nhận → Đang xử lý → Hoàn thành / Từ chối
                             Không thể đảo ngược khi đã Hoàn thành hoặc Từ chối
  [QT15] Chỉ chọn KTV:      Dropdown technician_id chỉ hiển thị user trong nhóm KTV

QUAN HỆ:
  ← cmcts_warranty.warranty (Many2one, warranty_id)

QUY TRÌNH XỬ LÝ (State Machine):
  [1_received] → [2_processing] → [3_done]
       ↓                ↓
  [4_rejected]     [4_rejected]
=============================================================================
"""
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WarrantyClaim(models.Model):
    _name = 'cmcts_warranty.warranty.claim'
    _description = 'Phiếu Yêu Cầu Bảo Hành'
    _inherit = ['mail.thread', 'mail.activity.mixin']   # Chatter: tự log mọi thay đổi
    _order = 'received_date desc, name asc'
    _rec_name = 'name'

    # =========================================================================
    # NHÓM 1: MÃ PHIẾU VÀ LIÊN KẾT BẢO HÀNH
    # =========================================================================
    name = fields.Char(
        string='Mã yêu cầu', required=True, copy=False,
        readonly=True, default='New', tracking=True,
        # [QT10] readonly=True: người dùng không nhập được.
        #        Mã CLM/xxxx sẽ được sinh tự động trong create() bên dưới.
    )
    warranty_id = fields.Many2one(
        'cmcts_warranty.warranty', string='Phiếu Bảo Hành',
        required=True, tracking=True, ondelete='cascade',
        # Many2one → liên kết tới cmcts_warranty.warranty.
        # ondelete='cascade': nếu phiếu BH bị xóa → YCBH cũng bị xóa theo.
        # [QT11] Domain trên UI lọc: state='active' VÀ claim_count=0
        #        → chỉ hiện phiếu BH còn hiệu lực và chưa có YCBH nào.
        #        (domain khai báo trong warranty_views.xml, không phải ở đây)
    )

    # =========================================================================
    # NHÓM 2: THÔNG TIN KẾ THỪA TỪ PHIẾU BH (Chỉ đọc, tự điền)
    # =========================================================================
    # related: Odoo tự lấy giá trị từ warranty_id, không cần nhập lại.
    # store=True: lưu vào DB để tìm kiếm/lọc nhanh, không cần JOIN mỗi lần.
    # readonly=True: chỉ xem, không sửa (dữ liệu gốc nằm ở bảng warranty).
    partner_id = fields.Many2one(
        related='warranty_id.partner_id', string='Khách hàng',
        store=True, readonly=True,
    )
    product_id = fields.Many2one(
        related='warranty_id.product_id', string='Sản phẩm',
        store=True, readonly=True,
    )
    product_name = fields.Char(
        related='warranty_id.product_name', string='Thiết bị',
        store=True, readonly=True,
    )
    lot_id = fields.Many2one(
        related='warranty_id.lot_id', string='Số Serial / Lô',
        store=True, readonly=True,
    )
    serial_number = fields.Char(
        related='warranty_id.serial_number', string='Số Serial',
        store=True, readonly=True,
    )
    warranty_expiry_date = fields.Date(
        related='warranty_id.expiry_date', string='Hạn BH',
        store=True, readonly=True,
        # Dùng để tính is_valid bên dưới
    )
    image = fields.Image(
        related='warranty_id.image', string='Ảnh thiết bị',
        readonly=True,
    )

    # =========================================================================
    # NHÓM 3: THÔNG TIN TIẾP NHẬN (Nhân viên tiếp nhận điền)
    # =========================================================================
    issue_description = fields.Text(
        string='Mô tả lỗi / Triệu chứng', required=True, tracking=True,
        # [QT13] Trong view: readonly="not is_receptionist"
        #        → KTV không được sửa mô tả, chỉ nhân viên tiếp nhận mới được.
    )
    received_date = fields.Date(
        string='Ngày tiếp nhận', default=fields.Date.today, required=True, tracking=True,
        # [QT13] Trong view: readonly="not is_receptionist"
    )
    expected_return_date = fields.Date(
        string='Ngày dự kiến trả', tracking=True,
        # [QT13] Trong view: readonly="not is_receptionist"
    )
    technician_id = fields.Many2one(
        'res.users', string='Kỹ thuật viên phụ trách',
        domain=lambda self: [('groups_id', 'in', self.env.ref('cmcts_warranty.group_warranty_technician').ids)],
        tracking=True,
        # [QT15] domain: chỉ user thuộc nhóm 'group_warranty_technician' (KTV) mới hiện.
        # [QT13] Trong view: readonly="not is_receptionist"
    )

    # =========================================================================
    # NHÓM 4: PHÂN QUYỀN THEO VAI TRÒ (Computed, dùng trong view)
    # =========================================================================
    is_receptionist = fields.Boolean(
        compute='_compute_is_receptionist',
        default=lambda self: self.env.user.has_group('cmcts_warranty.group_warranty_manager'),
        # [QT13] Field này được dùng trong warranty_views.xml để kiểm tra:
        #        readonly="not is_receptionist"
        #        → Nếu user là nhân viên tiếp nhận (group_warranty_manager): is_receptionist=True
        #          → các trường được sửa.
        #        → Nếu user là KTV (group_warranty_technician): is_receptionist=False
        #          → các trường bị khóa readonly, chỉ điền resolution_note + bấm nút.
    )

    @api.depends_context('uid')
    def _compute_is_receptionist(self):
        """
        [QT13] Tính is_receptionist dựa trên user đang đăng nhập.
        @api.depends_context('uid'): Odoo sẽ recompute khi user thay đổi
        (ví dụ: admin mở form → True; KTV mở cùng form → False).
        """
        is_rec = self.env.user.has_group('cmcts_warranty.group_warranty_manager')
        for record in self:
            record.is_receptionist = is_rec

    # =========================================================================
    # NHÓM 5: TRẠNG THÁI XỬ LÝ (State Machine)
    # =========================================================================
    state = fields.Selection([
        ('1_received',   'Tiếp nhận'),    # Trạng thái mặc định khi tạo mới
        ('2_processing', 'Đang xử lý'),   # Sau khi bấm "Bắt đầu xử lý"
        ('3_done',       'Hoàn thành'),   # Sau khi bấm "Hoàn thành"
        ('4_rejected',   'Từ chối'),      # Sau khi bấm "Từ chối"
    ], string='Trạng thái xử lý', default='1_received', tracking=True)
    # [QT14] Quy trình 1 chiều: write() chặn đổi ngược từ 3_done/4_rejected.
    # Tiền tố số (1_, 2_, 3_, 4_): giúp Odoo sắp xếp đúng thứ tự trên statusbar.

    resolution_note = fields.Text(
        string='Kết quả / Ghi chú xử lý', tracking=True,
        # [QT13] Field DUY NHẤT KTV được phép điền (không có readonly trong view).
    )
    color = fields.Integer(string='Mã màu', default=0)   # Kanban color picker

    # =========================================================================
    # NHÓM 6: TÍNH HỢP LỆ BẢO HÀNH
    # =========================================================================
    is_valid = fields.Boolean(
        string='BH còn hợp lệ?',
        compute='_compute_is_valid', store=True, tracking=True,
        # [QT12] Hiển thị badge 'Hợp lệ' / 'Hết hạn' trên Kanban card.
    )

    @api.depends('warranty_id', 'received_date', 'warranty_expiry_date')
    def _compute_is_valid(self):
        """
        [QT12] BH hợp lệ nếu ngày tiếp nhận ≤ ngày hết hạn BH.
        """
        for record in self:
            # Nếu có đủ cả 2 ngày: hết hạn và tiếp nhận
            if record.warranty_expiry_date and record.received_date:
                # Trả về True nếu nhận hàng trước hoặc ngay ngày hết hạn
                record.is_valid = record.received_date <= record.warranty_expiry_date
            else:
                # Nếu thiếu ngày thì coi như không hợp lệ
                record.is_valid = False

    # =========================================================================
    # NHÓM 7: CREATE — Sinh mã tự động
    # =========================================================================

    @api.model_create_multi
    def create(self, vals_list):
        """
        [QT10] Sinh mã YCBH tự động (CLM/0001, CLM/0002...).
        Nếu vals['name'] == 'New' (default) → lấy sequence tiếp theo.
        Sequence khai báo trong data/warranty_sequence.xml.
        """
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('cmcts_warranty.warranty.claim') or 'New'
        return super().create(vals_list)

    @api.constrains('warranty_id')
    def _check_one_claim_per_warranty(self):
        """
        [QT11] Mỗi Phiếu Bảo Hành chỉ được có đúng 1 Phiếu YCBH (bất kể trạng thái).
        Logic: tìm YCBH khác cùng warranty_id (loại trừ bản thân) → nếu có → báo lỗi.
        """
        for record in self:
            # Đếm trong Database (search_count) xem có bản ghi nào trùng warranty_id không
            count = self.search_count([
                ('warranty_id', '=', record.warranty_id.id),
                ('id', '!=', record.id), # ID phải khác bản ghi hiện tại đang xử lý
            ])
            # Nếu count > 0 nghĩa là đã có phiếu khác xí chỗ rồi
            if count > 0:
                # Ném lỗi chặn không cho lưu vào DB
                raise ValidationError(
                    f"Phiếu Bảo Hành '{record.warranty_id.name}' đã có phiếu yêu cầu bảo hành. "
                    "Mỗi phiếu BH chỉ được phép tạo 1 phiếu YCBH duy nhất."
                )

    # =========================================================================
    # NHÓM 8: ACTIONS — Nút bấm chuyển trạng thái
    # =========================================================================

    def action_process(self):
        """
        [QT14] Chuyển: Tiếp nhận → Đang xử lý.
        Chỉ được bấm khi state == '1_received' (invisible trong view).
        """
        for record in self:
            if record.state == '1_received':
                record.state = '2_processing'

    def action_done(self):
        """
        [QT14] Chuyển: Đang xử lý → Hoàn thành.
        Trả về hiệu ứng Rainbow Man để UI hiển thị animation ăn mừng.
        """
        for record in self:
            # Gán trạng thái thành Hoàn thành
            record.state = '3_done'
            
        # Odoo hỗ trợ trả về 1 object dictionary dạng 'effect' để tạo animation trên màn hình
        return {
            'effect': {
                'fadeout': 'slow',
                'message': '🎉 Xử lý bảo hành thành công! Khách hàng hài lòng!',
                'img_url': '/web/static/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def action_reject(self):
        """
        [QT14] Chuyển: Tiếp nhận hoặc Đang xử lý → Từ chối.
        Lý do từ chối: BH hết hạn, lỗi người dùng gây ra, không đủ điều kiện...
        Trả về hiệu ứng Rainbow Man với icon mặt trung tính.
        """
        for record in self:
            record.state = '4_rejected'
        return {
            'effect': {
                'fadeout': 'slow',
                'message': '❌ Yêu cầu bảo hành đã bị từ chối.',
                'img_url': '/web/static/img/neutral_face.svg',
                'type': 'rainbow_man',
            }
        }

    # =========================================================================
    # NHÓM 9: WRITE — Chặn đảo ngược trạng thái
    # =========================================================================

    def write(self, vals):
        """
        [QT14] Quy trình 1 chiều — Chặn đổi state ngược chiều:
        Một khi YCBH đã ở 'Hoàn thành' (3_done) hoặc 'Từ chối' (4_rejected),
        không thể kéo ngược về bất kỳ trạng thái nào trước đó.

        Tại sao? Để bảo vệ tính toàn vẹn của lịch sử xử lý.
        Ví dụ: không thể giả vờ phiếu đã hoàn thành rồi kéo lại để xử lý lần 2.
        """
        if 'state' in vals:
            for record in self:
                old_state = record.state
                new_state = vals['state']
                # Nếu đang là trạng thái cuối (3_done / 4_rejected)
                # mà cố đổi về trạng thái khác không phải cuối → chặn
                if old_state in ['3_done', '4_rejected'] and new_state not in ['3_done', '4_rejected']:
                    raise ValidationError(
                        "Không thể chuyển trạng thái ngược sau khi đã "
                        "Hoàn thành hoặc Từ chối yêu cầu bảo hành."
                    )
        return super().write(vals)
