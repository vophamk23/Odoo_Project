# AccessLogUpload API

## Overview

Nhận dữ liệu access log từ controller hardware và ghi vào hệ thống.

- **Endpoint name**: `AccessLogUpload`
- **Model**: `t4.gate_keeper.controller`
- **Method**: `controller_log`

---

## Request Body

```json
{
    "controller_sn": "CTRL-001",
    "devices": [
        {
            "device_sn": "DEV-001",
            "records": [
                {
                    "emp_id": 1,
                    "punch_type": "check_in",
                    "verify_mode": "face",
                    "punched_at": "2026-08-05T07:30:00+07:00"
                }
            ]
        }
    ]
}
```

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `controller_sn` | string | ✅ | Serial number của controller đã đăng ký trong hệ thống. |
| `devices` | array | ✅ | Danh sách device kèm access records. |

### Device Object

| Field | Type | Required | Description |
|---|---|---|---|
| `device_sn` | string | ✅ | Serial number của device. Phải thuộc controller đã chỉ định. |
| `records` | array | ❌ | Danh sách access log records. Nếu rỗng hoặc không có, device sẽ bị bỏ qua. |

### Record Object

| Field | Type | Required | Description |
|---|---|---|---|
| `emp_id` | integer | ✅ | Employee ID (số nguyên) đã đăng ký trong `t4.gate_keeper.employee`. |
| `punch_type` | string | ❌ | Loại chấm công. Giá trị hợp lệ: `check_in`, `check_out`. Mặc định: `unk` (Unknown). |
| `verify_mode` | string | ❌ | Phương thức xác thực. Giá trị hợp lệ: `face`, `fingerprint`, `card`, `password`, `other`. Mặc định: `other`. |
| `punched_at` | string | ❌ | Thời gian chấm công. Hỗ trợ ISO 8601 (ví dụ `2026-08-05T07:30:00+07:00`). Nếu không gửi, dùng thời gian hiện tại server. |

---

## Response

### Success (có records tạo thành công)

```json
{
    "success": true,
    "message": "3 access log(s) created successfully.",
    "data": {
        "created_count": 3
    }
}
```

### Success (có records thành công + có warnings)

```json
{
    "success": true,
    "message": "2 access log(s) created successfully.",
    "data": {
        "created_count": 2,
        "warnings": [
            "Employee with ID '999' not found. Skipped record on device 'DEV-002'.",
            "Device 'DEV-003' is not registered under controller 'CTRL-001'."
        ]
    }
}
```

### Success (không có device data)

```json
{
    "success": true,
    "message": "No device data provided.",
    "data": null
}
```

### Error (thiếu controller_sn)

```json
{
    "success": false,
    "message": "Controller serial number is required."
}
```

### Error (controller chưa đăng ký)

```json
{
    "success": false,
    "message": "Controller with serial number 'UNKNOWN-SN' is not registered."
}
```

---

## Validation Rules

| Rule | Behavior |
|---|---|
| `controller_sn` thiếu | ❌ Raise error, dừng xử lý. |
| Controller chưa đăng ký | ❌ Raise error, dừng xử lý. |
| `device_sn` thiếu trong một device entry | ⚠️ Skip device đó, thêm warning. |
| Device chưa đăng ký dưới controller | ⚠️ Skip device đó, thêm warning. |
| `emp_id` thiếu trong record | ⚠️ Skip record đó, thêm warning. |
| `emp_id` không phải số nguyên hợp lệ | ⚠️ Skip record đó, thêm warning. |
| Employee không tìm thấy | ⚠️ Skip record đó, thêm warning. |
| `punch_type` không hợp lệ hoặc thiếu | ✅ Mặc định `unk` (Unknown). |
| `verify_mode` không hợp lệ hoặc thiếu | ✅ Mặc định `other`. |
| `punched_at` thiếu hoặc parse lỗi | ✅ Mặc định thời gian hiện tại server (UTC). |

---

## Access Log Fields Mapping

| Request field | Access Log field | Type | Notes |
|---|---|---|---|
| (from controller lookup) | `controller_id` | Many2one | ID controller tìm bằng `controller_sn`. |
| (from device lookup) | `device_id` | Many2one | ID device tìm bằng `device_sn` + `controller_id`. |
| `emp_id` | `employee_id` | Many2one | ID employee tìm bằng `emp_id`. |
| `punched_at` | `access_time` | Datetime | ISO 8601 → naive UTC. |
| `punch_type` | `direction` | Selection | `check_in` → `in`, `check_out` → `out`, else → `unk`. |
| `verify_mode` | `verification_type` | Selection | `face`, `fingerprint`, `card`, `password`, `other`. |
| (auto) | `sync_status` | Selection | Luôn set `success`. |
| (auto, related) | `branch_id` | Many2one | Related từ `controller_id.branch_id`. |
| (auto, related) | `area_id` | Many2one | Related từ `device_id.area_id`. |

---

## Datetime Handling

- **Input**: ISO 8601 format, ví dụ `2026-08-05T07:30:00+07:00` hoặc `2026-08-05T00:30:00Z`.
- **Storage**: Odoo lưu Datetime dạng naive UTC (`2026-08-05 00:30:00`).
- **Conversion**: Nếu input có timezone offset, tự động convert về UTC rồi bỏ timezone info.
- **Fallback**: Nếu parse thất bại hoặc thiếu, dùng `fields.Datetime.now()`.

---

## Side Effects

Khi access log được tạo, model `t4.gate_keeper.access_log` sẽ tự động:

1. **Kiểm tra working hours**: Nếu `access_time` nằm ngoài giờ làm việc (08:00 - 17:00) hoặc cuối tuần, và device thuộc một Area, hệ thống tạo `t4.gate_keeper.area_warning` loại `invalid_access`.
2. **Timezone-aware**: Check giờ làm việc dựa trên timezone của Branch.

---

## Example: cURL

```bash
curl -X POST https://your-odoo-server/api/AccessLogUpload \
  -H "Content-Type: application/json" \
  -d '{
    "controller_sn": "CTRL-001",
    "devices": [
        {
            "device_sn": "DEV-001",
            "records": [
                {
                    "emp_id": 1,
                    "punch_type": "check_in",
                    "verify_mode": "fingerprint",
                    "punched_at": "2026-08-05T08:00:00+07:00"
                },
                {
                    "emp_id": 2,
                    "punch_type": "check_out",
                    "verify_mode": "face",
                    "punched_at": "2026-08-05T17:30:00+07:00"
                }
            ]
        },
        {
            "device_sn": "DEV-002",
            "records": [
                {
                    "emp_id": 3,
                    "punch_type": "check_in",
                    "verify_mode": "card",
                    "punched_at": "2026-08-05T07:45:00+07:00"
                }
            ]
        }
    ]
}'
```
