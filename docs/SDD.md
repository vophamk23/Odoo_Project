# Tài liệu Đặc tả Kiến trúc và Thiết kế Module (SDD)

**Dự án:** VoPC-CMCTS Phase 1  
**Phiên bản:** 1.0  
**Ngày lập:** 09/06/2026

Tài liệu này (System Design Document) đóng vai trò là "bản vẽ thi công" kỹ thuật dành cho đội ngũ phát triển Odoo. Nó quy định kiến trúc tổng thể, cách chia nhỏ các module và đặc tả chi tiết về việc kế thừa (inherit) Models/Views trong Odoo 18.

---

## 1. Kiến trúc tổng thể hệ thống (System Architecture)

Hệ thống tuân thủ chặt chẽ kiến trúc 3 lớp (3-tier architecture) tiêu chuẩn của Odoo:

1. **Lớp Dữ liệu (Data Tier):**
   - Quản trị bởi hệ quản trị cơ sở dữ liệu **PostgreSQL 14+**.
   - Lưu trữ toàn bộ dữ liệu cấu trúc (Bảng, Quan hệ, Dữ liệu thực tế).

2. **Lớp Logic Nghiệp vụ (Logic Tier / Application Layer):**
   - Lõi Odoo Framework viết bằng **Python 3.10+**.
   - Giao tiếp với DB thông qua hệ thống **Odoo ORM** (Object-Relational Mapping), loại bỏ việc viết câu lệnh SQL thô, đảm bảo tính toàn vẹn và security.

3. **Lớp Hiển thị (Presentation Tier):**
   - Backend: Dùng **Web Client (Owl Framework)**, các file XML định nghĩa giao diện (Views).
   - Frontend (Website): Dùng **QWeb Engine** (Template engine của Odoo) kết hợp Bootstrap, HTML5/CSS3.

### Kiến trúc triển khai (Deployment Architecture)
Dự án chạy hoàn toàn trên nền tảng Container:
- `odoo-web`: Container chạy tiến trình Odoo Server (Port 8069). Map volume thư mục `addons/` vào trong container để code nhận ngay lập tức.
- `odoo-db`: Container chạy tiến trình PostgreSQL (Port 5432).
- Mạng: 2 container kết nối qua mạng nội bộ Docker network (bridge).

---

## 2. Đặc tả cấu trúc thư mục Custom Addons

Toàn bộ code lập trình riêng cho dự án sẽ nằm trong thư mục `addons/` với cấu trúc sau:

```text
addons/
├── cmcts_inventory/     # Module quy định ràng buộc Serial Number
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   └── stock_picking.py
│   ├── views/
│   │   └── stock_picking_views.xml
│   └── security/
│       └── ir.model.access.csv
├── cmcts_crm/           # Module tự động hoá Sales Pipeline
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   └── crm_lead.py
│   └── data/
│       ├── automation_rules.xml
│       └── mail_templates.xml
└── cmcts_website/       # Module giao diện & Web form API
    ├── __init__.py
    ├── __manifest__.py
    ├── controllers/
    │   └── main.py
    └── views/
        ├── homepage_templates.xml
        └── contact_form_templates.xml
```

---

## 3. Đặc tả chi tiết từng Module

### 3.1 Module `cmcts_inventory` (Quản trị Kho lõi)

**Mục tiêu:** Ràng buộc chặt chẽ quy trình Nhập - Xuất - Chuyển kho phải thông qua quét/nhập Serial Number.

- **Models (Kế thừa Python):**
  - **Kế thừa `stock.picking`:** Viết hàm override `button_validate()`. Trước khi Odoo cho phép hoàn thành phiếu, quét qua tất cả `move_line_ids`. Nếu sản phẩm có thuộc tính `tracking == 'serial'` mà người dùng bỏ trống trường `lot_name` (lúc nhập) hoặc `lot_id` (lúc xuất), raise ra một `UserError` chặn Validate.
  - **Kế thừa `product.template`:** (Tùy chọn) Force default field `tracking` thành `serial` khi nhân viên tạo sản phẩm mới để tránh quên.

- **Views (Tùy biến XML):**
  - **Inherit `stock.view_picking_form`:** Điều chỉnh lại giao diện tab "Detailed Operations" (Chi tiết hoạt động). Highlight cột Serial Number bằng CSS/thuộc tính XML để nhân viên kho dễ chú ý.

- **Security (Phân quyền):**
  - Khai báo file `security/ir.model.access.csv` nếu có tạo thêm bảng phụ.
  - Đảm bảo tuân thủ role mặc định của nhóm `group_stock_user`.

### 3.2 Module `cmcts_website` (Giao diện & Web Form)

**Mục tiêu:** Hiển thị giao diện trang chủ chuyên nghiệp và xây dựng form liên hệ đổ trực tiếp về CRM.

- **Controllers (Xử lý API bằng Python):**
  - Tạo class kế thừa `http.Controller`.
  - Khai báo route `@http.route(['/tu-van/submit'], type='http', auth="public", website=True)`.
  - **Logic:** Hứng dữ liệu (POST request) gồm Tên, Email, SĐT. Sử dụng `request.env['crm.lead'].sudo().create({...})` để bypass quyền public, tạo thẳng record vào bảng `crm.lead`. Trả về trang "Cảm ơn".

- **Views (QWeb XML):**
  - **`homepage_templates.xml`:** Chứa cấu trúc HTML thiết kế riêng cho Hero Banner, Danh sách tính năng, và Footer.
  - **`contact_form_templates.xml`:** Chứa HTML form `<form action="/tu-van/submit" method="post">` kèm thẻ input required cho Tên, Email.

### 3.3 Module `cmcts_crm` (Tự động hóa Sales Pipeline)

**Mục tiêu:** Tối ưu hiệu suất làm việc của Sale bằng tự động hóa.

- **Data (Tự động hóa bằng XML):**
  - Sử dụng Odoo Automated Actions (module `base_automation`).
  - **`automation_rules.xml`:** Viết file XML tạo record cho bảng `base.automation`.
    - *Trigger:* On Update (Khi cập nhật).
    - *Condition:* `stage_id` chuyển sang ID tương ứng với cột "Đang tư vấn".
    - *Action:* Sinh ra một Activity (bảng `mail.activity`) gán cho `user_id` phụ trách Lead đó với nội dung "Cần gọi điện chăm sóc khách hàng".
  - **`mail_templates.xml`:** Tạo record `mail.template` chuẩn bị sẵn nội dung Báo giá có chứa các biến động (Jinja2) như `${object.partner_id.name}`.

- **Models:**
  - Kế thừa `crm.lead` để bắt các sự kiện (nếu dùng code Python thay vì XML base_automation) thông qua hàm `write()`.

---

*Tài liệu này được lưu tại: `/docs/SDD.md` trên GitHub repo*  
*Cập nhật lần cuối: 09/06/2026*
