# Tài liệu phân tích yêu cầu (SRS)

## 1. Bối cảnh dự án

### 1.1 Giới thiệu về đề tài
Trong thời đại chuyển đổi số, việc quản lý rời rạc giữa các khâu bán hàng, tiếp thị và kho bãi gây ra nhiều khó khăn cho các doanh nghiệp, đặc biệt là các doanh nghiệp phân phối thiết bị công nghệ cao (có giá trị lớn và cần theo dõi bảo hành theo Serial Number). 
Dự án **VoPC-CMCTS Phase 1** ra đời với mục đích mô phỏng và triển khai hệ thống quản trị doanh nghiệp toàn diện dựa trên nền tảng **Odoo 18**, lấy cảm hứng từ mô hình kinh doanh của công ty công nghệ thực tế (cmcts.com.vn). Dự án giúp tích hợp chặt chẽ quy trình từ khi khách hàng tiếp cận website, để lại thông tin tư vấn, cho đến quy trình nhân viên chốt sale và xuất kho giao hàng.

### 1.2 Mục tiêu, phạm vi và giới hạn dự án
**Mục tiêu:**
- Xây dựng một hệ thống ERP thu nhỏ nhưng vận hành trơn tru các luồng dữ liệu cốt lõi.
- Tự động hóa quy trình chăm sóc khách hàng (CRM) và quản lý hàng hóa chính xác đến từng đơn vị sản phẩm (Inventory by Serial Number).

**Phạm vi:**
- **Website E-commerce:** Giới thiệu công ty, sản phẩm, đăng ký tư vấn, Blog, Sự kiện.
- **Quản lý Kho (Inventory - Trọng tâm chính):** Theo dõi hàng hóa nhập, xuất, luân chuyển nội bộ bằng Unique Serial Number, kiểm kê kho.
- **CRM:** Quản lý cơ hội kinh doanh (Pipeline), tự động tạo Lead từ Website form, quản lý khách hàng thân thiết.

**Giới hạn dự án (Phase 1):**
- Không tích hợp các cổng thanh toán trực tuyến (Payment Gateways).
- Không triển khai các phân hệ Kế toán (Accounting), Hóa đơn điện tử hay Nhân sự (HR).
- Hệ thống được triển khai trên môi trường Localhost (Docker) với dữ liệu giả lập (Demo data).

### 1.3 Stakeholders và Vai trò
| Stakeholder | Vai trò trong hệ thống | Quyền hạn & Trách nhiệm |
| --- | --- | --- |
| **Quản trị viên (Admin)** | Trưởng dự án / Quản trị hệ thống | Có toàn quyền cài đặt, cấu hình Odoo, phân quyền người dùng và duyệt các báo cáo cấp cao. |
| **Khách hàng (Customer)** | Người dùng cuối (End-user) | Truy cập Website (Public), xem sản phẩm, đọc tin tức, và gửi yêu cầu tư vấn qua form. |
| **Nhân viên Kho (Inventory Staff)** | Quản lý vật tư và hàng hóa | Tạo phiếu nhập/xuất/chuyển kho, ghi nhận Serial Number, kiểm kê và xuất báo cáo tồn kho. |
| **Nhân viên Sales (Sales Rep)** | Chăm sóc khách hàng | Quản lý Leads/Opportunities trong CRM, kéo thả pipeline, cập nhật trạng thái tư vấn. |

