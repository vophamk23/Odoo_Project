# Tài liệu phân tích yêu cầu (SRS)

## 1. Tổng quan hệ thống

- **1.1 Tên dự án:** VoPC-CMCTS Phase 1
- **1.2 Mục tiêu:** Triển khai Odoo 18 cho doanh nghiệp kinh doanh thiết bị công nghệ và giải pháp phần mềm
- **1.3 Phạm vi:** Website E-commerce + Quản lý Kho + CRM
- **1.4 Công nghệ:** Odoo 18, PostgreSQL 14, Docker
- **1.5 Thời gian:** 09/06/2026 → 09/08/2026

## 2. Danh sách người dùng (Actor)

| Actor           | Mô tả                         | Quyền hạn        |
| --------------- | ----------------------------- | ---------------- |
| Admin           | Quản trị viên hệ thống        | Toàn bộ hệ thống |
| Nhân viên Kho   | Thực hiện nhập/xuất/kiểm kê   | Inventory module |
| Nhân viên Sales | Quản lý CRM, follow up khách  | CRM module       |
| Khách hàng      | Duyệt website, đăng ký tư vấn | Website (public) |

## 3. Sơ đồ Use Case

```mermaid
usecaseDiagram
    actor "Khách hàng" as KH
    actor "Nhân viên Kho" as NV_Kho
    actor "Nhân viên Sales" as NV_Sales

    package "Website Module" {
        usecase "UC01: Xem trang chủ" as UC01
        usecase "UC02: Xem danh sách sản phẩm và lọc" as UC02
        usecase "UC03: Xem chi tiết sản phẩm" as UC03
        usecase "UC04: Đăng ký tư vấn qua form" as UC04
        usecase "UC05: Đọc bài viết Blog" as UC05
        usecase "UC06: Đăng ký tham dự Event" as UC06
    }

    package "Inventory Module" {
        usecase "UC07: Nhập kho với Serial Number" as UC07
        usecase "UC08: Xuất kho theo Serial Number" as UC08
        usecase "UC09: Chuyển kho nội bộ" as UC09
        usecase "UC10: Tra cứu lịch sử Serial Number" as UC10
        usecase "UC11: Kiểm kê kho" as UC11
        usecase "UC13: Xem báo cáo tồn kho" as UC13
    }

    package "CRM Module" {
        usecase "UC12: Quản lý pipeline CRM" as UC12
    }

    KH --> UC01
    KH --> UC02
    KH --> UC03
    KH --> UC04
    KH --> UC05
    KH --> UC06

    NV_Kho --> UC07
    NV_Kho --> UC08
    NV_Kho --> UC09
    NV_Kho --> UC10
    NV_Kho --> UC11
    NV_Kho --> UC13

    NV_Sales --> UC12
    UC04 ..> UC12 : Tạo Lead tự động
```

## 4. Danh sách Use Case Chi Tiết

**UC01: Xem trang chủ website**
- Actor: Khách hàng
- Mô tả: Khách truy cập trang chủ, xem thông tin dịch vụ
- Tiền điều kiện: Odoo Website đang chạy, trang đã Published
- Luồng chính:
  1. Khách gõ URL vào trình duyệt
  2. Hệ thống hiển thị trang chủ với Hero, dịch vụ, sản phẩm nổi bật
  3. Khách đọc thông tin
- Kết quả: Khách hiểu về doanh nghiệp và dịch vụ

**UC02: Xem danh sách sản phẩm và lọc**
- Actor: Khách hàng
- Mô tả: Khách duyệt các danh mục sản phẩm (Thiết bị mạng, Phụ kiện, Máy tính...)
- Tiền điều kiện: Các sản phẩm đã được đăng lên website
- Kết quả: Khách tìm thấy sản phẩm mong muốn.

**UC03: Xem chi tiết sản phẩm**
- Actor: Khách hàng
- Mô tả: Khách xem thông tin chi tiết một sản phẩm cụ thể.
- Tiền điều kiện: Khách đã truy cập vào trang sản phẩm.
- Kết quả: Khách nắm rõ thông số và giá cả sản phẩm.

