# VoPC-CMCTS Phase 1

> Dự án mô phỏng triển khai **Odoo 18** cho một doanh nghiệp kinh doanh thiết bị công nghệ và giải pháp phần mềm, lấy cảm hứng từ [cmcts.com.vn](https://cmcts.com.vn).

## Tổng quan dự án

Mục tiêu của dự án là xây dựng một hệ thống quản trị doanh nghiệp toàn diện bao gồm:

- **Website:** Trang web giới thiệu công ty, sản phẩm và thu thập khách hàng tiềm năng.
- **Quản lý Kho (Inventory):** Quản lý nhập/xuất kho và tracking từng sản phẩm theo Serial Number.
- **Chăm sóc Khách hàng (CRM):** Quy trình xử lý khách hàng tiềm năng (Lead) tự động từ website đến khi chốt hợp đồng.
- **Email Marketing & Events:** Hệ thống tự động chăm sóc và tổ chức sự kiện.

## Yêu cầu hệ thống

- **Hệ điều hành:** Ubuntu 22.04 / Windows 11 với WSL2
- **Docker:** Phiên bản >= 24.0 (Tích hợp Docker Compose v2)
- **Cấu hình phần cứng:** RAM tối thiểu 4GB (khuyến nghị 8GB), Ổ cứng trống > 10GB.

## Cài đặt nhanh

Khởi chạy hệ thống chỉ với 3 dòng lệnh:

```bash
git clone https://github.com/Phase1-team/VoPC-cmcts.git
cd VoPC-cmcts
docker compose up -d
```

- **Hệ thống Odoo:** [http://localhost:8069](http://localhost:8069)
- **Hộp thư nội bộ (Mailhog):** [http://localhost:8025](http://localhost:8025)

## Thông tin đăng nhập mặc định

| Thông tin    | Giá trị               |
| ------------ | --------------------- |
| **URL**      | http://localhost:8069 |
| **Username** | admin                 |
| **Password** | admin                 |
| **Database** | vopc_cmcts            |

## Hướng dẫn Khôi phục dữ liệu (Restore)

Nếu hệ thống gặp sự cố, bạn có thể bung file backup để khôi phục lại dữ liệu bằng các lệnh sau:

```bash
# 1. Giải nén file backup
gunzip backup/TÊN_FILE.sql.gz

# 2. Nạp dữ liệu vào database PostgreSQL
docker exec -i vopc_db psql -U odoo -d vopc_cmcts < backup/TÊN_FILE.sql
```

## Git Workflow

Nhóm tuân thủ quy trình Git phân nhánh cơ bản:

- `main`: Nhánh chứa code ổn định nhất (Production).
- `develop`: Nhánh chứa code đang phát triển và test.
- `feature/xxx`: Nhánh cá nhân khi làm tính năng mới.

## Thành viên nhóm

| Họ và Tên    | Vai trò     | Chịu trách nhiệm                                                    |
| ------------ | ----------- | ------------------------------------------------------------------- |
| Phạm Công Võ | Trưởng nhóm | Toàn bộ dự án (Cấu hình Hệ thống, DevOps, Kho, CRM, Website, UI/UX) |
