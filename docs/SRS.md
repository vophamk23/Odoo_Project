# Tài liệu Phân tích Yêu cầu Hệ thống (SRS)

**Dự án:** VoPC-CMCTS Phase 1  
**Phiên bản:** 1.0  
**Ngày lập:** 09/06/2026  
**Nhóm thực hiện:** Phase1-team  
**GitHub:** https://github.com/Phase1-team/VoPC-cmcts

---

## Mục lục

1. [Bối cảnh dự án](#1-bối-cảnh-dự-án)
2. [Công nghệ & Môi trường](#2-công-nghệ--môi-trường)
3. [Yêu cầu hệ thống](#3-yêu-cầu-hệ-thống)
4. [Sơ đồ Use Case & Đặc tả chi tiết](#4-sơ-đồ-use-case--đặc-tả-chi-tiết)
5. [Bảng tổng hợp yêu cầu chức năng](#5-bảng-tổng-hợp-yêu-cầu-chức-năng)

---

## 1. Bối cảnh dự án

### 1.1 Giới thiệu đề tài

Trong thời đại chuyển đổi số, việc quản lý rời rạc giữa các khâu bán hàng, tiếp thị và kho bãi gây ra nhiều khó khăn cho các doanh nghiệp, đặc biệt là các doanh nghiệp phân phối thiết bị công nghệ cao có giá trị lớn và cần theo dõi bảo hành theo Serial Number.

Dự án **VoPC-CMCTS Phase 1** triển khai hệ thống quản trị doanh nghiệp toàn diện dựa trên nền tảng **Odoo 18**, lấy cảm hứng từ mô hình kinh doanh của công ty công nghệ thực tế [cmcts.com.vn](https://cmcts.com.vn). Dự án tích hợp chặt chẽ quy trình từ khi khách hàng tiếp cận website, để lại thông tin tư vấn, cho đến khi nhân viên chốt sale và xuất kho giao hàng.

### 1.2 Mục tiêu, phạm vi và giới hạn

**Mục tiêu:**

- Xây dựng hệ thống ERP vận hành trơn tru các luồng dữ liệu cốt lõi của doanh nghiệp
- Tự động hóa quy trình chăm sóc khách hàng (CRM) và quản lý hàng hóa chính xác đến từng đơn vị sản phẩm (Inventory by Serial Number)

**Phạm vi:**

- **Website E-commerce:** Giới thiệu công ty, sản phẩm, đăng ký tư vấn, Blog, Sự kiện
- **Quản lý Kho (Inventory — Trọng tâm chính):** Theo dõi hàng hóa nhập, xuất, luân chuyển nội bộ bằng Unique Serial Number, kiểm kê kho
- **CRM:** Quản lý pipeline cơ hội kinh doanh, tự động tạo Lead từ Website form, quản lý khách hàng thân thiết

**Giới hạn (Phase 1):**

- Không tích hợp cổng thanh toán trực tuyến (Payment Gateways)
- Không triển khai phân hệ Kế toán (Accounting), Hóa đơn điện tử hay Nhân sự (HR)
- Hệ thống triển khai trên môi trường Localhost với dữ liệu giả lập (Demo data)

### 1.3 Stakeholders và vai trò

| Stakeholder               | Vai trò                    | Quyền hạn & Trách nhiệm                                                                 |
| ------------------------- | -------------------------- | --------------------------------------------------------------------------------------- |
| **Quản trị viên (Admin)** | Quản trị hệ thống          | Toàn quyền cài đặt, cấu hình Odoo, phân quyền người dùng và duyệt báo cáo cấp cao       |
| **Khách hàng (Customer)** | Người dùng cuối (End-user) | Truy cập Website (Public), xem sản phẩm, đọc tin tức, gửi yêu cầu tư vấn qua form       |
| **Nhân viên Kho**         | Quản lý vật tư, hàng hóa   | Tạo phiếu nhập/xuất/chuyển kho, ghi nhận Serial Number, kiểm kê và xuất báo cáo tồn kho |
| **Nhân viên Sales**       | Chăm sóc khách hàng        | Quản lý Leads/Opportunities trong CRM, kéo thả pipeline, cập nhật trạng thái tư vấn     |

### 1.4 User Stories

| ID    | Vai trò         | Mong muốn                                                | Mục đích                                                      |
| ----- | --------------- | -------------------------------------------------------- | ------------------------------------------------------------- |
| US-01 | Khách hàng      | Xem danh sách thiết bị theo danh mục                     | Tìm kiếm sản phẩm phù hợp dễ dàng                             |
| US-02 | Khách hàng      | Điền form đăng ký tư vấn trực tuyến                      | Nhận hỗ trợ từ nhân viên kinh doanh                           |
| US-03 | Nhân viên Kho   | Gán Serial Number duy nhất cho từng thiết bị nhập kho    | Quản lý chính xác từng sản phẩm, phục vụ truy vết và bảo hành |
| US-04 | Nhân viên Kho   | Hệ thống cảnh báo khi nhập trùng Serial                  | Tránh sai sót dữ liệu                                         |
| US-05 | Nhân viên Kho   | Xem báo cáo truy vết (Traceability) của một Serial       | Biết sản phẩm đã đi từ phiếu nhập nào đến phiếu xuất nào      |
| US-06 | Nhân viên Sales | Hệ thống tự động tạo Lead khi khách submit form          | Không bỏ lỡ khách hàng tiềm năng nào                          |
| US-07 | Nhân viên Sales | Hệ thống tự động tạo Activity nhắc việc khi chuyển stage | Không quên liên hệ lại với khách đúng hạn                     |

---

## 2. Công nghệ & Môi trường

### 2.1 Tech Stack

| Thành phần                | Công nghệ                         | Phiên bản |
| ------------------------- | --------------------------------- | --------- |
| Nền tảng ERP              | Odoo                              | 18.0      |
| Ngôn ngữ backend          | Python                            | 3.10+     |
| Database                  | PostgreSQL                        | 14+       |
| Frontend                  | Odoo Website Builder + Custom CSS | —         |
| Triển khai                | Docker hoặc Ubuntu bare metal     | —         |
| Quản lý source            | Git + GitHub                      | —         |
| Công cụ thiết kế tài liệu | draw.io, dbdiagram.io             | —         |

### 2.2 Môi trường triển khai

| Môi trường              | Mô tả                            | URL                   |
| ----------------------- | -------------------------------- | --------------------- |
| **Development (Local)** | Máy tính cá nhân từng thành viên | http://localhost:8069 |
| **Demo (Shared)**       | Máy chủ chung cho cả nhóm demo   | Cấu hình sau          |

### 2.3 Tài khoản hệ thống

| Loại tài khoản  | Username      | Password     | Quyền                      |
| --------------- | ------------- | ------------ | -------------------------- |
| Quản trị viên   | `admin`       | `admin`      | Administrator (toàn quyền) |
| Nhân viên Kho   | `kho_staff`   | Cấu hình sau | Inventory User             |
| Nhân viên Sales | `sales_staff` | Cấu hình sau | CRM User                   |

> ⚠️ **Lưu ý:** Tài khoản `admin/admin` chỉ dùng cho môi trường dev/demo, không dùng cho production.

### 2.4 Cấu trúc GitHub repo

```
VoPC-cmcts/
├── main/           ← code ổn định, đã test
├── develop/        ← tổng hợp code từ các thành viên
├── feature/*       ← mỗi thành viên làm 1 nhánh riêng
└── backup/         ← chứa file backup database (.sql.gz)
```

---

## 3. Yêu cầu hệ thống

### 3.1 Yêu cầu chức năng (Functional Requirements)

#### Nhóm Website (FR-W)

| Mã     | Mô tả yêu cầu                                                                   | Độ ưu tiên |
| ------ | ------------------------------------------------------------------------------- | ---------- |
| FR-W01 | Hiển thị trang chủ với Hero Banner, giới thiệu dịch vụ và sản phẩm nổi bật      | Cao        |
| FR-W02 | Hiển thị danh sách sản phẩm E-commerce có phân chia danh mục, tìm kiếm và lọc   | Cao        |
| FR-W03 | Cung cấp Form Đăng ký tư vấn với các trường bắt buộc: Tên, Email, Số điện thoại | Cao        |
| FR-W04 | Hiển thị trang About Us, Blog tin tức công nghệ, Danh sách Sự kiện (Event)      | Trung bình |
| FR-W05 | Trang Contact Us: form liên hệ, bản đồ và thông tin liên lạc                    | Trung bình |
| FR-W06 | Giao diện responsive trên mobile, tablet và desktop                             | Trung bình |

#### Nhóm Quản lý Kho (FR-I) — Trọng tâm

| Mã     | Mô tả yêu cầu                                                               | Độ ưu tiên |
| ------ | --------------------------------------------------------------------------- | ---------- |
| FR-I01 | Cấu hình danh mục sản phẩm với tracking theo Unique Serial Number           | Cao        |
| FR-I02 | Tạo phiếu Nhập kho (Receipt) yêu cầu nhập Serial Number cho từng sản phẩm   | Cao        |
| FR-I03 | Tạo phiếu Xuất kho (Delivery) bắt buộc chọn Serial Number đang có trong kho | Cao        |
| FR-I04 | Tạo phiếu Chuyển kho nội bộ (Internal Transfer) giữa các vị trí             | Trung bình |
| FR-I05 | Truy xuất nguồn gốc Serial Number (Traceability) từ nhập đến xuất           | Cao        |
| FR-I06 | Kiểm kê kho (Inventory Adjustment) đối chiếu số liệu thực tế vs hệ thống    | Trung bình |
| FR-I07 | Báo cáo tồn kho thời gian thực, lọc theo kho/danh mục, xuất Excel           | Trung bình |
| FR-I08 | Cảnh báo khi nhập trùng Serial Number đã tồn tại trong hệ thống             | Cao        |
| FR-I09 | Dashboard kho: biểu đồ nhập/xuất theo tháng, widget tổng tồn kho            | Thấp       |

#### Nhóm CRM (FR-C)

| Mã     | Mô tả yêu cầu                                                                                 | Độ ưu tiên |
| ------ | --------------------------------------------------------------------------------------------- | ---------- |
| FR-C01 | Cấu hình Pipeline tối thiểu 6 bước: Tiếp nhận → Tư vấn → Báo giá → Đàm phán → Chốt → Thất bại | Cao        |
| FR-C02 | Tự động tạo Lead (Auto Lead Generation) từ Web Form gửi về hệ thống CRM                       | Cao        |
| FR-C03 | Phân loại khách hàng bằng Tags (VIP, Thân thiết, Tiềm năng, Mới)                              | Trung bình |
| FR-C04 | Tự động tạo Activity nhắc nhở nhân viên theo từng bước pipeline                               | Trung bình |
| FR-C05 | Gửi email template tự động theo từng bước chuyển stage                                        | Trung bình |

### 3.2 Yêu cầu phi chức năng (Non-Functional Requirements)

| Loại                 | Yêu cầu cụ thể                                                                                           |
| -------------------- | -------------------------------------------------------------------------------------------------------- |
| **Hiệu suất**        | Trang website tải dưới 3 giây. Xử lý phiếu nhập/xuất kho dưới 2 giây                                     |
| **Khả dụng**         | Giao diện website responsive từ 375px trở lên (mobile, tablet, desktop)                                  |
| **Bảo mật**          | Phân quyền nghiêm ngặt: Nhân viên Kho không xem được CRM và ngược lại. Khách vãng lai chỉ xem Public web |
| **Sao lưu**          | Database PostgreSQL được backup tự động, có thể restore khi mất dữ liệu                                  |
| **Dữ liệu**          | Serial Number phải là duy nhất trên toàn hệ thống, không cho phép trùng lặp                              |
| **Khả năng mở rộng** | Cấu trúc module Odoo cho phép bổ sung phân hệ Kế toán, HR ở Phase 2 mà không ảnh hưởng dữ liệu hiện tại  |

---

## 4. Sơ đồ Use Case & Đặc tả chi tiết

### 4.1 Sơ đồ Use Case tổng quan

```
┌─────────────────────────────────────────────────────────────────┐
│                        HỆ THỐNG VoPC-CMCTS                      │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │  WEBSITE MODULE  │  │ INVENTORY MODULE  │  │  CRM MODULE   │  │
│  │                  │  │                   │  │               │  │
│  │ UC01 Xem SP      │  │ UC03 Nhập kho     │  │ UC08 Pipeline │  │
│  │ UC02 Đăng ký TV  │  │ UC04 Xuất kho     │  │ UC09 Lead &   │  │
│  │                  │  │ UC05 Chuyển kho   │  │      Activity │  │
│  │                  │  │ UC06 Traceability │  │ UC10 Báo giá  │  │
│  │                  │  │ UC07 Báo cáo kho  │  │               │  │
│  │                  │  │ UC11 Quản lý SP   │  │               │  │
│  └──────────────────┘  └──────────────────┘  └───────────────┘  │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                     SYSTEM ADMIN                           │   │
│  │                  UC12 Phân quyền User                      │   │
│  └───────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

Actor → Use Case:
👤 Khách hàng    → UC01, UC02
👷 NV Kho        → UC03, UC04, UC05, UC06, UC07, UC11
💼 NV Sales      → UC08, UC09, UC10
🔧 Admin         → UC11, UC12, UC07

Liên kết đặc biệt:
UC02 ──[include]──▶ UC09  (Form website tự động tạo Lead)
UC10 ──[trigger]──▶ UC04  (Xác nhận đơn hàng kích hoạt xuất kho)
```

### 4.2 Đặc tả Use Case chi tiết

---

#### UC01 — Xem & Tìm kiếm Sản phẩm

| Thành phần           | Chi tiết                                                                                                                                       |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usecase ID**       | UC01                                                                                                                                           |
| **Tên**              | Xem & Tìm kiếm Sản phẩm                                                                                                                        |
| **Mô tả**            | Khách hàng duyệt danh mục, tìm kiếm và xem chi tiết thông số kỹ thuật sản phẩm trên Website                                                    |
| **Actor**            | Khách hàng                                                                                                                                     |
| **Phạm vi**          | Website (E-commerce)                                                                                                                           |
| **Điều kiện trước**  | Website đang hoạt động. Sản phẩm đã được cấu hình hiển thị (Published) với đầy đủ ảnh, giá                                                     |
| **Luồng chính**      | 1. Khách hàng truy cập vào trang danh sách sản phẩm tại đường dẫn `/shop`.<br>2. Ở thanh điều hướng bên trái, khách hàng nhấn chọn danh mục sản phẩm mong muốn.<br>3. Hệ thống tự động xử lý và hiển thị danh sách các thiết bị tương ứng.<br>4. Khách hàng nhấp chuột vào một sản phẩm cụ thể để xem cấu hình chi tiết, mức giá và trạng thái tồn kho. |
| **Luồng thay thế**   | Bước 2: Khách gõ từ khóa vào thanh Search thay vì chọn danh mục                                                                                |
| **Luồng ngoại lệ**   | Không tìm thấy sản phẩm → Hiển thị thông báo "Không tìm thấy sản phẩm nào phù hợp"                                                             |
| **Điều kiện sau**    | Khách nắm được thông tin sản phẩm, có thể tiến hành đăng ký tư vấn                                                                             |
| **Yêu cầu đặc biệt** | Trang tải dưới 3 giây, responsive tốt trên điện thoại                                                                                          |

---

#### UC02 — Đăng ký tư vấn qua form

| Thành phần           | Chi tiết                                                                                                                                                         |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usecase ID**       | UC02                                                                                                                                                             |
| **Tên**              | Đăng ký tư vấn qua form                                                                                                                                          |
| **Mô tả**            | Khách hàng để lại thông tin (Tên, SĐT, Email, Nhu cầu) để nhân viên Sales liên hệ tư vấn                                                                         |
| **Actor**            | Khách hàng                                                                                                                                                       |
| **Phạm vi**          | Website + CRM (tích hợp)                                                                                                                                         |
| **Điều kiện trước**  | Website hoạt động bình thường. Form đã được cấu hình kết nối CRM                                                                                                 |
| **Luồng chính**      | 1. Khách hàng truy cập vào trang liên hệ tại đường dẫn `/tu-van`.<br>2. Khách hàng điền đầy đủ thông tin vào form (Họ tên, Số điện thoại, Email, Nội dung cần hỗ trợ).<br>3. Khách hàng nhấn nút "Gửi thông tin".<br>4. Hệ thống ghi nhận yêu cầu và hiển thị màn hình Cảm ơn.<br>5. Hệ thống CRM tự động khởi tạo một Lead mới chứa thông tin vừa nhập. |
| **Luồng thay thế**   | Không có                                                                                                                                                         |
| **Luồng ngoại lệ**   | Bỏ trống trường bắt buộc (Email) → Hiển thị cảnh báo đỏ, không cho submit                                                                                        |
| **Điều kiện sau**    | Lead mới xuất hiện ở stage "Tiếp nhận yêu cầu" trong CRM. Email xác nhận gửi cho khách                                                                           |
| **Yêu cầu đặc biệt** | Form có chống spam cơ bản. Email xác nhận gửi trong vòng 1 phút                                                                                                  |

---

#### UC03 — Nhập kho theo Serial Number

| Thành phần           | Chi tiết                                                                                                                                             |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usecase ID**       | UC03                                                                                                                                                 |
| **Tên**              | Nhập kho theo Serial Number                                                                                                                          |
| **Mô tả**            | Nhân viên kho nhận hàng từ nhà cung cấp và gán mã Serial duy nhất cho từng thiết bị                                                                  |
| **Actor**            | Nhân viên Kho                                                                                                                                        |
| **Phạm vi**          | Inventory                                                                                                                                            |
| **Điều kiện trước**  | Sản phẩm đã được cấu hình "Tracking by Unique Serial Number"                                                                                         |
| **Luồng chính**      | 1. Nhân viên Kho đăng nhập và tạo một phiếu Nhập kho (Receipt) mới trên hệ thống.<br>2. Chọn tên Nhà cung cấp và thêm các dòng sản phẩm cần nhập vào phiếu.<br>3. Mở chi tiết hoạt động (Detailed Operations) để nhập hoặc quét mã Serial Number duy nhất cho từng sản phẩm.<br>4. Nhân viên kiểm tra lại thông tin và bấm nút "Validate" để hoàn tất.<br>5. Số lượng tồn kho tự động tăng lên và các mã Serial vừa nhập chính thức được kích hoạt tại kho đích. |
| **Luồng thay thế**   | Import hàng loạt Serial bằng file Excel thay vì nhập tay                                                                                             |
| **Luồng ngoại lệ**   | Nhập Serial đã tồn tại → Hệ thống báo lỗi Duplicate, chặn Validate                                                                                   |
| **Điều kiện sau**    | Tồn kho tăng đúng số lượng. Serial được kích hoạt và nằm ở kho đích                                                                                  |
| **Yêu cầu đặc biệt** | Mỗi Serial phải là duy nhất trên toàn hệ thống                                                                                                       |

---

#### UC04 — Xuất kho theo Serial Number

| Thành phần           | Chi tiết                                                                                                                                     |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usecase ID**       | UC04                                                                                                                                         |
| **Tên**              | Xuất kho theo Serial Number                                                                                                                  |
| **Mô tả**            | Nhân viên kho tạo phiếu xuất kho giao sản phẩm cho khách, chọn đúng Serial thực tế sẽ giao                                                   |
| **Actor**            | Nhân viên Kho                                                                                                                                |
| **Phạm vi**          | Inventory                                                                                                                                    |
| **Điều kiện trước**  | Tồn kho sản phẩm > 0, Serial cần xuất đang có trong kho (On Hand)                                                                            |
| **Luồng chính**      | 1. Nhân viên Kho khởi tạo một phiếu Xuất kho (Delivery Order) trên hệ thống.<br>2. Điền thông tin đối tác nhận hàng và chọn các sản phẩm cần xuất.<br>3. Trong danh sách hàng có sẵn (On Hand), nhân viên chọn đích danh các Serial Number thực tế sẽ được giao.<br>4. Nhân viên bấm "Validate" để xác nhận xuất kho.<br>5. Tồn kho sản phẩm giảm xuống và các mã Serial tương ứng được đánh dấu là đã xuất. |
| **Luồng thay thế**   | Nhấn "Auto Assign" để Odoo tự chọn Serial cũ nhất (FIFO)                                                                                     |
| **Luồng ngoại lệ**   | Serial không có trong kho → Odoo cảnh báo và chặn xuất kho                                                                                   |
| **Điều kiện sau**    | Tồn kho giảm đúng số lượng. Serial được đánh dấu đã giao cho khách hàng                                                                      |
| **Yêu cầu đặc biệt** | Không có                                                                                                                                     |

---

#### UC05 — Chuyển kho nội bộ

| Thành phần           | Chi tiết                                                                                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usecase ID**       | UC05                                                                                                                                                          |
| **Tên**              | Chuyển kho nội bộ (Internal Transfer)                                                                                                                         |
| **Mô tả**            | Di chuyển sản phẩm cùng Serial từ vị trí này sang vị trí khác trong cùng công ty                                                                              |
| **Actor**            | Nhân viên Kho                                                                                                                                                 |
| **Phạm vi**          | Inventory                                                                                                                                                     |
| **Điều kiện trước**  | Hàng hóa có sẵn tại vị trí nguồn (Source Location)                                                                                                            |
| **Luồng chính**      | 1. Nhân viên Kho khởi tạo phiếu Chuyển kho nội bộ (Internal Transfer).<br>2. Chỉ định rõ Vị trí nguồn (Source Location) và Vị trí đích (Destination Location).<br>3. Thêm sản phẩm cần chuyển và lựa chọn đích danh các mã Serial Number.<br>4. Kiểm tra số lượng và nhấn "Validate" để hoàn tất điều chuyển.<br>5. Các mã Serial được chọn sẽ biến mất ở vị trí nguồn và cập nhật trạng thái có mặt tại vị trí đích. |
| **Luồng thay thế**   | Không có                                                                                                                                                      |
| **Luồng ngoại lệ**   | Vị trí đích bị khóa hoặc không đủ quyền → Hệ thống báo lỗi, không cho thực hiện                                                                               |
| **Điều kiện sau**    | Serial biến mất ở vị trí nguồn, xuất hiện tại vị trí đích. Tổng tồn kho toàn công ty không đổi                                                                |
| **Yêu cầu đặc biệt** | Không có                                                                                                                                                      |

---

#### UC06 — Truy vết Serial Number (Traceability)

| Thành phần           | Chi tiết                                                                                                                                                                    |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usecase ID**       | UC06                                                                                                                                                                        |
| **Tên**              | Truy vết Serial Number (Traceability)                                                                                                                                       |
| **Mô tả**            | Xem toàn bộ hành trình của một Serial từ khi nhập kho đến khi xuất bán — rất quan trọng khi làm bảo hành                                                                    |
| **Actor**            | Nhân viên Kho, Admin                                                                                                                                                        |
| **Phạm vi**          | Inventory                                                                                                                                                                   |
| **Điều kiện trước**  | Serial Number đã tồn tại trong hệ thống                                                                                                                                     |
| **Luồng chính**      | 1. Người dùng truy cập vào menu Lots/Serial Numbers trong phân hệ Quản lý Kho.<br>2. Điền mã Serial Number cần kiểm tra vào ô tìm kiếm.<br>3. Mở bản ghi chi tiết của Serial đó và nhấn vào nút "Traceability" (Truy vết).<br>4. Hệ thống ngay lập tức hiển thị biểu đồ cây liệt kê toàn bộ lịch sử các phiếu nhập, xuất, chuyển kho liên quan đến Serial này. |
| **Luồng thay thế**   | Không có                                                                                                                                                                    |
| **Luồng ngoại lệ**   | Nhập sai mã Serial → Danh sách trống                                                                                                                                        |
| **Điều kiện sau**    | Người dùng xem được đầy đủ lịch sử và lấy được mã phiếu xuất để kiểm tra bảo hành                                                                                           |
| **Yêu cầu đặc biệt** | Cây truy vết phải ghi rõ ngày giờ của từng lần dịch chuyển                                                                                                                  |

---

#### UC07 — Báo cáo tồn kho

| Thành phần           | Chi tiết                                                                                                                            |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Usecase ID**       | UC07                                                                                                                                |
| **Tên**              | Báo cáo tồn kho                                                                                                                     |
| **Mô tả**            | Xuất báo cáo tổng hợp về lượng hàng và giá trị tồn kho tại các vị trí cụ thể                                                        |
| **Actor**            | Nhân viên Kho, Admin                                                                                                                |
| **Phạm vi**          | Inventory                                                                                                                           |
| **Điều kiện trước**  | User được cấp quyền xem Báo cáo (Inventory Report)                                                                                  |
| **Luồng chính**      | 1. Người dùng truy cập vào tính năng Inventory Report trong phần Báo cáo của Odoo.<br>2. Sử dụng bộ lọc (Filter) và nhóm (Group By) để thu hẹp phạm vi theo sản phẩm, danh mục hoặc vị trí kho cụ thể.<br>3. Màn hình hiển thị số lượng tồn kho và giá trị hàng hóa theo thời gian thực.<br>4. Nhấn nút Export để kết xuất dữ liệu ra file Excel phục vụ cho việc báo cáo bên ngoài. |
| **Luồng thay thế**   | Chuyển chế độ xem sang Pivot hoặc Graph để phân tích trực quan                                                                      |
| **Luồng ngoại lệ**   | Không có                                                                                                                            |
| **Điều kiện sau**    | Có file Excel dữ liệu tồn kho chính xác để báo cáo                                                                                  |
| **Yêu cầu đặc biệt** | Dữ liệu phải là thời gian thực (Real-time)                                                                                          |

---

#### UC08 — Quản lý Pipeline CRM

| Thành phần           | Chi tiết                                                                                                                                                                     |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usecase ID**       | UC08                                                                                                                                                                         |
| **Tên**              | Quản lý Pipeline CRM                                                                                                                                                         |
| **Mô tả**            | Nhân viên Sales theo dõi và kéo thả Lead/Opportunity qua các bước trong quy trình bán hàng                                                                                   |
| **Actor**            | Nhân viên Sales                                                                                                                                                              |
| **Phạm vi**          | CRM                                                                                                                                                                          |
| **Điều kiện trước**  | Đã cấu hình các Stage: Tiếp nhận → Tư vấn → Báo giá → Đàm phán → Chốt / Thất bại                                                                                             |
| **Luồng chính**      | 1. Nhân viên Sales truy cập ứng dụng CRM và mở giao diện Pipeline dưới dạng bảng Kanban.<br>2. Hệ thống hiển thị danh sách các Cơ hội kinh doanh (Lead) đang được phân loại theo từng giai đoạn (Stage).<br>3. Nhân viên nắm giữ thẻ của một Lead và thực hiện thao tác Kéo - Thả (Drag & Drop) sang giai đoạn tiếp theo.<br>4. Hệ thống ghi nhận trạng thái mới và tự động tính toán lại tỷ lệ chốt thành công (Probability). |
| **Luồng thay thế**   | Đánh dấu Lead là "Won" hoặc "Lost" trực tiếp mà không cần qua hết các bước                                                                                                   |
| **Luồng ngoại lệ**   | Không có                                                                                                                                                                     |
| **Điều kiện sau**    | Lead thay đổi Stage. Xác suất thành công (Probability) tự động cập nhật. Activity nhắc việc tự tạo                                                                           |
| **Yêu cầu đặc biệt** | Giao diện Drag & Drop mượt mà                                                                                                                                                |

---

#### UC09 — Xử lý Lead & Activity tự động

| Thành phần           | Chi tiết                                                                                                                                                                                                                |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usecase ID**       | UC09                                                                                                                                                                                                                    |
| **Tên**              | Xử lý Lead & Activity tự động                                                                                                                                                                                           |
| **Mô tả**            | Nhận Lead từ website và thực hiện các tác vụ chăm sóc theo lịch nhắc nhở tự động                                                                                                                                        |
| **Actor**            | Nhân viên Sales                                                                                                                                                                                                         |
| **Phạm vi**          | CRM                                                                                                                                                                                                                     |
| **Điều kiện trước**  | Website Form đã kết nối CRM. Automated Actions tạo Activity đã được kích hoạt                                                                                                                                           |
| **Luồng chính**      | 1. Lead mới được hệ thống tự động đẩy vào cột "Tiếp nhận" ngay sau khi khách hàng điền form trên website.<br>2. Nhân viên mở chi tiết Lead và nhận được tác vụ (Activity) tự động nhắc nhở "Cần gọi điện tư vấn".<br>3. Nhân viên thực hiện cuộc gọi hỗ trợ, sau đó nhấn "Mark as Done" và nhập ghi chú nội dung đã trao đổi.<br>4. Nếu cần chăm sóc thêm, nhân viên tiếp tục chọn "Schedule Next Activity" để lên lịch hẹn lần sau. |
| **Luồng thay thế**   | Gửi email trực tiếp trong khung Log của Lead thay vì gọi điện                                                                                                                                                           |
| **Luồng ngoại lệ**   | Activity quá hạn → Hệ thống đổi màu cảnh báo sang Đỏ                                                                                                                                                                    |
| **Điều kiện sau**    | Lead được chăm sóc kịp thời. Lịch sử làm việc ghi nhận đầy đủ trong Log                                                                                                                                                 |
| **Yêu cầu đặc biệt** | Lịch sử Log không thể xóa để đảm bảo minh bạch                                                                                                                                                                          |

---

#### UC10 — Lập Báo giá và Đơn bán hàng

| Thành phần           | Chi tiết                                                                                                                                                                                |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usecase ID**       | UC10                                                                                                                                                                                    |
| **Tên**              | Lập Báo giá và Đơn bán hàng                                                                                                                                                             |
| **Mô tả**            | Nhân viên Sales tạo Báo giá từ Lead thành công, gửi khách và chốt thành Sales Order                                                                                                     |
| **Actor**            | Nhân viên Sales                                                                                                                                                                         |
| **Phạm vi**          | CRM & Sales                                                                                                                                                                             |
| **Điều kiện trước**  | Opportunity đã đến giai đoạn "Báo giá" hoặc "Chốt"                                                                                                                                      |
| **Luồng chính**      | 1. Nhân viên Sales mở chi tiết một Cơ hội kinh doanh (Opportunity) đã đến giai đoạn chốt.<br>2. Nhấn nút "New Quotation" để khởi tạo một Báo giá mới gắn liền với khách hàng này.<br>3. Thêm các sản phẩm, tùy chỉnh số lượng, đơn giá và áp dụng chiết khấu (nếu có).<br>4. Nhấn "Send by Email" để gửi ngay bản PDF Báo giá cho khách hàng tham khảo.<br>5. Sau khi khách đồng ý mua, nhấn "Confirm" để chính thức chuyển Báo giá thành Đơn bán hàng (Sales Order). |
| **Luồng thay thế**   | In Báo giá ra PDF đưa trực tiếp cho khách thay vì gửi email                                                                                                                             |
| **Luồng ngoại lệ**   | Thêm sản phẩm hết hàng vào báo giá → Odoo hiện cảnh báo màu đỏ                                                                                                                          |
| **Điều kiện sau**    | Sales Order được tạo. Hệ thống tự động sinh phiếu Xuất kho (Delivery) ở trạng thái "Chờ xử lý"                                                                                          |
| **Yêu cầu đặc biệt** | Mẫu PDF Báo giá có logo và thông tin liên hệ của công ty                                                                                                                                |

---

#### UC11 — Quản lý danh mục Sản phẩm

| Thành phần           | Chi tiết                                                                                                                                                                       |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Usecase ID**       | UC11                                                                                                                                                                           |
| **Tên**              | Quản lý danh mục Sản phẩm                                                                                                                                                      |
| **Mô tả**            | Tạo mới và cấu hình thông tin cho các sản phẩm thiết bị công nghệ chuẩn bị kinh doanh                                                                                          |
| **Actor**            | Admin, Nhân viên Kho (có quyền Quản lý)                                                                                                                                        |
| **Phạm vi**          | Inventory                                                                                                                                                                      |
| **Điều kiện trước**  | Đăng nhập với quyền Admin hoặc Quản lý Kho                                                                                                                                     |
| **Luồng chính**      | 1. Người quản lý truy cập danh mục Products và chọn nút "Create" để khởi tạo sản phẩm mới.<br>2. Điền đầy đủ thông tin cơ bản: Tên sản phẩm, tải ảnh minh họa, mức giá và danh mục (Category).<br>3. Chuyển sang tab Inventory, tích chọn phương thức Tracking là "By Unique Serial Number" để kích hoạt tính năng truy vết.<br>4. Đảm bảo thuộc tính Product Type được đặt là "Storable Product" (Hàng lưu kho).<br>5. Nhấn "Save" để lưu lại cấu hình sản phẩm. |
| **Luồng thay thế**   | Import hàng loạt sản phẩm bằng file Excel                                                                                                                                      |
| **Luồng ngoại lệ**   | Quên chọn Serial Tracking → Nhân viên kho sau này không thể nhập Serial cho hàng hóa đó                                                                                        |
| **Điều kiện sau**    | Sản phẩm sẵn sàng để nhập kho và đăng bán trên Website                                                                                                                         |
| **Yêu cầu đặc biệt** | Bắt buộc đặt loại "Storable Product" cho tất cả thiết bị cần lưu kho                                                                                                           |

---

#### UC12 — Quản lý Phân quyền Người dùng

| Thành phần           | Chi tiết                                                                                                                                                                                                             |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Usecase ID**       | UC12                                                                                                                                                                                                                 |
| **Tên**              | Quản lý Phân quyền Người dùng                                                                                                                                                                                        |
| **Mô tả**            | Admin tạo tài khoản cho nhân viên và phân quyền truy cập nghiêm ngặt giữa các phòng ban                                                                                                                              |
| **Actor**            | Admin                                                                                                                                                                                                                |
| **Phạm vi**          | Settings                                                                                                                                                                                                             |
| **Điều kiện trước**  | Đăng nhập bằng tài khoản Administrator cao nhất                                                                                                                                                                      |
| **Luồng chính**      | 1. Quản trị viên (Admin) truy cập vào đường dẫn Settings > Users & Companies > Users và nhấn "Create".<br>2. Khai báo các thông tin bắt buộc gồm Tên nhân viên và Email dùng để đăng nhập.<br>3. Tại phần Access Rights, thiết lập phân quyền nghiêm ngặt: Nhân viên Kho chỉ được quyền thao tác Inventory, Nhân viên Sales chỉ được thao tác CRM.<br>4. Nhấn "Send Invitation" để gửi email chứa đường dẫn cho phép nhân viên tự kích hoạt và đặt mật khẩu cá nhân. |
| **Luồng thay thế**   | Admin tự đặt mật khẩu trực tiếp (Change Password) thay vì gửi email mời                                                                                                                                              |
| **Luồng ngoại lệ**   | Cấp quyền sai → Nhân viên có thể xem dữ liệu nhạy cảm của phòng ban khác                                                                                                                                             |
| **Điều kiện sau**    | Nhân viên đăng nhập được và chỉ thấy các app được phân quyền                                                                                                                                                         |
| **Yêu cầu đặc biệt** | Tài khoản Admin mặc định không bao giờ được phép xóa                                                                                                                                                                 |

---

## 5. Bảng tổng hợp yêu cầu chức năng

| Mã FR  | Mô tả                                            | Module    | UC liên quan | Ưu tiên |
| ------ | ------------------------------------------------ | --------- | ------------ | ------- |
| FR-W01 | Trang chủ Hero Banner, dịch vụ, sản phẩm nổi bật | Website   | UC01         | Cao     |
| FR-W02 | Danh sách sản phẩm, lọc danh mục, tìm kiếm       | Website   | UC01         | Cao     |
| FR-W03 | Form Đăng ký tư vấn (Tên, Email, SĐT bắt buộc)   | Website   | UC02         | Cao     |
| FR-W04 | Trang About Us, Blog, Event                      | Website   | —            | TB      |
| FR-W05 | Trang Contact Us: form, bản đồ, thông tin        | Website   | —            | TB      |
| FR-W06 | Responsive mobile/tablet/desktop                 | Website   | —            | TB      |
| FR-I01 | Cấu hình sản phẩm Tracking by Unique Serial      | Inventory | UC11         | Cao     |
| FR-I02 | Phiếu Nhập kho với Serial Number                 | Inventory | UC03         | Cao     |
| FR-I03 | Phiếu Xuất kho chọn Serial On Hand               | Inventory | UC04         | Cao     |
| FR-I04 | Phiếu Chuyển kho nội bộ                          | Inventory | UC05         | TB      |
| FR-I05 | Traceability toàn bộ vòng đời Serial             | Inventory | UC06         | Cao     |
| FR-I06 | Kiểm kê kho, điều chỉnh chênh lệch               | Inventory | —            | TB      |
| FR-I07 | Báo cáo tồn kho thời gian thực, xuất Excel       | Inventory | UC07         | TB      |
| FR-I08 | Cảnh báo nhập trùng Serial Number                | Inventory | UC03         | Cao     |
| FR-I09 | Dashboard kho: biểu đồ nhập/xuất                 | Inventory | —            | Thấp    |
| FR-C01 | Pipeline CRM 6 bước tư vấn thiết kế              | CRM       | UC08         | Cao     |
| FR-C02 | Auto Lead từ Web Form → CRM                      | CRM       | UC02, UC09   | Cao     |
| FR-C03 | Tag khách hàng: VIP, Thân thiết, Tiềm năng, Mới  | CRM       | —            | TB      |
| FR-C04 | Activity tự động nhắc việc theo stage            | CRM       | UC09         | TB      |
| FR-C05 | Email template tự động theo stage                | CRM       | UC09         | TB      |

---

_Tài liệu này được lưu tại: `/docs/SRS_VoPC_cmcts.md` trên GitHub repo_  
_Cập nhật lần cuối: 09/06/2026_
