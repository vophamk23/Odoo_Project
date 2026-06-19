# VoPC-cmcts - Phase 2: Quản lý Bảo Hành Thiết Bị

> Dự án phát triển module **Quản lý Bảo Hành Thiết Bị (Warranty Management)** trên nền tảng **Odoo 18**, được xây dựng độc lập và tích hợp vào hệ thống VoPC-cmcts từ Phase 1.
> Module được thiết kế phục vụ công ty kinh doanh thiết bị công nghệ **CMCTS** — quản lý toàn bộ vòng đời bảo hành cho các sản phẩm đã bán, từ tiếp nhận đến xử lý yêu cầu.

## Công nghệ sử dụng

| Thành phần        | Phiên bản               |
| ----------------- | ----------------------- |
| Framework         | Odoo 18.0               |
| Database          | PostgreSQL 14           |
| Môi trường        | Docker + Docker Compose |
| Ngôn ngữ Backend  | Python 3                |
| Ngôn ngữ Frontend | XML, CSS                |
| Bảo mật           | CSV (ACL)               |

## Tính năng chính

### 📋 Quản lý Phiếu Bảo Hành (`cmcts_warranty.warranty`)

- Lưu thông tin thiết bị: tên, serial number, nhóm sản phẩm
- Liên kết khách hàng (`res.partner`), đơn hàng gốc (`sale.order`), serial (`stock.lot`)
- **Mã phiếu tự động**: `WH/0001`, `WH/0002`, ... — không cho nhập tay
- **Tự động tính ngày hết hạn** = ngày mua + số tháng bảo hành
- **Tự động chuyển trạng thái** `expired` nếu phiếu quá hạn ngay lúc tạo
- **Cron job hàng đêm** quét và cập nhật phiếu hết hạn
- **Lọc serial động**: dropdown serial chỉ hiển thị serial đúng sản phẩm, đúng đơn hàng, chưa được dùng
- Theo dõi trạng thái: `Còn hiệu lực → Hết hạn → Đã hủy`
- Phiếu đã hủy không thể kích hoạt lại
- Smart button hiển thị số lần yêu cầu bảo hành

### 🔧 Quản lý Phiếu Yêu cầu Bảo Hành (`cmcts_warranty.warranty.claim`)

- Tạo phiếu tiếp nhận khi khách mang thiết bị đến sửa
- **Tự động kiểm tra** BH còn hợp lệ hay hết hạn tại thời điểm tiếp nhận (`is_valid`)
- **Mã phiếu tự động**: `CLM/0001`, `CLM/0002`, ...
- Quy trình xử lý: `Tiếp nhận → Đang xử lý → Hoàn thành / Từ chối`
- Phân công kỹ thuật viên xử lý, theo dõi ngày dự kiến trả máy
- Hiệu ứng Rainbow Man khi hoàn thành xử lý thành công

### 🎨 Giao diện (UI/UX)

- **Form View**: statusbar, ribbon, smart button, tabs, chatter đầy đủ
- **List View**: decoration màu theo trạng thái, widget `remaining_days`
- **Kanban View**: thẻ nhóm theo trạng thái, color picker, ảnh thiết bị
- **Search View**: bộ lọc nhanh theo trạng thái, group by nhóm sản phẩm / kỹ thuật viên
- **Graph & Pivot View**: thống kê yêu cầu BH theo kỹ thuật viên và trạng thái

### 📝 Ghi log thay đổi

- Kế thừa `mail.thread` và `mail.activity.mixin`
- Tất cả fields quan trọng đều có `tracking=True` → tự động ghi vào Chatter

### 🔐 Phân quyền 4 Lớp

| Lớp                      | File                  | Mô tả                                                                 |
| ------------------------ | --------------------- | --------------------------------------------------------------------- |
| **Lớp 1** - App/Menu     | `warranty_menus.xml`  | Odoo tự ẩn menu nếu user không có quyền đọc                           |
| **Lớp 2** - Model (CRUD) | `ir.model.access.csv` | `group_warranty_technician`: chỉ đọc / `group_warranty_manager`: toàn quyền |
| **Lớp 3** - Record       | `warranty_rules.xml`  | Nhân viên chỉ thấy phiếu BH do mình phụ trách                         |
| **Lớp 4** - Field        | `warranty.py`         | Trường ghi chú nội bộ và kỹ thuật viên chỉ Manager mới thấy           |

## Cấu trúc thư mục