### 1.4 User Stories
- **Là Khách hàng**, tôi muốn xem danh sách các thiết bị công nghệ theo danh mục để dễ dàng tìm kiếm sản phẩm phù hợp.
- **Là Khách hàng**, tôi muốn điền form Đăng ký tư vấn trực tuyến để nhận được sự hỗ trợ từ nhân viên kinh doanh.
- **Là Nhân viên Kho**, tôi muốn gán mã Serial Number duy nhất cho mỗi thiết bị nhập vào để quản lý chính xác từng sản phẩm (phục vụ truy vết và bảo hành sau này).
- **Là Nhân viên Kho**, tôi muốn hệ thống cảnh báo nếu tôi vô tình nhập trùng một mã Serial đã tồn tại trong kho để tránh sai sót dữ liệu.
- **Là Nhân viên Kho**, tôi muốn xem báo cáo truy vết (Traceability) của một Serial Number để biết nó đã đi từ phiếu nhập nào đến phiếu xuất nào.
- **Là Nhân viên Sales**, tôi muốn hệ thống CRM tự động tạo một Lead mới ngay khi khách hàng submit form trên Website để tôi không bỏ lỡ bất kỳ khách hàng tiềm năng nào.
- **Là Nhân viên Sales**, tôi muốn hệ thống tự động sinh ra tác vụ (Activity) "Gọi điện tư vấn" khi tôi chuyển một khách hàng sang giai đoạn mới để nhắc nhở tôi làm việc.

---

## 2. Yêu cầu hệ thống

### 2.1 Yêu cầu chức năng (Functional Requirements)

**Nhóm chức năng Website:**
- **FR-W01:** Hiển thị Trang chủ chuyên nghiệp với Hero Banner và danh sách dịch vụ nổi bật.
- **FR-W02:** Hiển thị danh sách sản phẩm E-commerce có phân chia danh mục (Thiết bị mạng, Phụ kiện, Máy tính...).
- **FR-W03:** Hệ thống cung cấp Form Đăng ký tư vấn (Contact Form) yêu cầu bắt buộc nhập Tên và Email.
- **FR-W04:** Hiển thị các trang thông tin tĩnh: About Us, Blog tin tức công nghệ, Danh sách Sự kiện (Event).

**Nhóm chức năng Quản lý Kho (Inventory) - Trọng tâm:**
- **FR-I01:** Quản lý danh mục Sản phẩm và Cấu hình theo dõi bằng Serial Number duy nhất (Tracking by Unique Serial Number).
- **FR-I02:** Chức năng Tạo phiếu Nhập kho (Receipt) yêu cầu quét/nhập Serial Number.
- **FR-I03:** Chức năng Tạo phiếu Xuất kho (Delivery) bắt buộc chọn Serial Number đang có sẵn (On Hand).
- **FR-I04:** Chức năng Chuyển kho nội bộ (Internal Transfer) luân chuyển Serial giữa các Vị trí (Locations).
- **FR-I05:** Truy xuất nguồn gốc Serial Number (Traceability) từ đầu đến cuối.
- **FR-I06:** Cập nhật số lượng tồn kho qua Kiểm kê kho (Inventory Adjustments) và xem báo cáo tồn kho thời gian thực.

**Nhóm chức năng CRM:**
- **FR-C01:** Cấu hình Pipeline tối thiểu 6 bước (Mới, Tiếp nhận yêu cầu, Đang tư vấn, Báo giá, Chốt hợp đồng, Thất bại).
- **FR-C02:** Tự động bắt Lead (Auto Lead Generation) từ Web Form đổ về hệ thống CRM.
- **FR-C03:** Phân loại khách hàng bằng Tags (Ví dụ: VIP, Thân thiết, Tiềm năng) và bộ lọc tìm kiếm.
- **FR-C04:** Tính năng Activities tự động nhắc nhở nhân viên (gọi điện, email) theo từng quy trình chốt sale.

### 2.2 Yêu cầu phi chức năng (Non-functional requirements)

