# -*- coding: utf-8 -*-
# Mục đích: Kiểm thử toàn bộ 8 API Endpoint theo từng mã phản hồi:
#   - 200 OK  : Dữ liệu hợp lệ, xử lý thành công.
#   - 400     : Thiếu trường bắt buộc / dữ liệu không tồn tại.
#   - 401     : Không có token / token sai (kiểm ở tầng HTTP, không mock ở đây).
#
# Chiến lược: Mock get_body() để inject payload giả lập từ phần cứng.
#             ValidationError từ Odoo ⟺ HTTP 400 ở tầng framework.

from odoo.tests import common
from odoo.exceptions import ValidationError
from werkzeug.exceptions import BadRequest
from unittest.mock import patch, MagicMock
import unittest


class TestApiResponseCodes(common.TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # --- Dữ liệu nền ---
        cls.branch = cls.env["t4.gate_keeper.branch"].create({
            "name": "Branch Response Test",
            "timezone": "Asia/Ho_Chi_Minh",
        })
        cls.branch_other = cls.env["t4.gate_keeper.branch"].create({
            "name": "Branch Other",
            "timezone": "Asia/Tokyo",
        })

        cls.area = cls.env["t4.gate_keeper.area"].create({
            "name": "Test Area",
            "branch_id": cls.branch.id,
        })

        cls.controller = cls.env["t4.gate_keeper.controller"].create({
            "name": "Controller Response Test",
            "serial_number": "CTRL-RESP-001",
            "branch_id": cls.branch.id,
            "status": "offline",
        })

        cls.device_model = cls.env["t4.gate_keeper.device_model"].create({
            "name": "Model Resp Test",
            "version": "1.0",
        })

        cls.device = cls.env["t4.gate_keeper.device"].create({
            "name": "Device Response Test",
            "serial_number": "DEV-RESP-001",
            "controller_id": cls.controller.id,
            "area_id": cls.area.id,
            "device_model_id": cls.device_model.id,
            "status": "offline",
        })

        cls.algorithm = cls.env["t4.gate_keeper.algorithm"].create({
            "name": "Algorithm Resp",
            "code": "resp_algo",
            "version": "1.0",
        })

        cls.employee = cls.env["t4.gate_keeper.employee"].create({
            "name": "Employee Response Test",
            "branch_id": cls.branch.id,
            "emp_id": 3001,
        })
        cls.employee_other_branch = cls.env["t4.gate_keeper.employee"].create({
            "name": "Employee Other Branch",
            "branch_id": cls.branch_other.id,
            "emp_id": 9999,
        })

        cls.biometric = cls.env["t4.gate_keeper.employee.biometric"].create({
            "employee_id": cls.employee.id,
            "device_model_id": cls.device_model.id,
            "algorithm_id": cls.algorithm.id,
            "biometric_type": "base64",
            "binary_template": b"dGVzdF90ZW1wbGF0ZQ==",
        })

    # -------------------------------------------------------------------------
    # Helper
    # -------------------------------------------------------------------------
    def _patch(self, payload):
        """Trả về context manager giả lập get_body() với payload cho trước."""
        mock_req = MagicMock()
        mock_app = MagicMock()
        mock_req.env = MagicMock(wraps=self.env)
        mock_req.env.__getitem__.side_effect = lambda key: mock_app if key == 'core.api.application' else self.env[key]
        
        p_req = patch(
            "odoo.addons.t4_coreapi.utils.core_api_utils.request", mock_req
        )
        p_body = patch(
            "odoo.addons.t4_gate_keeper.models.gk_controller.get_body",
            return_value=payload,
        )
        return p_req, p_body

    # =========================================================================
    # API 2: HEART BEAT
    # =========================================================================

    def test_heartbeat_200_online(self):
        """✅ 200 — Heartbeat hợp lệ, controller + device online."""
        payload = {
            "controller_sn": "CTRL-RESP-001",
            "devices_status": [{"device_sn": "DEV-RESP-001", "status": "online"}],
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.controller_heartbeat()

        self.assertEqual(self.controller.status, "online")
        self.assertEqual(self.device.status, "online")
        self.assertEqual(res.get("message"), "Success")

    def test_heartbeat_200_device_offline(self):
        """✅ 200 — Heartbeat báo device offline."""
        payload = {
            "controller_sn": "CTRL-RESP-001",
            "devices_status": [{"device_sn": "DEV-RESP-001", "status": "offline"}],
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.controller_heartbeat()

        self.assertEqual(self.device.status, "offline")
        self.assertEqual(res.get("message"), "Success")

    def test_heartbeat_400_missing_sn(self):
        """❌ 400 — Thiếu controller_sn → BadRequest."""
        payload = {"devices_status": []}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(BadRequest):
                self.controller.controller_heartbeat()

    def test_heartbeat_400_fake_sn(self):
        """❌ 400 — controller_sn không tồn tại → ValidationError."""
        payload = {"controller_sn": "CTRL-FAKE-XYZ", "devices_status": []}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.controller_heartbeat()

    # =========================================================================
    # API 3: EMPLOYEE SYNC
    # =========================================================================

    def test_employee_sync_200_first_sync(self):
        """✅ 200 — Lần đầu sync (last_sync_at = False) → nhân viên nằm trong new[]."""
        self.controller.write({"last_sync_at": False})
        payload = {"controller_sn": "CTRL-RESP-001"}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.controller_employee_sync()

        self.assertEqual(res.get("message"), "Employee Sync Completed")
        data = res["data"][0]
        self.assertIn("new", data)
        self.assertIn("update", data)
        self.assertIn("deleted", data)
        emp_ids = [e["id"] for e in data["new"]]
        self.assertIn(self.employee.emp_id, emp_ids)

    def test_employee_sync_200_delta_empty(self):
        """✅ 200 — Sync lần hai không có thay đổi → tất cả danh sách rỗng."""
        from odoo.fields import Datetime
        from datetime import timedelta
        self.controller.write({"last_sync_at": Datetime.now() + timedelta(minutes=10)})
        payload = {"controller_sn": "CTRL-RESP-001"}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.controller_employee_sync()

        data = res["data"][0]
        total = len(data["new"]) + len(data["update"]) + len(data["deleted"])
        self.assertEqual(total, 0)

    def test_employee_sync_400_missing_sn(self):
        """❌ 400 — Thiếu controller_sn → BadRequest."""
        payload = {}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(BadRequest):
                self.controller.controller_employee_sync()

    def test_employee_sync_400_fake_sn(self):
        """❌ 400 — controller_sn không tồn tại → ValidationError."""
        payload = {"controller_sn": "CTRL-FAKE-XYZ"}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.controller_employee_sync()

    # =========================================================================
    # API 4: CONTROLLER REGISTER
    # =========================================================================

    def test_controller_register_200_full(self):
        """✅ 200 — Đăng ký controller đầy đủ thông tin."""
        payload = {
            "serial_number": "CTRL-RESP-001",
            "branch_code": "Branch Response Test",
            "firmware_version": "v3.0.0",
            "ip_address": "192.168.99.1",
            "connection_type": "tcp_ip",
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.controller_register()

        self.assertEqual(res.get("message"), "Controller registered successfully")

    def test_controller_register_200_minimal(self):
        """✅ 200 — Đăng ký controller tối thiểu (chỉ serial + branch_code)."""
        payload = {
            "serial_number": "CTRL-RESP-001",
            "branch_code": "Branch Response Test",
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.controller_register()

        self.assertEqual(res.get("message"), "Controller registered successfully")

    def test_controller_register_400_missing_serial(self):
        """❌ 400 — Thiếu serial_number → BadRequest."""
        payload = {"branch_code": "Branch Response Test"}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(BadRequest):
                self.controller.controller_register()

    def test_controller_register_400_missing_branch(self):
        """❌ 400 — Thiếu branch_code → BadRequest."""
        payload = {"serial_number": "CTRL-RESP-001"}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(BadRequest):
                self.controller.controller_register()

    def test_controller_register_400_fake_branch(self):
        """❌ 400 — branch_code không tồn tại → ValidationError."""
        payload = {
            "serial_number": "CTRL-NEW-FAKE",
            "branch_code": "BRANCH-FAKE-XYZ-DOES-NOT-EXIST",
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.controller_register()

    # =========================================================================
    # API 5: DEVICE REGISTER
    # =========================================================================

    def test_device_register_200_full(self):
        """✅ 200 — Đăng ký device đầy đủ thông tin."""
        payload = {
            "name": "Dev Response Full",
            "serial_number": "DEV-RESP-001",
            "controller_sn": "CTRL-RESP-001",
            "firmware_version": "v1.5.0",
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.device_register()

        self.assertEqual(res.get("message"), "Device registered successfully")
        self.assertIn("device_id", res.get("data", {}))

    def test_device_register_200_minimal(self):
        """✅ 200 — Đăng ký device tối thiểu (name + serial + controller_sn)."""
        payload = {
            "name": "Dev Minimal",
            "serial_number": "DEV-RESP-MINIMAL",
            "controller_sn": "CTRL-RESP-001",
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.device_register()

        self.assertEqual(res.get("message"), "Device registered successfully")

    def test_device_register_400_missing_serial(self):
        """❌ 400 — Thiếu serial_number → ValidationError."""
        payload = {
            "name": "Dev No Serial",
            "controller_sn": "CTRL-RESP-001",
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.device_register()

    def test_device_register_400_missing_controller(self):
        """❌ 400 — Thiếu controller_sn → ValidationError."""
        payload = {
            "name": "Dev No Ctrl",
            "serial_number": "DEV-RESP-NO-CTRL",
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.device_register()

    def test_device_register_400_fake_controller(self):
        """❌ 400 — controller_sn không tồn tại → ValidationError."""
        payload = {
            "name": "Dev Fake Ctrl",
            "serial_number": "DEV-RESP-FAKE",
            "controller_sn": "CTRL-FAKE-XYZ",
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.device_register()

    # =========================================================================
    # API 6: CONTROLLER EMPLOYEE SYNC STATUS
    # =========================================================================

    @unittest.skip("ControllerEmployeeSyncStatus endpoint removed/deprecated from production code")
    def test_sync_status_200_needs_update(self):
        """✅ 200 — Controller đang out_of_sync → update = True."""
        self.controller.write({"employee_sync_status": "out_of_sync"})
        payload = {"controller_sn": "CTRL-RESP-001"}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.controller_employee_sync_status()

        self.assertTrue(res["data"]["update"])
        self.assertEqual(res.get("message"), "Success")

    @unittest.skip("ControllerEmployeeSyncStatus endpoint removed/deprecated from production code")
    def test_sync_status_200_no_update(self):
        """✅ 200 — Controller đã synced → update = False."""
        self.controller.write({"employee_sync_status": "synced"})
        payload = {"controller_sn": "CTRL-RESP-001"}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.controller_employee_sync_status()

        self.assertFalse(res["data"]["update"])

    @unittest.skip("ControllerEmployeeSyncStatus endpoint removed/deprecated from production code")
    def test_sync_status_400_missing_sn(self):
        """❌ 400 — Thiếu controller_sn → BadRequest."""
        payload = {}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(BadRequest):
                self.controller.controller_employee_sync_status()

    @unittest.skip("ControllerEmployeeSyncStatus endpoint removed/deprecated from production code")
    def test_sync_status_400_fake_sn(self):
        """❌ 400 — controller_sn không tồn tại → ValidationError."""
        payload = {"controller_sn": "CTRL-FAKE-XYZ"}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.controller_employee_sync_status()

    # =========================================================================
    # API 7: EMPLOYEE BIOMETRIC GET
    # =========================================================================

    def test_biometric_get_200_with_data(self):
        """✅ 200 — Nhân viên có biometric phù hợp → trả về mảng templates."""
        device_model = self.env["t4.gate_keeper.device_model"].create({
            "name": "Model Resp Test 2",
            "version": "1.0",
        })
        self.device.write({"device_model_id": device_model.id})

        payload = {
            "controller_sn": "CTRL-RESP-001",
            "emp_id": 3001,
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.employee_biometric_get()

        self.assertIn("data", res)
        self.assertEqual(res["data"]["emp_id"], 3001)
        self.assertIsInstance(res["data"].get("finger_templates"), list)

    def test_biometric_get_200_empty_array(self):
        """✅ 200 — Nhân viên không có biometric nào phù hợp → templates rỗng."""
        emp_no_bio = self.env["t4.gate_keeper.employee"].create({
            "name": "Employee No Bio",
            "branch_id": self.branch.id,
            "emp_id": 3002,
        })
        payload = {
            "controller_sn": "CTRL-RESP-001",
            "emp_id": 3002,
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.employee_biometric_get()

        self.assertIn("data", res)
        self.assertEqual(res["data"]["finger_templates"], [])
        self.assertIsNone(res["data"]["face_template"])

    def test_biometric_get_400_missing_controller_sn(self):
        """❌ 400 — Thiếu controller_sn → ValidationError."""
        payload = {"emp_id": 3001}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.employee_biometric_get()

    def test_biometric_get_400_missing_employee_id(self):
        """❌ 400 — Thiếu emp_id → ValidationError."""
        payload = {"controller_sn": "CTRL-RESP-001"}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.employee_biometric_get()

    def test_biometric_get_400_fake_controller(self):
        """❌ 400 — controller_sn không tồn tại → ValidationError."""
        payload = {
            "controller_sn": "CTRL-FAKE-XYZ",
            "emp_id": 3001,
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.employee_biometric_get()

    def test_biometric_get_400_wrong_branch(self):
        """❌ 400 — Nhân viên thuộc chi nhánh khác với Controller → Không lấy được dữ liệu."""
        payload = {
            "controller_sn": "CTRL-RESP-001",
            "emp_id": 9999,
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.employee_biometric_get()
            self.assertIsNone(res["data"]["face_template"])
            self.assertEqual(res["data"]["finger_templates"], [])

    # =========================================================================
    # API 8: CONTROLLER GET CONFIG
    # =========================================================================

    def test_get_config_200_with_devices(self):
        """✅ 200 — Controller có device → trả về danh sách devices đầy đủ."""
        payload = {"controller_sn": "CTRL-RESP-001"}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.controller_get_config()

        self.assertEqual(res.get("message"), "Success")
        self.assertIn("timezone", res)
        self.assertIn("devices", res.get("data", {}))
        self.assertIsInstance(res["data"]["devices"], list)
        self.assertGreaterEqual(len(res["data"]["devices"]), 1)

    def test_get_config_200_structure(self):
        """✅ 200 — Kiểm tra cấu trúc từng phần tử trong devices[]."""
        payload = {"controller_sn": "CTRL-RESP-001"}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.controller_get_config()

        devices = res["data"]["devices"]
        if devices:
            dev = devices[0]
            self.assertIn("device_sn", dev)
            self.assertIn("assigned_area", dev)
            self.assertIn("device_model", dev)
            self.assertIn("status", dev)
            self.assertIn("connection_type", dev)
            self.assertIn("port/channel", dev)
            self.assertIn("supported_biometric_types", dev)

    def test_get_config_400_missing_sn(self):
        """❌ 400 — Thiếu controller_sn → ValidationError."""
        payload = {}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.controller_get_config()

    def test_get_config_400_fake_sn(self):
        """❌ 400 — controller_sn không tồn tại → ValidationError."""
        payload = {"controller_sn": "CTRL-FAKE-XYZ"}
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.controller_get_config()

    # =========================================================================
    # API 8: CONTROLLER SYNC ACK & EXTRA RESPONSES
    # =========================================================================

    @unittest.skip("ControllerSyncAck endpoint removed/deprecated from production code")
    def test_sync_ack_200(self):
        """✅ 200 — Báo hoàn thành đồng bộ thành công."""
        payload = {
            "controller_id": "CTRL-RESP-001",
            "sync_timestamp": "2026-07-20 18:00:00"
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            res = self.controller.sync_ack()

        self.assertEqual(res.get("message"), "Success")
        self.assertEqual(res["data"]["status"], "200 OK")

    @unittest.skip("ControllerSyncAck endpoint removed/deprecated from production code")
    def test_sync_ack_400_missing_id(self):
        """❌ 400 — Thiếu controller_id → BadRequest."""
        payload = {
            "sync_timestamp": "2026-07-20 18:00:00"
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(BadRequest):
                self.controller.sync_ack()

    @unittest.skip("ControllerSyncAck endpoint removed/deprecated from production code")
    def test_sync_ack_400_fake_id(self):
        """❌ 400 — Controller ID không tồn tại → ValidationError."""
        payload = {
            "controller_id": "CTRL-FAKE-XYZ",
            "sync_timestamp": "2026-07-20 18:00:00"
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.sync_ack()

    def test_device_register_400_duplicate_port(self):
        """❌ 400 — Trùng lặp port_or_channel của thiết bị trên cùng Controller → ValidationError."""
        # Đặt port_or_channel cho device đã có
        self.device.write({"port_or_channel": "relay_1"})

        # Thử đăng ký thiết bị mới trùng port_or_channel "relay_1"
        payload = {
            "serial_number": "DEV-RESP-NEW",
            "controller_sn": "CTRL-RESP-001",
            "port_or_channel": "relay_1",
            "name": "New Device Duplicate Port",
        }
        p_req, p_body = self._patch(payload)
        with p_req, p_body:
            with self.assertRaises(ValidationError):
                self.controller.device_register()