```
addons/cmcts_warranty/
├── __manifest__.py
├── models/
│   ├── warranty.py              # Model: cmcts_warranty.warranty
│   └── warranty_claim.py        # Model: cmcts_warranty.warranty.claim
├── views/
│   ├── warranty_views.xml       # Form, List, Kanban, Search, Graph, Pivot
│   └── warranty_menus.xml       # Menu và Actions
├── security/
│   ├── warranty_groups.xml      # Groups: User / Manager
│   ├── warranty_rules.xml       # Record Rules (row-level security)
│   └── ir.model.access.csv      # Model-level Access Control
├── data/
│   ├── warranty_sequence.xml    # Sequence: WH/0001, CLM/0001
│   └── warranty_cron.xml        # Cron job hàng đêm
├── tests/
│   ├── test_warranty_model.py   # Test logic nghiệp vụ
│   └── test_warranty_security.py # Test phân quyền
├── demo/
│   └── demo.xml                 # Dữ liệu mẫu
└── static/
    ├── description/icon.png
    └── src/css/warranty_style.css
```

## Hướng dẫn cài đặt & khởi động

**Yêu cầu:** Docker và Docker Compose đã được cài đặt.

```bash
# 1. Clone repository
git clone https://github.com/vophamk23/Odoo_Project.git
cd Odoo_Project

# 2. Khởi động hệ thống
docker compose up -d

# 3. Truy cập
# Odoo: http://localhost:8069
# Đăng nhập: admin / admin
```

## Hướng dẫn cập nhật module (sau khi sửa code)

```bash
# Cập nhật module
docker compose exec odoo odoo -u cmcts_warranty --stop-after-init -d vopc-cmcts

# Khởi động lại server
docker compose restart odoo
```

## Hướng dẫn chạy Unit Test

| File                        | Mô tả                                             |
| --------------------------- | ------------------------------------------------- |
| `test_warranty_model.py`    | CRUD, computed fields, validation, state machine  |
| `test_warranty_security.py` | Phân quyền: không có quyền / chỉ đọc / toàn quyền |

```bash
# Chạy toàn bộ test
docker compose run --rm odoo odoo \
  --db_host=db --db_user=odoo --db_password=odoo \
  --test-enable --test-tags cmcts_warranty \
  -u cmcts_warranty -d vopc-test --stop-after-init --log-level=test

# Chạy test model
docker compose run --rm odoo odoo \
  --db_host=db --db_user=odoo --db_password=odoo \
  --test-enable --test-tags cmcts_warranty.TestWarrantyModel \
  -u cmcts_warranty -d vopc-test --stop-after-init --log-level=test

# Chạy test phân quyền
docker compose run --rm odoo odoo \
  --db_host=db --db_user=odoo --db_password=odoo \
  --test-enable --test-tags cmcts_warranty.TestWarrantySecurity \
  -u cmcts_warranty -d vopc-test --stop-after-init --log-level=test
```

**Đọc kết quả:**

- ✅ `0 failed, 0 error(s)` → Tất cả PASS
- ❌ `X failed` → Có lỗi logic, kiểm tra file tương ứng

> Database `vopc-test` là DB test riêng biệt, không ảnh hưởng dữ liệu thật.

---

## Luật nghiệp vụ

| Mã   | Mô tả                                                             |
| ---- | ----------------------------------------------------------------- |
| QT1  | Mã phiếu tự động: `WH/0001`, `WH/0002`, ...                       |
| QT2  | Ngày hết hạn tự tính: `expiry_date = sale_date + warranty_months` |
| QT3  | Tự động hết hạn ngay lúc tạo nếu `expiry_date < hôm nay`          |
| QT4  | Cron hàng đêm quét và cập nhật phiếu hết hạn                      |
| QT5  | Phiếu đã hủy không thể kích hoạt lại                              |
| QT6  | Mỗi số serial chỉ xuất hiện 1 lần trong hệ thống                  |
| QT6b | Dropdown serial lọc động theo sản phẩm và đơn hàng                |
| QT7  | Thời gian bảo hành từ 1 đến 120 tháng                             |
| QT8  | Ngày mua không được là ngày tương lai                             |
| QT9  | Theo dõi số lần yêu cầu BH và trạng thái đang mở                  |

## Thành viên

| Họ và Tên    | MSSV | Vai trò                           |
| ------------ | ---- | --------------------------------- |
| Phạm Công Võ | -    | Phát triển toàn bộ module Phase 2 |

## Liên kết

- 📦 Phase 1 (VoPC-cmcts): [github.com/vophamk23/Odoo_Project](https://github.com/vophamk23/Odoo_Project)
- 🏫 Trường: Đại học Bách Khoa – ĐHQG TP.HCM
- 🏢 Khoa: Khoa học và Kỹ thuật Máy Tính