| Loại yêu cầu | Chi tiết |
| --- | --- |
| **Hiệu suất (Performance)** | Thời gian tải các trang giao diện người dùng trên Website không vượt quá 3 giây. Thời gian xử lý phiếu xuất/nhập kho dưới 2 giây. |
| **Tính khả dụng (Usability)** | Giao diện Website phải tương thích (Responsive) với đa nền tảng: PC, Tablet, Mobile (từ 375px trở lên). Giao diện backend Odoo trực quan, dễ học cho nhân viên mới. |
| **Bảo mật (Security)** | Dữ liệu CRM và Kho được phân quyền theo chức vụ. Nhân viên Kho không được phép xem các báo giá kinh doanh của CRM và ngược lại. Khách vãng lai chỉ xem được thông tin Public trên Web. |
| **Tính dự phòng (Reliability/Backup)** | Hệ thống Database PostgreSQL cần có cơ chế sao lưu (Backup) tự động và có khả năng phục hồi (Restore) khi phát sinh sự cố mất dữ liệu. |

---

## 3. Sơ đồ Use-Case và Đặc tả chi tiết

### 3.1 Sơ đồ Use-Case Tổng quan

```mermaid
usecaseDiagram
    actor "Khách hàng" as KH
    actor "Nhân viên Kho" as NV_Kho
    actor "Nhân viên Sales" as NV_Sales

    package "Website Module" {
        usecase "UC01: Xem & Tìm kiếm Sản phẩm" as UC01
        usecase "UC02: Đăng ký tư vấn qua form" as UC02
    }

    package "Inventory Module" {
        usecase "UC03: Nhập kho theo Serial" as UC03
        usecase "UC04: Xuất kho theo Serial" as UC04
        usecase "UC05: Chuyển kho nội bộ" as UC05
        usecase "UC06: Traceability (Truy vết)" as UC06
        usecase "UC07: Báo cáo Tồn kho" as UC07
    }

    package "CRM Module" {
        usecase "UC08: Quản lý Pipeline" as UC08
        usecase "UC09: Xử lý Lead & Activity" as UC09
    }

    KH --> UC01
    KH --> UC02

    NV_Kho --> UC03
    NV_Kho --> UC04
    NV_Kho --> UC05
    NV_Kho --> UC06
    NV_Kho --> UC07

    NV_Sales --> UC08
    NV_Sales --> UC09
    
    UC02 ..> UC09 : <<include>> Tạo Lead tự động
```

### 3.2 Đặc tả Use-Case chi tiết

**UC01: Xem & Tìm kiếm Sản phẩm**
- **Actor:** Khách hàng
- **Mô tả:** Khách hàng duyệt danh mục, tìm kiếm và xem chi tiết cấu hình sản phẩm trên Website.
- **Luồng sự kiện chính:**
  1. Khách truy cập vào trang `/shop`.
  2. Chọn danh mục sản phẩm ở thanh điều hướng bên trái.
  3. Hệ thống trả về danh sách các mặt hàng tương ứng.
  4. Khách click vào một sản phẩm để xem giá, hình ảnh và thông số kỹ thuật.
- **Tiền điều kiện:** Sản phẩm đã được nhân viên cập nhật thông tin và đánh dấu "Published".

**UC02: Đăng ký tư vấn qua form**
- **Actor:** Khách hàng
- **Mô tả:** Gửi yêu cầu liên hệ hoặc đăng ký nhận báo giá cho dự án/thiết bị.
- **Luồng sự kiện chính:**
  1. Khách hàng vào trang `/tu-van`.
  2. Điền Họ Tên, Số điện thoại, Email và Nội dung cần tư vấn.
  3. Bấm "Gửi thông tin".
  4. Hệ thống hiển thị thông báo gửi thành công và ghi nhận dữ liệu vào backend.
- **Luồng ngoại lệ:** Nếu để trống trường Email, hệ thống báo lỗi không cho gửi form.

**UC03: Nhập kho theo Serial Number**
- **Actor:** Nhân viên Kho
- **Mô tả:** Nhập thiết bị công nghệ từ Nhà cung cấp vào kho lưu trữ và gán mã Serial.
- **Luồng sự kiện chính:**
  1. Nhân viên Kho tạo một phiếu Receipt mới.
  2. Chọn Nhà cung cấp và thêm dòng Sản phẩm cần nhập.
  3. Nhập/Quét mã Serial cho từng đơn vị sản phẩm tương ứng với số lượng nhập.
  4. Bấm Validate để hoàn tất.