**UC04: Đăng ký tư vấn qua form**
- Actor: Khách hàng
- Mô tả: Khách điền thông tin (Tên, Email, SĐT) để yêu cầu tư vấn.
- Tiền điều kiện: Module CRM đã được kết nối với Website form.
- Kết quả: Thông tin được gửi đi, màn hình cảm ơn xuất hiện, và hệ thống CRM tự động nhận Lead.

**UC05: Đọc bài viết Blog**
- Actor: Khách hàng
- Mô tả: Khách duyệt và đọc tin tức công nghệ trên Blog.
- Kết quả: Khách nhận được thông tin hữu ích.

**UC06: Đăng ký tham dự Event**
- Actor: Khách hàng
- Mô tả: Khách đăng ký tham gia các sự kiện do công ty tổ chức.
- Tiền điều kiện: Module Events đã kích hoạt và có sự kiện đang mở.
- Kết quả: Khách đăng ký thành công và nhận email xác nhận.

**UC07: Nhập kho với Serial Number**
- Actor: Nhân viên Kho
- Mô tả: Nhân viên nhận hàng vào kho và gán mã Serial duy nhất cho từng mặt hàng.
- Tiền điều kiện: Sản phẩm được cấu hình "Tracking by Unique Serial Number".
- Kết quả: Số lượng tồn kho tăng lên cùng với danh sách Serial hợp lệ.

**UC08: Xuất kho theo Serial Number**
- Actor: Nhân viên Kho
- Mô tả: Nhân viên tạo phiếu xuất kho để giao hàng.
- Kết quả: Tồn kho giảm xuống, Serial được ghi nhận đã xuất khỏi kho.

**UC09: Chuyển kho nội bộ**
- Actor: Nhân viên Kho
- Mô tả: Chuyển hàng giữa các kho hoặc vị trí lưu trữ (Location) nội bộ.
- Kết quả: Hàng hóa (cùng Serial) di chuyển thành công tới vị trí đích.

**UC10: Tra cứu lịch sử Serial Number**
- Actor: Nhân viên Kho
- Mô tả: Sử dụng tính năng Traceability để xem toàn bộ vòng đời của một Serial (từ lúc nhập đến xuất).
- Kết quả: Hiển thị đầy đủ đường đi của Serial.

**UC11: Kiểm kê kho**
- Actor: Nhân viên Kho
- Mô tả: Cập nhật lại số lượng tồn kho thực tế nếu có sai lệch.
- Kết quả: Số lượng kho trên hệ thống khớp với kho thực tế.

**UC12: Quản lý pipeline CRM**
- Actor: Nhân viên Sales
- Mô tả: Quản lý các cơ hội kinh doanh trên giao diện Kanban, kéo thả giữa các bước.
- Kết quả: Trạng thái của Lead/Opportunity được cập nhật, kích hoạt các Activity tự động.

**UC13: Xem báo cáo tồn kho**
- Actor: Nhân viên Kho
- Mô tả: Xuất và xem các báo cáo tổng quan về số lượng tồn kho.
- Kết quả: Báo cáo hiển thị chính xác và chi tiết.

## 5. Yêu cầu phi chức năng

| Yêu cầu      | Mô tả                      | Tiêu chí đo lường                       |
| ------------ | -------------------------- | --------------------------------------- |
| Performance  | Trang load nhanh           | < 3 giây trên kết nối thông thường      |
| Responsive   | Hiển thị trên mọi thiết bị | Không lỗi layout ở 375px, 768px, 1366px |
| Availability | Hệ thống ổn định           | Không crash trong 2 giờ demo liên tục   |
| Data Backup  | Bảo vệ dữ liệu             | Backup tự động mỗi ngày, restore được   |
| Security     | Phân quyền người dùng      | Admin/Staff/Public có quyền riêng biệt  |

## 6. Ràng buộc hệ thống

- Phạm vi: chỉ Phase 1, không tích hợp thanh toán
- Môi trường: chạy local, không deploy production
- Dữ liệu: dùng dữ liệu demo, không dữ liệu thật
- Ngôn ngữ: tiếng Việt (giao diện website), tiếng Anh (backend Odoo)
