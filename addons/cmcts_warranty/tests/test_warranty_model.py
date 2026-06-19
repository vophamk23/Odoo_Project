# -*- coding: utf-8 -*-
"""
File: tests/test_warranty_model.py
Chức năng: Unit Test cho Model Phiếu Bảo Hành (cmcts_warranty.warranty).
Kiểm tra CRUD, computed fields (ngày hết hạn), validation, state machine.
Yêu cầu Phase 2 - Mục 4: Viết test case và xác nhận hoàn tất module.

[Cập nhật Phase 1 Link]: Sau khi liên kết product.product + stock.lot,
các test case dùng product_id và lot_id thay vì product_name (Char).
"""
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta


class TestWarrantyModel(TransactionCase):
    """
    Lớp chứa các Test Case kiểm tra Model Phiếu Bảo Hành.
    """

    def setUp(self):
        """Chuẩn bị dữ liệu dùng chung cho tất cả test case."""
        super().setUp()
        self.Warranty = self.env['cmcts_warranty.warranty']
        self.Claim = self.env['cmcts_warranty.warranty.claim']

        # Tạo partner mẫu
        self.partner = self.env['res.partner'].create({'name': 'Khách hàng Test CMCTS'})

        # Tạo nhóm sản phẩm demo
        self.categ = self.env['product.category'].create({'name': 'Test Category'})

        # Tạo product demo (product.template → product.product)
        self.product_tmpl = self.env['product.template'].create({
            'name': 'Laptop Dell XPS 15',
            'type': 'consu',
            'categ_id': self.categ.id,
            'tracking': 'serial',
        })
        self.product = self.product_tmpl.product_variant_ids[0]

        # Tạo lot/serial demo
        self.lot = self.env['stock.lot'].create({
            'name': 'SN-TEST-0001',
            'product_id': self.product.id,
            'company_id': self.env.company.id,
        })

        # Dữ liệu mẫu hợp lệ cho 1 phiếu BH
        self.valid_warranty_vals = {
            'product_id': self.product.id,
            'lot_id': self.lot.id,
            'partner_id': self.partner.id,
            'sale_date': date.today() - relativedelta(months=3),
            'warranty_months': 12,
        }

    def _make_lot(self, serial_name):
        """Helper: tạo stock.lot mới với serial_name cho self.product."""
        return self.env['stock.lot'].create({
            'name': serial_name,
            'product_id': self.product.id,
            'company_id': self.env.company.id,
        })

    # ===================================================
    # TC-W01: Tạo phiếu bảo hành hợp lệ
    # ===================================================
    def test_01_create_warranty(self):
        """TC-W01: Tạo phiếu bảo hành với dữ liệu hợp lệ → thành công"""
        warranty = self.Warranty.create(self.valid_warranty_vals)
        self.assertTrue(warranty.id, "Phải tạo được phiếu bảo hành.")
        self.assertEqual(warranty.product_name, 'Laptop Dell XPS 15')
        self.assertEqual(warranty.state, 'active', "Trạng thái mặc định phải là 'active'.")

    # ===================================================
    # TC-W02: Mã phiếu BH được tự động sinh (WH/xxxx)
    # ===================================================
    def test_02_auto_sequence_name(self):
        """TC-W02: Mã phiếu BH phải được tự động tạo theo sequence WH/xxxx"""
        warranty = self.Warranty.create(self.valid_warranty_vals)
        self.assertNotEqual(warranty.name, 'New', "Mã phiếu phải được sinh tự động, không phải 'New'.")
        self.assertTrue(warranty.name.startswith('WH/'), "Mã phiếu BH phải bắt đầu bằng 'WH/'.")

    # ===================================================
    # TC-W03: Computed field ngày hết hạn tính đúng
    # ===================================================
    def test_03_compute_expiry_date(self):
        """TC-W03: Ngày hết hạn = ngày mua + warranty_months"""
        sale_date = date.today() - relativedelta(months=3)
        warranty = self.Warranty.create({
            **self.valid_warranty_vals,
            'sale_date': sale_date,
            'warranty_months': 12,
        })
        expected_expiry = sale_date + relativedelta(months=12)
        self.assertEqual(
            warranty.expiry_date, expected_expiry,
            f"Ngày hết hạn phải là {expected_expiry} (ngày mua + 12 tháng)."
        )

    # ===================================================
    # TC-W04: Serial Number (lot_id) không được trùng lặp
    # ===================================================
    def test_04_duplicate_serial_number(self):
        """TC-W04: Tạo 2 phiếu cùng lot_id (Serial) → ValidationError"""
        self.Warranty.create(self.valid_warranty_vals)
        with self.assertRaises(ValidationError):
            self.Warranty.create({
                **self.valid_warranty_vals,
                # Cùng lot_id → phải bị chặn
            })

    # ===================================================
    # TC-W05: Thời gian BH không hợp lệ (= 0)
    # ===================================================
    def test_05_invalid_warranty_months_zero(self):
        """TC-W05: warranty_months = 0 → ValidationError"""
        new_lot = self._make_lot('SN-TEST-0099')
        with self.assertRaises(ValidationError):
            self.Warranty.create({
                **self.valid_warranty_vals,
                'lot_id': new_lot.id,
                'warranty_months': 0,
            })

    # ===================================================
    # TC-W06: Thời gian BH không hợp lệ (> 120 tháng)
    # ===================================================
    def test_06_invalid_warranty_months_over_max(self):
        """TC-W06: warranty_months > 120 → ValidationError"""
        new_lot = self._make_lot('SN-TEST-0098')
        with self.assertRaises(ValidationError):
            self.Warranty.create({
                **self.valid_warranty_vals,
                'lot_id': new_lot.id,
                'warranty_months': 200,
            })

    # ===================================================
    # TC-W07: Ngày mua trong tương lai → bị chặn
    # ===================================================
    def test_07_future_sale_date(self):
        """TC-W07: sale_date ở tương lai → ValidationError"""
        new_lot = self._make_lot('SN-TEST-0097')
        with self.assertRaises(ValidationError):
            self.Warranty.create({
                **self.valid_warranty_vals,
                'lot_id': new_lot.id,
                'sale_date': date.today() + relativedelta(days=1),
            })

    # ===================================================
    # TC-W08: Hủy phiếu BH → không thể kích hoạt lại
    # ===================================================
    def test_08_cancelled_cannot_reactivate(self):
        """TC-W08: Phiếu đã hủy → không thể đổi về active"""
        warranty = self.Warranty.create(self.valid_warranty_vals)
        warranty.action_cancel()
        self.assertEqual(warranty.state, 'cancelled')
        with self.assertRaises(ValidationError):
            warranty.write({'state': 'active'})

    # ===================================================
    # TC-W09: Tạo Phiếu yêu cầu BH hợp lệ
    # ===================================================
    def test_09_create_warranty_claim(self):
        """TC-W09: Tạo phiếu yêu cầu BH khi phiếu còn hiệu lực → thành công"""
        warranty = self.Warranty.create(self.valid_warranty_vals)
        claim = self.Claim.create({
            'warranty_id': warranty.id,
            'issue_description': 'Màn hình bị sọc ngang sau 3 tháng sử dụng.',
            'received_date': date.today(),
        })
        self.assertTrue(claim.id, "Phải tạo được phiếu yêu cầu BH.")
        self.assertTrue(claim.name.startswith('CLM/'), "Mã yêu cầu phải bắt đầu bằng 'CLM/'.")

    # ===================================================
    # TC-W10: is_valid tự động tính đúng (BH còn hạn)
    # ===================================================
    def test_10_is_valid_when_in_warranty(self):
        """TC-W10: Yêu cầu trong thời hạn BH → is_valid = True"""
        lot = self._make_lot('SN-TEST-0010')
        warranty = self.Warranty.create({
            **self.valid_warranty_vals,
            'lot_id': lot.id,
            'sale_date': date.today() - relativedelta(months=3),
            'warranty_months': 12,
        })
        claim = self.Claim.create({
            'warranty_id': warranty.id,
            'issue_description': 'Test lỗi bàn phím.',
            'received_date': date.today(),
        })
        self.assertTrue(claim.is_valid, "BH còn trong hạn → is_valid phải là True.")

    # ===================================================
    # TC-W11: is_valid = False khi BH hết hạn
    # ===================================================
    def test_11_is_valid_when_expired(self):
        """TC-W11: Yêu cầu sau ngày hết hạn BH → is_valid = False"""
        lot = self._make_lot('SN-TEST-0011')
        warranty = self.Warranty.create({
            **self.valid_warranty_vals,
            'lot_id': lot.id,
            'sale_date': date.today() - relativedelta(years=2),
            'warranty_months': 12,
        })
        claim = self.Claim.create({
            'warranty_id': warranty.id,
            'issue_description': 'Test lỗi pin yếu.',
            'received_date': date.today(),
        })
        self.assertFalse(claim.is_valid, "BH đã hết hạn → is_valid phải là False.")

    # ===================================================
    # TC-W12: State Machine - Rainbow Man khi hoàn thành
    # ===================================================
    def test_12_action_done_rainbow_man(self):
        """TC-W12: action_done → đổi state + trả về hiệu ứng Rainbow Man"""
        warranty = self.Warranty.create(self.valid_warranty_vals)
        claim = self.Claim.create({
            'warranty_id': warranty.id,
            'issue_description': 'Test hoàn thành.',
            'received_date': date.today(),
            'state': '2_processing',
        })
        result = claim.action_done()
        self.assertEqual(claim.state, '3_done', "State phải là '3_done' sau action_done.")
        self.assertIn('effect', result, "Phải trả về dict có key 'effect'.")
        self.assertEqual(result['effect']['type'], 'rainbow_man')

    # ===================================================
    # TC-W13: State Machine - Không thể đảo ngược từ Done
    # ===================================================
    def test_13_state_no_rollback_from_done(self):
        """TC-W13: Claim đã Done → không thể quay về Processing → ValidationError"""
        warranty = self.Warranty.create(self.valid_warranty_vals)
        claim = self.Claim.create({
            'warranty_id': warranty.id,
            'issue_description': 'Test rollback.',
            'received_date': date.today(),
            'state': '3_done',
        })
        with self.assertRaises(ValidationError):
            claim.write({'state': '2_processing'})

    # ===================================================
    # TC-W14: claim_count tự động cập nhật
    # ===================================================
    def test_14_claim_count_updates(self):
        """TC-W14: claim_count tăng đúng khi thêm phiếu yêu cầu"""
        lot = self._make_lot('SN-TEST-0014')
        warranty = self.Warranty.create({
            **self.valid_warranty_vals,
            'lot_id': lot.id,
        })
        self.assertEqual(warranty.claim_count, 0)
        self.Claim.create({
            'warranty_id': warranty.id,
            'issue_description': 'Lần 1.',
            'received_date': date.today(),
        })
        warranty.invalidate_recordset()
        self.assertEqual(warranty.claim_count, 1, "claim_count phải là 1 sau khi thêm 1 yêu cầu.")