- **Hậu điều kiện:** Sản phẩm với mã Serial tương ứng chính thức có trạng thái "On Hand" trong kho.

**UC04: Xuất kho theo Serial Number**
- **Actor:** Nhân viên Kho
- **Mô tả:** Xuất hàng hóa giao cho Khách hàng dựa trên Serial Number cụ thể.
- **Luồng sự kiện chính:**
  1. Nhân viên Kho tạo phiếu Delivery.
  2. Chọn Sản phẩm cần xuất.
  3. Bấm vào icon chi tiết (Detailed Operations) để chọn đích danh Serial Number đang có trong kho.
  4. Bấm Validate.
- **Luồng ngoại lệ:** Nếu chọn một Serial đang không nằm trong kho, hệ thống cảnh báo và từ chối xuất.

**UC05: Chuyển kho nội bộ (Internal Transfer)**
- **Actor:** Nhân viên Kho
- **Mô tả:** Di chuyển hàng hóa từ Kệ/Kho này sang Kệ/Kho khác trong công ty.
- **Luồng sự kiện chính:**
  1. Tạo phiếu Internal Transfer.
  2. Chọn Vị trí nguồn (Source Location) và Vị trí đích (Destination Location).
  3. Chọn sản phẩm và mã Serial muốn di chuyển.
  4. Bấm Validate.

**UC06: Traceability (Truy vết Serial)**
- **Actor:** Nhân viên Kho
- **Mô tả:** Truy xuất toàn bộ lịch sử di chuyển của một mã Serial để phục vụ bảo hành, khiếu nại.
- **Luồng sự kiện chính:**
  1. Vào menu Lots/Serial Numbers.
  2. Gõ tìm mã Serial cần tra cứu.
  3. Nhấn vào nút Traceability trên giao diện.
  4. Hệ thống hiển thị sơ đồ cây từ lúc Nhập (Vendor) -> Kho nội bộ -> Xuất (Customer).

**UC07: Xem Báo cáo tồn kho**
- **Actor:** Nhân viên Kho, Admin
- **Mô tả:** Kiểm tra tổng số lượng hàng hóa và giá trị hàng hóa đang nằm trong các kho.
- **Luồng sự kiện chính:**
  1. Vào menu Reporting > Inventory Report.
  2. Sử dụng bộ lọc theo Location hoặc Danh mục sản phẩm.
  3. Export file Excel nếu cần thiết.

**UC08: Quản lý Pipeline (Cơ hội kinh doanh)**
- **Actor:** Nhân viên Sales
- **Mô tả:** Theo dõi và cập nhật trạng thái của các Leads/Opportunities trên giao diện Kanban.
- **Luồng sự kiện chính:**
  1. Vào ứng dụng CRM.
  2. Giao diện hiển thị các cột trạng thái (New, Đang tư vấn, Báo giá...).
  3. Nhân viên nắm giữ thẻ Khách hàng và Kéo - Thả (Drag & Drop) sang cột tiếp theo.
  4. Hệ thống cập nhật xác suất chốt (Probability) tự động.

**UC09: Xử lý Lead & Activity tự động**
- **Actor:** Nhân viên Sales
- **Mô tả:** Nhận Lead từ website và thực hiện các tác vụ theo quy trình đã thiết lập.
- **Luồng sự kiện chính:**
  1. Ngay khi Khách hàng gửi Form (UC02), Lead mới xuất hiện trong cột "New".
  2. Nhân viên vào chi tiết Lead, hệ thống có sẵn lịch "Call to Action" nhắc nhở gọi điện tư vấn.
  3. Nhân viên gọi xong, đánh dấu "Mark as Done" và ghi chú kết quả tư vấn vào log.
  4. Gửi email template (Báo giá) trực tiếp từ giao diện Odoo cho khách.
