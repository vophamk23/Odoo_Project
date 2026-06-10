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
    actor "Quản trị viên (Admin)" as Admin

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
        usecase "UC11: Quản lý danh mục Sản phẩm" as UC11
    }

    package "CRM & Sales Module" {
        usecase "UC08: Quản lý Pipeline" as UC08
        usecase "UC09: Xử lý Lead & Activity" as UC09
        usecase "UC10: Lập Báo giá & Đơn bán hàng" as UC10
    }

    package "System Admin" {
        usecase "UC12: Quản lý Phân quyền Người dùng" as UC12
    }

    KH --> UC01
    KH --> UC02

    NV_Kho --> UC03
    NV_Kho --> UC04
    NV_Kho --> UC05
    NV_Kho --> UC06
    NV_Kho --> UC07
    NV_Kho --> UC11

    NV_Sales --> UC08
    NV_Sales --> UC09
    NV_Sales --> UC10

    Admin --> UC11
    Admin --> UC12
    Admin --> UC07

    UC02 ..> UC09 : <<include>> Tạo Lead tự động
    UC10 ..> UC04 : <<trigger>> Kích hoạt Xuất kho
```

### 3.2 Đặc tả Use-Case chi tiết

Dưới đây là chi tiết đặc tả cho các Use Case theo đúng biểu mẫu chuẩn.

#### UC01: Xem & Tìm kiếm Sản phẩm

| Thành phần | Chi tiết |
| --- | --- |
| **Usecase ID** | UC01 |
| **Usecase Name** | Xem & Tìm kiếm Sản phẩm |
| **Description** | Khách hàng duyệt danh mục, tìm kiếm và xem chi tiết thông số kỹ thuật của sản phẩm trên Website. |
| **Actors** | Khách hàng |
| **Scope** | Phân hệ Website (E-commerce) |
| **Preconditions** | Hệ thống website đang hoạt động. Các sản phẩm đã được nhân viên cấu hình hiển thị (Published) với đầy đủ hình ảnh, giá cả. |
| **Normal flow** | 1. Khách truy cập vào trang `/shop`.<br>2. Chọn danh mục sản phẩm mong muốn ở thanh điều hướng bên trái.<br>3. Hệ thống trả về danh sách các mặt hàng tương ứng.<br>4. Khách click vào một sản phẩm để xem cấu hình chi tiết, giá và tồn kho. |
| **Post conditions** | Khách hàng nắm được thông tin sản phẩm và có thể tiến hành bước tiếp theo (Đăng ký tư vấn). |
| **Alternative flow** | Ở bước 2, thay vì chọn danh mục, Khách hàng gõ từ khóa trực tiếp vào thanh Tìm kiếm (Search bar) để tìm đích danh sản phẩm. |
| **Exception flow** | Nếu Khách hàng tìm kiếm sản phẩm không tồn tại, hệ thống hiển thị thông báo "Không tìm thấy sản phẩm nào phù hợp". |
| **Special Requirements** | Giao diện phải tải trang dưới 3 giây và responsive tốt trên điện thoại di động. |

#### UC02: Đăng ký tư vấn qua form

| Thành phần | Chi tiết |
| --- | --- |
| **Usecase ID** | UC02 |
| **Usecase Name** | Đăng ký tư vấn qua form |
| **Description** | Khách hàng để lại thông tin (Tên, Số điện thoại, Email) và nội dung cần tư vấn trên trang Website để nhân viên Sales liên hệ lại. |
| **Actors** | Khách hàng |
| **Scope** | Phân hệ Website và tích hợp CRM |
| **Preconditions** | Hệ thống Website hoạt động bình thường. Mẫu form liên hệ đã được cấu hình trỏ về CRM. |
| **Normal flow** | 1. Khách hàng truy cập trang `/tu-van`.<br>2. Khách hàng điền đầy đủ các thông tin: Họ Tên, Số điện thoại, Email và Nội dung cần hỗ trợ.<br>3. Khách hàng nhấn nút "Gửi thông tin".<br>4. Hệ thống ghi nhận dữ liệu, hiển thị màn hình Cảm ơn. |
| **Post conditions** | Dữ liệu form được lưu trữ thành công và hệ thống CRM tự động khởi tạo một Lead mới. |
| **Alternative flow** | Không có |
| **Exception flow** | Nếu khách hàng để trống trường bắt buộc (VD: Email), hệ thống hiển thị cảnh báo đỏ và không cho phép submit form. |
| **Special Requirements** | Form phải có chức năng chống spam (CAPTCHA cơ bản). |

#### UC03: Nhập kho theo Serial Number

| Thành phần | Chi tiết |
| --- | --- |
| **Usecase ID** | UC03 |
| **Usecase Name** | Nhập kho theo Serial Number |
| **Description** | Nhân viên kho thực hiện quy trình nhận hàng từ nhà cung cấp và gán mã định danh Serial duy nhất cho từng thiết bị nhập kho. |
| **Actors** | Nhân viên Kho |
| **Scope** | Phân hệ Quản lý Kho (Inventory) |
| **Preconditions** | Sản phẩm đã được khởi tạo trong hệ thống và đánh dấu thuộc tính "Tracking by Unique Serial Number". |
| **Normal flow** | 1. Nhân viên Kho đăng nhập hệ thống và tạo một phiếu Nhập kho (Receipt).<br>2. Chọn tên Nhà cung cấp và thêm dòng Sản phẩm cần nhập.<br>3. Mở popup Detailed Operations, nhập/quét mã Serial Number cho từng sản phẩm tương ứng với số lượng nhập.<br>4. Nhân viên bấm nút "Validate" để hoàn tất phiếu. |
| **Post conditions** | Số lượng tồn kho (On Hand) của sản phẩm tăng lên. Các Serial Number vừa nhập được kích hoạt và nằm ở kho đích. |
| **Alternative flow** | Thay vì nhập thủ công, nhân viên có thể sử dụng tính năng Import Excel để đưa hàng loạt mã Serial vào phiếu nhập. |
| **Exception flow** | Nếu nhân viên gán một Serial Number đã có sẵn trong kho, hệ thống lập tức báo lỗi Duplicate và ngăn chặn bước Validate. |
| **Special Requirements** | Phải đảm bảo quy tắc mỗi mã Serial là duy nhất trên toàn hệ thống. |

#### UC04: Xuất kho theo Serial Number

| Thành phần | Chi tiết |
| --- | --- |
| **Usecase ID** | UC04 |
| **Usecase Name** | Xuất kho theo Serial Number |
| **Description** | Nhân viên kho tạo phiếu xuất kho để giao sản phẩm cho khách hàng, chọn đúng Serial Number thực tế sẽ giao. |
| **Actors** | Nhân viên Kho |
| **Scope** | Phân hệ Quản lý Kho (Inventory) |
| **Preconditions** | Tồn kho của sản phẩm phải > 0 và Serial Number cần xuất phải đang nằm trong kho (On Hand). |
| **Normal flow** | 1. Nhân viên Kho tạo phiếu Xuất kho (Delivery Order).<br>2. Chọn Đối tác nhận hàng và Sản phẩm cần xuất.<br>3. Hệ thống gợi ý số lượng xuất (Check Availability).<br>4. Nhân viên chọn đích danh Serial Number đang có mặt ở kho.<br>5. Bấm nút "Validate" để chốt phiếu. |
| **Post conditions** | Tồn kho của sản phẩm giảm đi. Serial Number đó được đánh dấu là đã giao cho Khách hàng. |
| **Alternative flow** | Nhân viên có thể bấm "Auto Assign" để Odoo tự động bắt Serial Number cũ nhất (FIFO) ra xuất thay vì tự chọn. |
| **Exception flow** | Nếu cố tình điền một mã Serial không có trong kho, Odoo sẽ hiện cảnh báo và chặn luồng xuất kho. |
| **Special Requirements** | Không có |

#### UC05: Chuyển kho nội bộ (Internal Transfer)

| Thành phần | Chi tiết |
| --- | --- |
| **Usecase ID** | UC05 |
| **Usecase Name** | Chuyển kho nội bộ (Internal Transfer) |
| **Description** | Luân chuyển sản phẩm cùng mã Serial từ vị trí này (VD: Kho tổng) sang vị trí khác (VD: Kho trưng bày) trong nội bộ công ty. |
| **Actors** | Nhân viên Kho |
| **Scope** | Phân hệ Quản lý Kho (Inventory) |
| **Preconditions** | Hàng hóa muốn chuyển phải có sẵn tồn kho tại Vị trí nguồn (Source Location). |
| **Normal flow** | 1. Tạo phiếu Internal Transfer.<br>2. Chọn Vị trí nguồn (Source Location) và Vị trí đích (Destination Location).<br>3. Chọn sản phẩm và đích danh mã Serial muốn di chuyển.<br>4. Bấm Validate để hoàn tất. |
| **Post conditions** | Hàng hóa (cùng mã Serial) sẽ biến mất ở Vị trí nguồn và xuất hiện tại Vị trí đích. Tổng tồn kho công ty không đổi. |
| **Alternative flow** | Không có |
| **Exception flow** | Lỗi nếu Vị trí đích bị khóa hoặc không đủ quyền truy cập. |
| **Special Requirements** | Không có |

#### UC06: Traceability (Truy vết Serial)

| Thành phần | Chi tiết |
| --- | --- |
| **Usecase ID** | UC06 |
| **Usecase Name** | Traceability (Truy vết Serial) |
| **Description** | Khả năng truy xuất lại toàn bộ hành trình (đường đi) của một Serial Number từ khi nhập kho đến khi xuất bán. Rất quan trọng khi làm bảo hành. |
| **Actors** | Nhân viên Kho, Admin |
| **Scope** | Phân hệ Quản lý Kho (Inventory) |
| **Preconditions** | Mã Serial Number phải tồn tại trong hệ thống. |
| **Normal flow** | 1. Truy cập menu Lots/Serial Numbers trong Inventory.<br>2. Nhập mã Serial vào ô tìm kiếm.<br>3. Mở bản ghi Serial đó ra và nhấn vào nút "Traceability" (hoặc "Truy vết") trên góc phải giao diện.<br>4. Hệ thống hiển thị biểu đồ cây liệt kê tất cả các phiếu nhập, chuyển, xuất liên quan. |
| **Post conditions** | Người dùng xem được lịch sử và lấy được mã phiếu xuất gốc để kiểm tra bảo hành. |
| **Alternative flow** | Không có |
| **Exception flow** | Nếu gõ sai mã Serial, hệ thống hiển thị danh sách rỗng. |
| **Special Requirements** | Cây truy vết phải chỉ rõ ngày giờ thực hiện của từng lần dịch chuyển. |

#### UC07: Báo cáo Tồn kho

| Thành phần | Chi tiết |
| --- | --- |
| **Usecase ID** | UC07 |
| **Usecase Name** | Báo cáo Tồn kho |
| **Description** | Xuất báo cáo tổng hợp hoặc chi tiết về lượng hàng, giá trị tồn kho tại các Location cụ thể. |
| **Actors** | Nhân viên Kho, Admin |
| **Scope** | Phân hệ Quản lý Kho (Inventory) |
| **Preconditions** | User phải được cấp quyền xem Báo cáo (Inventory Report). |
| **Normal flow** | 1. Vào menu Reporting > Inventory Report.<br>2. Sử dụng thanh filter để nhóm (Group By) theo Sản phẩm hoặc theo Vị trí (Location).<br>3. Xem số lượng tồn kho hiển thị trực quan.<br>4. Bấm nút Export để tải báo cáo Excel về máy tính. |
| **Post conditions** | Có được file dữ liệu Excel tồn kho chính xác để báo cáo ban giám đốc. |
| **Alternative flow** | Chuyển chế độ xem từ List sang Pivot/Graph để phân tích trực quan. |
| **Exception flow** | Không có |
| **Special Requirements** | Dữ liệu phải là thời gian thực (Real-time). |

#### UC08: Quản lý Pipeline (Cơ hội kinh doanh)

| Thành phần | Chi tiết |
| --- | --- |
| **Usecase ID** | UC08 |
| **Usecase Name** | Quản lý Pipeline |
| **Description** | Nhân viên kinh doanh theo dõi và kéo thả các Lead/Opportunity qua các chặng trong quy trình bán hàng bằng giao diện Kanban. |
| **Actors** | Nhân viên Sales |
| **Scope** | Phân hệ CRM |
| **Preconditions** | Đã cấu hình các cột Stage (Mới, Đang tư vấn, Báo giá, Chốt...). |
| **Normal flow** | 1. Nhân viên Sales vào ứng dụng CRM, mở giao diện Pipeline.<br>2. Giao diện Kanban hiện ra với các Lead.<br>3. Nhân viên nắm giữ thẻ Lead của một Khách hàng và Kéo - Thả (Drag & Drop) sang cột tiếp theo (Ví dụ: Từ "Mới" sang "Báo giá").<br>4. Hệ thống cập nhật trạng thái mới. |
| **Post conditions** | Lead thay đổi Stage. Hệ thống tự động cập nhật xác suất thành công (Probability). |
| **Alternative flow** | Đánh dấu Lead là "Won" (Thắng) hoặc "Lost" (Thua) trực tiếp mà không cần qua hết các bước trung gian. |
| **Exception flow** | Không có |
| **Special Requirements** | Giao diện phải mượt mà khi Drag & Drop lượng dữ liệu lớn. |

#### UC09: Xử lý Lead & Activity tự động

| Thành phần | Chi tiết |
| --- | --- |
| **Usecase ID** | UC09 |
| **Usecase Name** | Xử lý Lead & Activity tự động |
| **Description** | Nhận Lead từ website và thực hiện các tác vụ chăm sóc (gọi điện, email) theo lịch nhắc nhở. |
| **Actors** | Nhân viên Sales |
| **Scope** | Phân hệ CRM |
| **Preconditions** | Website Form đã kết nối tới CRM. Các luật tự động (Automated Actions) tạo Activity đã được kích hoạt. |
| **Normal flow** | 1. Lead tự động xuất hiện ở cột "Mới" khi Khách hàng gửi Form.<br>2. Nhân viên vào chi tiết Lead, hệ thống hiển thị lịch nhắc việc (Activity) "Cần gọi điện tư vấn" màu xanh (chưa quá hạn).<br>3. Nhân viên thực hiện cuộc gọi, ấn "Mark as Done" và ghi chú nội dung cuộc gọi.<br>4. Chọn "Schedule Next Activity" nếu cần gọi lại lần 2. |
| **Post conditions** | Lead được chăm sóc kịp thời. Lịch sử làm việc được ghi nhận đầy đủ trong phần Log của Lead. |
| **Alternative flow** | Có thể bấm Gửi Email ngay trong khung chat (Log) của Lead để trao đổi trực tiếp với khách thay vì gọi điện. |
| **Exception flow** | Nếu Activity quá hạn, hệ thống đổi màu lịch nhắc nhở sang Đỏ để cảnh báo. |
| **Special Requirements** | Lịch sử Log phải không thể xóa để đảm bảo minh bạch trong việc chăm sóc khách hàng. |

#### UC10: Lập Báo giá và Đơn bán hàng (Sales Order)

| Thành phần | Chi tiết |
| --- | --- |
| **Usecase ID** | UC10 |
| **Usecase Name** | Lập Báo giá và Đơn bán hàng |
| **Description** | Nhân viên Sales tạo Báo giá (Quotation) từ một Lead/Opportunity thành công, gửi cho khách hàng và chốt thành Đơn bán hàng (Sales Order). |
| **Actors** | Nhân viên Sales |
| **Scope** | Phân hệ CRM & Sales |
| **Preconditions** | Cơ hội kinh doanh (Opportunity) đã đến giai đoạn "Báo giá" hoặc "Chốt". |
| **Normal flow** | 1. Nhân viên mở thẻ Khách hàng trong CRM, nhấn nút "New Quotation".<br>2. Thêm các sản phẩm, số lượng, điều chỉnh đơn giá/chiết khấu nếu cần.<br>3. Nhấn "Send by Email" để gửi file PDF Báo giá cho khách hàng.<br>4. Khi khách hàng xác nhận mua, nhân viên nhấn "Confirm" để chuyển Báo giá thành Đơn bán hàng (Sales Order). |
| **Post conditions** | Đơn bán hàng được tạo thành công. Hệ thống tự động sinh ra một phiếu Xuất kho (Delivery) ở trạng thái "Chờ xử lý" (Waiting) cho bộ phận Kho. |
| **Alternative flow** | Nhân viên có thể in Báo giá ra giấy (Print PDF) đưa trực tiếp cho khách thay vì gửi Email. |
| **Exception flow** | Nếu thêm sản phẩm đang hết hàng (Out of Stock) vào báo giá, Odoo sẽ hiện cảnh báo màu đỏ bên cạnh tên sản phẩm. |
| **Special Requirements** | Mẫu PDF Báo giá phải có logo và thông tin liên hệ của CMCTS. |

#### UC11: Quản lý danh mục Sản phẩm

| Thành phần | Chi tiết |
| --- | --- |
| **Usecase ID** | UC11 |
| **Usecase Name** | Quản lý danh mục Sản phẩm |
| **Description** | Tạo mới và cấu hình thông tin cho các sản phẩm thiết bị công nghệ chuẩn bị kinh doanh. |
| **Actors** | Admin, Nhân viên Kho (có quyền Quản lý) |
| **Scope** | Phân hệ Inventory |
| **Preconditions** | Người dùng đăng nhập với quyền Admin hoặc Quản lý Kho. |
| **Normal flow** | 1. Vào menu Products > Tạo mới (Create).<br>2. Điền Tên sản phẩm, tải ảnh đại diện lên, thiết lập Giá bán, Danh mục (Category).<br>3. Chuyển sang tab "Inventory", tích chọn phương thức Tracking là "By Unique Serial Number".<br>4. Nhấn Save. |
| **Post conditions** | Sản phẩm mới xuất hiện trong hệ thống, sẵn sàng để Nhập kho và đăng bán lên Website. |
| **Alternative flow** | Import hàng loạt sản phẩm bằng file Excel thay vì nhập tay từng cái. |
| **Exception flow** | Nếu quên chọn "By Unique Serial Number" mà để mặc định là "No Tracking", nhân viên kho sau này sẽ không thể nhập Serial cho hàng hóa đó. |
| **Special Requirements** | Bắt buộc phải đánh dấu các sản phẩm thiết bị là hàng hóa "Storable Product" (Hàng lưu kho). |

#### UC12: Quản lý Phân quyền Người dùng (Access Rights)

| Thành phần | Chi tiết |
| --- | --- |
| **Usecase ID** | UC12 |
| **Usecase Name** | Quản lý Phân quyền Người dùng |
| **Description** | Admin tạo tài khoản cho nhân viên và phân quyền truy cập nghiêm ngặt giữa các phòng ban. |
| **Actors** | Admin |
| **Scope** | Phân hệ Settings (Cài đặt hệ thống) |
| **Preconditions** | Phải đăng nhập bằng tài khoản Administrator cao nhất. Kích hoạt chế độ Developer Mode nếu cần thiết lập sâu. |
| **Normal flow** | 1. Vào Settings > Users & Companies > Users.<br>2. Nhấn Create để tạo tài khoản mới (Nhập tên, Email đăng nhập).<br>3. Ở phần Access Rights, thiết lập:<br> - Nhân viên A: CRM = User: All Documents, Inventory = Blank.<br> - Nhân viên B: Inventory = User, CRM = Blank.<br>4. Gửi email mời (Send Invitation) để nhân viên tự đặt mật khẩu. |
| **Post conditions** | Nhân viên nhận được tài khoản. Khi đăng nhập, Nhân viên Kho sẽ không thấy icon app CRM, và ngược lại. |
| **Alternative flow** | Admin tự thiết lập Mật khẩu trực tiếp (Change Password) thay vì gửi email mời. |
| **Exception flow** | Nếu cấp quyền sai, nhân viên có thể xem được dữ liệu nhạy cảm của phòng ban khác. |
| **Special Requirements** | Tài khoản Admin mặc định không bao giờ được phép xóa. |
