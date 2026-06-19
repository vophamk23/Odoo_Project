# -*- coding: utf-8 -*-
"""
=============================================================================
File: models/warranty.py
Model: cmcts_warranty.warranty  →  Bảng DB: cmcts_warranty_warranty
=============================================================================
MỤC ĐÍCH:
  Lưu trữ Phiếu Bảo Hành (PBH) cho từng thiết bị đã bán.
  Mỗi record = 1 phiếu bảo hành gắn với 1 thiết bị + 1 khách hàng.

LUẬT NGHIỆP VỤ ĐƯỢC HIỆN THỰC TRONG FILE NÀY:
  [QT1] Mã phiếu tự động:  WH/0001, WH/0002, ... (không cho nhập tay)
  [QT2] Ngày hết hạn tự tính: expiry_date = sale_date + warranty_months
  [QT3] Tự động hết hạn:  Nếu expiry_date < hôm nay → state = 'expired' ngay lúc tạo
  [QT4] Cron hàng đêm:    Quét & cập nhật những phiếu lỡ bị sót (phiếu cũ)
  [QT5] Không hồi sinh:   Phiếu đã 'cancelled' không thể đổi state khác
  [QT6] Serial duy nhất:  Mỗi số serial chỉ xuất hiện 1 lần trong hệ thống
  [QT6b] Serial lọc động: Dropdown serial chỉ hiển thị:
         • Serial của product được chọn
         • Chưa được dùng ở warranty active/expired
         • Nếu warranty bị cancelled → serial có thể tái sử dụng
  [QT7] Tháng hợp lệ:     warranty_months phải từ 1 đến 120
  [QT8] Ngày mua hợp lệ:  sale_date không được là ngày tương lai
  [QT9] Theo dõi claim:   Đếm số YCBH + biết có YCBH đang mở không

QUAN HỆ:
  → cmcts_warranty.warranty.claim (One2many, warranty_id)
=============================================================================
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging
import json

_logger = logging.getLogger(__name__)


class Warranty(models.Model):
    _name = "cmcts_warranty.warranty"
    _description = "Phiếu Bảo Hành Thiết Bị"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Chatter: tự log mọi thay đổi
    _order = "expiry_date asc, name asc"
    _rec_name = "name"

    # =========================================================================
    # NHÓM 1: THÔNG TIN NHẬN DẠNG THIẾT BỊ
    # =========================================================================
    name = fields.Char(
        string="Mã phiếu BH",
        required=True,
        copy=False,
        readonly=True,
        default="New",
        tracking=True,
        # [QT1] readonly=True + default='New': người dùng không nhập được.
        #       Odoo sẽ tự sinh mã WH/0001 khi gọi create() bên dưới.
    )
    product_id = fields.Many2one(
        "product.product",
        string="Sản phẩm / Thiết bị",
        required=True,
        tracking=True,
        # Liên kết tới bảng product.product (Module Product chuẩn Odoo).
        # Tên thiết bị, loại thiết bị đều lấy từ đây.
    )
    lot_id = fields.Many2one(
        "stock.lot",
        string="Số Serial / Lô",
        required=True,
        tracking=True,
        # [QT6] Liên kết tới stock.lot (Module Stock chuẩn Odoo).
        # Domain lọc theo product_id để chỉ hiện Serial của đúng sản phẩm đó.
    )
    # Computed: tên sản phẩm (lấy từ product_id, dùng cho related field ở claim)
    product_name = fields.Char(
        string="Tên thiết bị",
        related="product_id.name",
        store=True,
        readonly=True,
    )
    # Computed: serial number text (lấy từ lot_id, dùng cho related field ở claim)
    serial_number = fields.Char(
        string="Số Serial",
        related="lot_id.name",
        store=True,
        readonly=True,
    )
    # Computed: nhóm sản phẩm (Laptop, Server...) lấy từ product_id.categ_id
    product_category_id = fields.Many2one(
        "product.category",
        string="Nhóm sản phẩm",
        related="product_id.categ_id",
        store=True,
        readonly=True,
    )
    image = fields.Image(
        string="Ảnh thiết bị", 
        max_width=256, 
        max_height=256,
        compute="_compute_image",
        store=True,
        readonly=False
    )

    product_id_domain = fields.Char(compute="_compute_product_id_domain", store=False)
    lot_id_domain = fields.Char(compute="_compute_lot_id_domain", store=False)

    # =========================================================================
    # NHÓM 2: KHÁCH HÀNG & ĐƠN HÀNG
    # =========================================================================
    partner_id = fields.Many2one(
        "res.partner", string="Khách hàng", required=True, tracking=True
    )
    sale_order_id = fields.Many2one(
        "sale.order",
        string="Đơn hàng gốc",
        help="Chọn đơn hàng mà sản phẩm này được bán. Tự động điền ngày mua từ đây. (Domain lọc trong view)",
        tracking=True,
    )

    # =========================================================================
    # NHÓM 3: THỜI GIAN BẢO HÀNH
    # =========================================================================
    sale_date = fields.Date(
        string="Ngày mua",
        required=True,
        tracking=True,
        # [QT8] Không được là ngày tương lai: kiểm tra tại _check_sale_date()
    )
    warranty_months = fields.Integer(
        string="Thời gian BH (tháng)",
        default=12,
        required=True,
        tracking=True,
        # [QT7] Phải từ 1 đến 120: kiểm tra tại _check_warranty_months()
    )
    expiry_date = fields.Date(
        string="Ngày hết hạn BH",
        compute="_compute_expiry_date",
        store=True,
        tracking=True,
        # [QT2] Tự tính: _compute_expiry_date() chạy khi sale_date/warranty_months thay đổi.
        #       store=True: ghi vào DB để tìm kiếm / cron quét được.
    )

    # =========================================================================
    # NHÓM 4: TRẠNG THÁI & GIAO DIỆN
    # =========================================================================
    state = fields.Selection(
        [
            ("active", "Còn hiệu lực"),
            ("expired", "Hết thời hạn bảo hành"),
            ("cancelled", "Đã hủy"),
        ],
        string="Trạng thái BH",
        default="active",
        tracking=True,
    )
    # [QT3] state tự chuyển sang 'expired' ngay trong create() nếu expiry < hôm nay.
    # [QT4] Cron hàng đêm quét & gán 'expired' cho những phiếu bị sót (phiếu cũ).
    # [QT5] Một khi = 'cancelled' → write() chặn mọi đổi ngược.

    color = fields.Integer(string="Mã màu", default=0)  # Dùng cho Kanban color picker
    active = fields.Boolean(string="Active", default=True)
    note = fields.Text(string="Ghi chú", tracking=True)
    internal_note = fields.Text(string="Ghi chú nội bộ", tracking=True)

    # =========================================================================
    # NHÓM 5: QUAN HỆ VỚI PHIẾU YÊU CẦU BẢO HÀNH
    # =========================================================================
    claim_ids = fields.One2many(
        "cmcts_warranty.warranty.claim",
        "warranty_id",
        string="Danh sách yêu cầu BH",
        # One2many: 1 phiếu BH có thể liên kết nhiều YCBH (nhưng luật chỉ cho 1)
    )
    claim_count = fields.Integer(
        string="Số lần yêu cầu",
        compute="_compute_claim_count",
        store=True,
        # [QT9a] Đếm tổng số YCBH. store=True để dùng trong domain view.
        # Dùng trong domain: ('claim_count', '=', 0) → ẩn BH đã có YCBH khỏi dropdown.
    )
    has_open_claim = fields.Boolean(
        string="Đang có yêu cầu BH?",
        compute="_compute_has_open_claim",
        store=True,
        # [QT9b] True nếu có YCBH đang xử lý (Tiếp nhận / Đang xử lý).
        # Có thể dùng để hiển thị cảnh báo trên UI.
    )

    # =========================================================================
    # NHÓM 6: COMPUTED FIELDS
    # =========================================================================

    @api.depends("sale_date", "warranty_months")
    def _compute_expiry_date(self):
        """
        [QT2] Tính ngày hết hạn = ngày mua + số tháng bảo hành.
        Dùng relativedelta để tính đúng tháng (không phải 30 ngày cố định).
        Ví dụ: mua 31/01/2024, BH 1 tháng → hết hạn 28/02/2024 (không phải 02/03).
        """
        for record in self:
            if record.sale_date and record.warranty_months > 0:
                record.expiry_date = record.sale_date + relativedelta(
                    months=record.warranty_months
                )
            else:
                record.expiry_date = False

    @api.depends("product_id.image_1920")
    def _compute_image(self):
        """Tự động lấy ảnh từ danh mục sản phẩm nếu phiếu chưa có ảnh."""
        for record in self:
            # Chỉ điền tự động nếu ảnh đang trống
            if record.product_id and not record.image:
                record.image = record.product_id.image_1920

    @api.depends("claim_ids")
    def _compute_claim_count(self):
        """[QT9a] Đếm tổng số YCBH đã tạo cho phiếu BH này."""
        for record in self:
            record.claim_count = len(record.claim_ids)

    @api.depends("claim_ids.state")
    def _compute_has_open_claim(self):
        """
        [QT9b] True nếu có ít nhất 1 YCBH đang mở.
        'Đang mở' = state là '1_received' (Tiếp nhận) hoặc '2_processing' (Đang xử lý).
        """
        for record in self:
            record.has_open_claim = any(
                c.state in ("1_received", "2_processing") for c in record.claim_ids
            )

    @api.depends("sale_order_id")
    def _compute_product_id_domain(self):
        """
        Tính toán bộ lọc (domain) động cho trường product_id trên giao diện,
        để chỉ hiển thị những sản phẩm có nằm trong đơn hàng đã chọn.
        """
        # Vòng lặp for bắt buộc trong Odoo khi dùng compute field để xử lý nhiều record cùng lúc
        for record in self:
            if record.sale_order_id:
                # Tìm tất cả các dòng chi tiết đơn hàng, loại bỏ các sản phẩm là 'Dịch vụ' (service)
                sale_lines = record.sale_order_id.order_line.filtered(
                    lambda l: l.product_id.type != "service"
                )
                # Lấy danh sách ID của các sản phẩm đó
                ids = sale_lines.mapped("product_id").ids
                # Trả về chuỗi JSON chứa domain để giao diện Odoo đọc được
                record.product_id_domain = json.dumps([("id", "in", ids)])
            else:
                # Nếu chưa chọn đơn hàng, trả về rỗng (tức là hiện tất cả sản phẩm)
                record.product_id_domain = json.dumps([])

    @api.depends("product_id", "sale_order_id")
    def _compute_lot_id_domain(self):
        """
        Tính toán bộ lọc (domain) động cho trường Số Serial (lot_id).
        Chỉ hiển thị Serial của đúng sản phẩm đó, và loại bỏ các Serial đã được bảo hành.
        """
        for record in self:
            # Nếu chưa chọn sản phẩm, khóa trường Serial lại (domain = ID False)
            if not record.product_id:
                record.lot_id_domain = json.dumps([("id", "=", False)])
                continue

            # Tìm kiếm trong DB các phiếu bảo hành khác đang xài chung sản phẩm này
            used = self.env["cmcts_warranty.warranty"].search(
                [
                    ("product_id", "=", record.product_id.id),
                    ("state", "in", ["active", "expired"]), # Chỉ tính phiếu còn sống hoặc hết hạn
                    ("id", "!=", record.id), # Bỏ qua chính record hiện tại
                ]
            )
            
            # Xây dựng điều kiện lọc cơ bản: đúng sản phẩm, và không nằm trong danh sách đã bị dùng
            domain = [
                ("product_id", "=", record.product_id.id),
                ("id", "not in", used.mapped("lot_id").ids),
            ]
            
            # Nếu có đơn hàng, chỉ hiện Serial của những thiết bị đã thực sự giao cho khách
            if record.sale_order_id:
                move_lines = self.env["stock.move.line"].search(
                    [
                        ("product_id", "=", record.product_id.id),
                        ("move_id.sale_line_id.order_id", "=", record.sale_order_id.id),
                        ("state", "=", "done"), # Hàng đã giao (done)
                        ("lot_id", "!=", False), # Có đánh số Serial
                    ]
                )
                # Thêm điều kiện: Serial phải nằm trong danh sách hàng đã giao
                domain.append(("id", "in", move_lines.mapped("lot_id").ids))

            # Chuyển đổi mảng domain thành JSON để đẩy ra UI
            record.lot_id_domain = json.dumps(domain)

    # =========================================================================
    # NHÓM 7: ONCHANGE — Điền tự động từ đơn hàng
    # =========================================================================

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        """
        Khi chọn khách hàng → domain sẽ lọc danh sách đơn hàng
        (không cần clear sale_order_id, Odoo sẽ tự handle).
        """
        # Odoo tự động apply domain, không cần code thêm
        pass

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """
        Khi chọn sản phẩm → filter lot_id qua _get_lot_domain():
        [QT6b] loại trừ serial đã dùng ở warranty active/expired khác.
        Nếu đang có sale_order_id → chỉ hiện serial thực sự nằm trong
        đơn hàng đó (đã giao) cho đúng sản phẩm này.
        """
        self.lot_id = False
        if self.product_id:
            result = self._get_lot_domain()
            if self.sale_order_id:
                sale_lines = self.sale_order_id.order_line.filtered(
                    lambda l: l.product_id.type != "service"
                )
                unique_products = sale_lines.mapped("product_id")
                result["domain"]["product_id"] = [("id", "in", unique_products.ids)]
                return result
        else:
            domain = {"lot_id": [("id", "=", False)]}
            if self.sale_order_id:
                sale_lines = self.sale_order_id.order_line.filtered(
                    lambda l: l.product_id.type != "service"
                )
                unique_products = sale_lines.mapped("product_id")
                domain["product_id"] = [("id", "in", unique_products.ids)]
            return {"domain": domain}

    @api.onchange("sale_order_id")
    def _onchange_sale_order_id(self):
        """
        Khi chọn đơn hàng:
        - Tự điền ngày mua từ date_order.
        - Giới hạn dropdown product_id: chỉ hiện sản phẩm (non-service) có trong đơn này.
        - Nếu đơn chỉ có 1 sản phẩm → auto-select, đồng thời filter lot_id theo
          serial đã giao trong đơn đó (qua _get_lot_domain).
        - Nếu đơn có nhiều sản phẩm → để trống, chờ user chọn trong domain đã lọc.
        """
        if self.sale_order_id:
            self.sale_date = (
                self.sale_order_id.date_order.date()
                if self.sale_order_id.date_order
                else fields.Date.today()
            )

            sale_lines = self.sale_order_id.order_line.filtered(
                lambda l: l.product_id.type != "service"
            )
            unique_products = sale_lines.mapped("product_id")

            self.lot_id = False

            if len(unique_products) == 1:
                self.product_id = unique_products[0]
                return self._get_lot_domain()
            else:
                self.product_id = False
                return {
                    "domain": {
                        "product_id": [("id", "in", unique_products.ids)],
                        "lot_id": [("id", "=", False)],
                    }
                }
        else:
            self.product_id = False
            self.lot_id = False
            return {"domain": {"product_id": [], "lot_id": [("id", "=", False)]}}

    def _get_lot_domain(self):
        """
        Domain dùng chung cho lot_id, áp 2 lớp lọc:
        1) [QT6b] Loại trừ serial đã gắn warranty active/expired (record khác).
        2) Nếu có sale_order_id: chỉ giữ serial nằm trong stock.move.line đã
           giao (state='done') gắn với sale_line_id thuộc đơn hàng này, đúng
           product_id đang chọn. Nếu không có sale_order_id (tạo tay, không
           qua đơn hàng) → bỏ qua điều kiện này.
        """
        if not self.product_id:
            return {"domain": {"lot_id": [("id", "=", False)]}}

        used_warranties = self.env["cmcts_warranty.warranty"].search(
            [
                ("product_id", "=", self.product_id.id),
                ("state", "in", ["active", "expired"]),
            ]
        )
        domain = [
            ("product_id", "=", self.product_id.id),
            ("id", "not in", used_warranties.mapped("lot_id").ids),
        ]

        if self.sale_order_id:
            move_lines = self.env["stock.move.line"].search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("move_id.sale_line_id.order_id", "=", self.sale_order_id.id),
                    ("state", "=", "done"),
                    ("lot_id", "!=", False),
                ]
            )
            domain.append(("id", "in", move_lines.mapped("lot_id").ids))

        return {"domain": {"lot_id": domain}}

    # =========================================================================
    # NHÓM 8: CREATE — Sinh mã tự động + auto-expire khi tạo mới
    # =========================================================================

    @api.model_create_multi
    def create(self, vals_list):
        """
        Ghi đè create() để xử lý 2 luật:

        [QT1] Sinh mã phiếu WH/xxxx tự động:
              Nếu vals['name'] == 'New' (default) → lấy sequence tiếp theo.

        [QT3] Tự động set state='expired' nếu phiếu tạo với ngày mua quá cũ:
              - Tính expiry INLINE trong vals (trước khi INSERT vào DB).
              - Lý do tính inline: computed field 'expiry_date' chưa được flush
                vào bộ nhớ tại thời điểm này → không thể đọc record.expiry_date.
              - Nếu tính xong thấy expiry < hôm nay → đặt vals['state']='expired'
                để INSERT 1 lần với đúng state, không cần UPDATE thêm.
        """
        today = fields.Date.today()
        for vals in vals_list:
            # [QT1] Sinh mã tự động
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("cmcts_warranty.warranty") or "New"
                )

            # [QT3] Tự động hết hạn ngay khi tạo
            sale_date = vals.get("sale_date")
            warranty_months = vals.get("warranty_months", 12)
            if sale_date and warranty_months:
                if isinstance(sale_date, str):
                    # UI gửi chuỗi 'YYYY-MM-DD' → chuyển thành date object
                    sale_date = fields.Date.from_string(sale_date)
                expiry = sale_date + relativedelta(months=int(warranty_months))
                if expiry < today and vals.get("state", "active") == "active":
                    vals["state"] = "expired"  # Ghi thẳng → 1 INSERT duy nhất

        return super().create(vals_list)

    # =========================================================================
    # NHÓM 9: CRON JOB — Quét hàng đêm
    # =========================================================================

    @api.model
    def _cron_update_expired_warranties(self):
        """
        [QT4] Cron chạy hàng đêm (khai báo trong data/warranty_cron.xml).
        Mục đích: tự động rà soát DB và cập nhật state thành 'expired' nếu quá hạn.
        """
        # Lấy ngày hiện tại
        today = fields.Date.today()
        # Tìm tất cả các phiếu đang 'active' nhưng ngày hết hạn lại nhỏ hơn hôm nay
        expired_warranties = self.search(
            [
                ("state", "=", "active"),
                ("expiry_date", "<", today),
            ]
        )
        # Nếu tìm thấy, thực hiện ghi hàng loạt (write) để đổi trạng thái thành 'expired'
        if expired_warranties:
            expired_warranties.write({"state": "expired"})

    # =========================================================================
    # NHÓM 10: ACTIONS — Nút bấm trên form
    # =========================================================================

    def action_cancel(self):
        """Hủy phiếu bảo hành. Không thể hoàn tác (xem [QT5] trong write())."""
        for record in self:
            if record.state != "cancelled":
                record.state = "cancelled"

    def action_view_claims(self):
        """Smart button: mở danh sách YCBH liên quan tới phiếu BH này."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Yêu cầu BH - {self.name}",
            "res_model": "cmcts_warranty.warranty.claim",
            "view_mode": "list,form,kanban",
            "domain": [("warranty_id", "=", self.id)],
            "context": {"default_warranty_id": self.id},
        }

    # =========================================================================
    # NHÓM 11: VALIDATION — Ràng buộc dữ liệu
    # =========================================================================

    @api.constrains("lot_id")
    def _check_serial_number(self):
        """
        [QT6] Tầng ORM: Mỗi Số Serial (stock.lot) chỉ được xuất hiện 1 lần trong hệ thống bảo hành
              (constrains chạy sau mỗi create/write → chặn việc tạo duplicate).

        [QT6b] Tầng UI: Dropdown serial sẽ tự filter (onchange) để ẩn serial đang active/expired
               → user không thể chọn bằng tay. constrains này chỉ là lớp bảo vệ thêm.
        """
        for record in self:
            if record.lot_id:
                domain = [("lot_id", "=", record.lot_id.id), ("id", "!=", record.id)]
                if self.search_count(domain) > 0:
                    raise ValidationError(
                        f"Số Serial '{record.lot_id.name}' đã có phiếu bảo hành. "
                        "Mỗi số serial chỉ được tạo 1 phiếu bảo hành."
                    )

    @api.constrains("warranty_months")
    def _check_warranty_months(self):
        """[QT7] Thời gian bảo hành phải từ 1 đến 120 tháng (10 năm)."""
        for record in self:
            if record.warranty_months <= 0:
                raise ValidationError("Thời gian bảo hành phải lớn hơn 0 tháng.")
            if record.warranty_months > 120:
                raise ValidationError(
                    "Thời gian bảo hành tối đa là 120 tháng (10 năm)."
                )

    @api.constrains("sale_date")
    def _check_sale_date(self):
        """[QT8] Ngày mua không được là ngày trong tương lai."""
        today = fields.Date.today()
        for record in self:
            if record.sale_date and record.sale_date > today:
                raise ValidationError("Ngày mua không được là ngày trong tương lai.")

    def write(self, vals):
        """
        Ghi đè write() để xử lý 2 luật:

        [QT5] Chặn hồi sinh phiếu đã hủy:
              Nếu record đang 'cancelled' mà ai đó cố set state khác → chặn.

        [QT3b] Tự động hết hạn khi chỉnh sửa ngày mua / số tháng:
              Nếu sale_date hoặc warranty_months thay đổi → computed field expiry_date
              sẽ được tính lại → kiểm tra lại xem có phiếu nào vừa hết hạn không.
              Dùng context 'skip_expiry_check=True' để tránh đệ quy vô hạn
              (write() gọi write() → gọi lại write()...).
        """
        # [QT5] Chặn hồi sinh
        if "state" in vals:
            for record in self:
                if record.state == "cancelled" and vals["state"] != "cancelled":
                    raise ValidationError(
                        "Không thể kích hoạt lại phiếu bảo hành đã bị hủy."
                    )

        res = super().write(vals)

        # [QT3b] Auto-expire sau khi cập nhật ngày/tháng
        if not self.env.context.get("skip_expiry_check") and (
            "sale_date" in vals or "warranty_months" in vals
        ):
            today = fields.Date.today()
            to_expire = self.filtered(
                lambda r: r.state == "active"
                and r.expiry_date
                and r.expiry_date < today
            )
            if to_expire:
                # with_context(skip_expiry_check=True): báo cho lần write() tiếp theo
                # biết đây là lần gọi nội bộ → không kiểm tra lại nữa
                to_expire.with_context(skip_expiry_check=True).write(
                    {"state": "expired"}
                )

        return res
