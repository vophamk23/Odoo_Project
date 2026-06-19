# -*- coding: utf-8 -*-
"""
File: tests/test_warranty_security.py
Chức năng: Security/Permission tests cho module Bảo Hành.
[Cập nhật Phase 1 Link]: Dùng product_id + lot_id thay vì product_name (Char).
"""
from odoo.tests.common import TransactionCase
from odoo.exceptions import AccessError, ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta


class TestWarrantySecurity(TransactionCase):

    def setUp(self):
        super().setUp()

        # User KHÔNG CÓ QUYỀN vào app Bảo Hành
        self.user_no_access = self.env['res.users'].create({
            'name': 'User No Access',
            'login': 'no_access_warranty_1',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

        # Receptionist (Nhân viên tiếp nhận) - Toàn quyền Tạo/Sửa/Xóa
        self.user_receptionist = self.env['res.users'].create({
            'name': 'Receptionist User',
            'login': 'receptionist_warranty_1',
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('cmcts_warranty.group_warranty_manager').id,
            ])],
        })

        # Technician (Kỹ thuật viên) - Chỉ đọc trên Warranty, có quyền Sửa trên Claim được giao
        self.user_technician = self.env['res.users'].create({
            'name': 'Technician User',
            'login': 'technician_warranty_1',
            'groups_id': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('cmcts_warranty.group_warranty_technician').id,
            ])],
        })

        # Tạo Khách hàng mẫu
        self.partner = self.env['res.partner'].create({
            'name': 'KH Security Test',
        })

        # Tạo product + lot demo dùng chung
        self.categ = self.env['product.category'].create({'name': 'Test Category Security'})
        self.product_tmpl = self.env['product.template'].create({
            'name': 'Laptop Test Security',
            'type': 'consu',
            'categ_id': self.categ.id,
            'tracking': 'serial',
        })
        self.product = self.product_tmpl.product_variant_ids[0]
        self.lot = self.env['stock.lot'].create({
            'name': 'SN-SEC-001',
            'product_id': self.product.id,
            'company_id': self.env.company.id,
        })

        # Các giá trị mặc định để tạo Warranty mẫu
        self.warranty_vals = {
            'product_id': self.product.id,
            'lot_id': self.lot.id,
            'partner_id': self.partner.id,
            'sale_date': date.today() - relativedelta(months=1),
            'warranty_months': 12,
        }

    def _make_lot(self, serial_name):
        """Helper: tạo stock.lot mới với serial_name cho self.product."""
        return self.env['stock.lot'].create({
            'name': serial_name,
            'product_id': self.product.id,
            'company_id': self.env.company.id,
        })

    def test_01_no_access_cannot_read(self):
        """Test: User không có quyền sẽ KHÔNG THỂ XEM phiếu bảo hành"""
        warranty = self.env['cmcts_warranty.warranty'].create(self.warranty_vals)
        with self.assertRaises(AccessError):
            _ = self.env['cmcts_warranty.warranty'].with_user(self.user_no_access).browse(warranty.id).product_name

    def test_02_no_access_cannot_create(self):
        """Test: User không có quyền sẽ KHÔNG THỂ TẠO phiếu bảo hành"""
        new_lot = self._make_lot('SN-NO-ACCESS')
        with self.assertRaises(AccessError):
            self.env['cmcts_warranty.warranty'].with_user(self.user_no_access).create({
                'product_id': self.product.id,
                'lot_id': new_lot.id,
                'partner_id': self.partner.id,
                'sale_date': date.today() - relativedelta(months=1),
                'warranty_months': 12,
            })

    def test_03_technician_can_read_assigned(self):
        """Test: KTV CÓ THỂ XEM phiếu bảo hành nếu Claim đó được giao cho mình"""
        warranty = self.env['cmcts_warranty.warranty'].create(self.warranty_vals)
        self.env['cmcts_warranty.warranty.claim'].create({
            'warranty_id': warranty.id,
            'issue_description': 'Màn hình lỗi.',
            'received_date': date.today(),
            'technician_id': self.user_technician.id,
        })
        record = self.env['cmcts_warranty.warranty'].with_user(self.user_technician).browse(warranty.id)
        self.assertEqual(record.product_name, 'Laptop Test Security')

    def test_03b_technician_cannot_read_unassigned(self):
        """Test: KTV KHÔNG THỂ XEM phiếu bảo hành nếu Claim đó KHÔNG giao cho mình"""
        warranty = self.env['cmcts_warranty.warranty'].create(self.warranty_vals)
        # Tạo claim không gán cho KTV nào hoặc gán cho KTV khác
        self.env['cmcts_warranty.warranty.claim'].create({
            'warranty_id': warranty.id,
            'issue_description': 'Màn hình lỗi.',
            'received_date': date.today(),
        })
        with self.assertRaises(AccessError):
            _ = self.env['cmcts_warranty.warranty'].with_user(self.user_technician).browse(warranty.id).product_name

    def test_04_technician_cannot_create_warranty(self):
        """Test: KTV chỉ có quyền xem Phiếu bảo hành (KHÔNG THỂ TẠO MỚI)"""
        new_lot = self._make_lot('SN-TECH-CREATE')
        with self.assertRaises(AccessError):
            self.env['cmcts_warranty.warranty'].with_user(self.user_technician).create({
                'product_id': self.product.id,
                'lot_id': new_lot.id,
                'partner_id': self.partner.id,
                'sale_date': date.today() - relativedelta(months=1),
                'warranty_months': 6,
            })

    def test_05_technician_cannot_write_warranty(self):
        """Test: KTV chỉ có quyền xem Phiếu bảo hành (KHÔNG THỂ SỬA)"""
        warranty = self.env['cmcts_warranty.warranty'].create(self.warranty_vals)
        with self.assertRaises(AccessError):
            warranty.with_user(self.user_technician).write({'note': 'Hacked'})

    def test_06_technician_cannot_delete_warranty(self):
        """Test: KTV chỉ có quyền xem Phiếu bảo hành (KHÔNG THỂ XÓA)"""
        warranty = self.env['cmcts_warranty.warranty'].create(self.warranty_vals)
        with self.assertRaises(AccessError):
            warranty.with_user(self.user_technician).unlink()

    def test_07_receptionist_can_see_others_record(self):
        """Test: Tiếp nhận có thể xem tất cả Phiếu bảo hành của người khác"""
        new_lot = self._make_lot('SN-SEC-002')
        other_warranty = self.env['cmcts_warranty.warranty'].create({
            **self.warranty_vals,
            'lot_id': new_lot.id,
        })
        # Nhân viên tiếp nhận có thể xem phiếu bảo hành do người khác tạo
        record = self.env['cmcts_warranty.warranty'].with_user(self.user_receptionist).browse(other_warranty.id)
        self.assertEqual(record.product_name, 'Laptop Test Security')

    def test_08_receptionist_can_create(self):
        """Test: Tiếp nhận CÓ THỂ TẠO Phiếu bảo hành"""
        new_lot = self._make_lot('SN-REC-001')
        warranty = self.env['cmcts_warranty.warranty'].with_user(self.user_receptionist).create({
            'product_id': self.product.id,
            'lot_id': new_lot.id,
            'partner_id': self.partner.id,
            'sale_date': date.today() - relativedelta(months=2),
            'warranty_months': 24,
        })
        self.assertTrue(warranty.id)

    def test_09_receptionist_can_write(self):
        """Test: Tiếp nhận CÓ THỂ SỬA Phiếu bảo hành (kể cả ghi chú nội bộ)"""
        warranty = self.env['cmcts_warranty.warranty'].create(self.warranty_vals)
        warranty.with_user(self.user_receptionist).write({
            'internal_note': 'Ghi chú nội bộ do Tiếp nhận chỉnh sửa',
        })
        self.assertEqual(warranty.internal_note, 'Ghi chú nội bộ do Tiếp nhận chỉnh sửa')

    def test_10_receptionist_can_delete(self):
        """Test: Tiếp nhận CÓ THỂ XÓA Phiếu bảo hành"""
        new_lot = self._make_lot('SN-DEL-001')
        warranty = self.env['cmcts_warranty.warranty'].create({
            **self.warranty_vals,
            'lot_id': new_lot.id,
        })
        warranty_id = warranty.id
        warranty.with_user(self.user_receptionist).unlink()
        result = self.env['cmcts_warranty.warranty'].search([('id', '=', warranty_id)])
        self.assertEqual(len(result), 0)

    def test_11_technician_can_write_claim(self):
        """Test: KTV có quyền SỬA các Claim được giao cho mình"""
        warranty = self.env['cmcts_warranty.warranty'].create(self.warranty_vals)
        claim = self.env['cmcts_warranty.warranty.claim'].create({
            'warranty_id': warranty.id,
            'issue_description': 'Màn hình lỗi.',
            'received_date': date.today(),
            'technician_id': self.user_technician.id,
        })
        # Kỹ thuật viên cập nhật trạng thái
        claim.with_user(self.user_technician).write({
            'state': '2_processing',
            'resolution_note': 'Đang tiến hành thay thế màn hình.',
        })
        self.assertEqual(claim.state, '2_processing')

    def test_11b_technician_cannot_write_unassigned_claim(self):
        """Test: KTV KHÔNG ĐƯỢC SỬA các Claim KHÔNG giao cho mình"""
        warranty = self.env['cmcts_warranty.warranty'].create(self.warranty_vals)
        claim = self.env['cmcts_warranty.warranty.claim'].create({
            'warranty_id': warranty.id,
            'issue_description': 'Màn hình lỗi.',
            'received_date': date.today(),
        })
        with self.assertRaises(AccessError):
            claim.with_user(self.user_technician).write({
                'resolution_note': 'Hacked',
            })

    def test_12_duplicate_serial_validation(self):
        """Test: Validation CHẶN tạo trùng số Serial (lot_id)"""
        self.env['cmcts_warranty.warranty'].create(self.warranty_vals)
        with self.assertRaises(ValidationError):
            self.env['cmcts_warranty.warranty'].create({
                **self.warranty_vals,
                # Cùng lot_id → phải bị chặn
            })

    def test_13_claim_state_no_rollback(self):
        """Test: Validation CHẶN lùi trạng thái từ Hoàn tất về Tiếp nhận"""
        warranty = self.env['cmcts_warranty.warranty'].create(self.warranty_vals)
        claim = self.env['cmcts_warranty.warranty.claim'].create({
            'warranty_id': warranty.id,
            'issue_description': 'Test rollback.',
            'received_date': date.today(),
            'state': '3_done',
        })
        with self.assertRaises(ValidationError):
            claim.write({'state': '1_received'})

    def test_14_technician_domain_restriction(self):
        """Test: Cột technician_id chỉ được phép chọn những User có quyền KTV"""
        field = self.env['cmcts_warranty.warranty.claim']._fields['technician_id']
        domain = field.domain
        if callable(domain):
            domain = domain(self.env['cmcts_warranty.warranty.claim'])

        # Tìm kiếm các user khớp với điều kiện domain
        allowed_users = self.env['res.users'].search(domain)

        # Kỹ thuật viên phải có mặt trong danh sách hợp lệ
        self.assertIn(self.user_technician.id, allowed_users.ids)
        # Nhân viên tiếp nhận cũng kế thừa quyền của KTV nên họ CŨNG CÓ MẶT trong danh sách
        self.assertIn(self.user_receptionist.id, allowed_users.ids)
