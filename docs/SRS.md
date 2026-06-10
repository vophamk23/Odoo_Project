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

Trong bối cảnh nền kinh tế số đang phát triển mạnh mẽ, việc duy trì hệ thống quản lý rời rạc và thủ công giữa các bộ phận bán hàng, tiếp thị và kho bãi đang tạo ra những rào cản lớn đối với năng lực cạnh tranh của doanh nghiệp. Vấn đề này đặc biệt nhức nhối đối với các doanh nghiệp hoạt động trong lĩnh vực phân phối thiết bị khoa học công nghệ cao, nơi các sản phẩm có giá trị tài sản lớn và đòi hỏi sự giám sát chặt chẽ về chế độ bảo hành thông qua các chuỗi mã định danh duy nhất (Serial Number). 

Để giải quyết bài toán trên, dự án **VoPC-CMCTS Phase 1** được khởi tạo nhằm mục đích nghiên cứu, mô phỏng và triển khai một giải pháp quản trị doanh nghiệp (ERP) toàn diện. Dựa trên sức mạnh của nền tảng mã nguồn mở **Odoo 18** và lấy cảm hứng từ mô hình kinh doanh thực tiễn của Công ty TNHH Thương Mại C.M.C (cmcts.com.vn), dự án hướng tới việc thiết lập một quy trình số hóa liền mạch. Quy trình này kết nối chặt chẽ từ điểm chạm đầu tiên khi khách hàng tiếp cận website (Front-end) và để lại thông tin tư vấn, đi qua phễu bán hàng CRM, cho đến khâu cuối cùng là nhân viên quản lý kho xác nhận xuất hàng theo đúng số Serial Number quy định.

### 1.2 Mục tiêu, phạm vi và giới hạn

**Mục tiêu cốt lõi:**

- Thiết kế và triển khai một hệ thống ERP tiêu chuẩn, đảm bảo vận hành trơn tru các luồng dữ liệu cốt lõi giúp số hóa hoàn toàn quy trình kinh doanh.
- Tự động hóa ở mức tối đa quy trình tiếp nhận, phân bổ và chăm sóc khách hàng tiềm năng (CRM), đồng thời nâng cao tính minh bạch trong quản lý hàng hóa vật lý chính xác đến từng đơn vị sản phẩm (Inventory Tracking by Serial Number).

**Phạm vi hệ thống:**

- **Website (E-commerce & Portal):** Xây dựng cổng thông tin giới thiệu pháp nhân doanh nghiệp, trưng bày danh mục sản phẩm trực tuyến, tích hợp biểu mẫu thu thập dữ liệu khách hàng (Web Form) cùng các trang nội dung hỗ trợ như Blog và Sự kiện.
- **Quản lý Kho (Inventory — Trọng tâm chính):** Thiết lập quy trình vận hành kho bãi bao gồm theo dõi luồng hàng hóa nhập (Inbound), xuất (Outbound) và luân chuyển nội bộ (Internal Transfer) dựa trên công nghệ quản lý bằng Unique Serial Number. Cung cấp công cụ kiểm kê kho và truy xuất nguồn gốc sản phẩm chi tiết.
- **Quản lý quan hệ khách hàng (CRM):** Xây dựng cấu trúc đường ống bán hàng (Pipeline) thông minh để quản lý cơ hội kinh doanh. Tích hợp tự động hóa quy trình tạo Lead từ Website form và cung cấp công cụ nhắc việc giúp nhân viên kinh doanh duy trì tương tác tốt với khách hàng.

**Giới hạn dự án (Giai đoạn Phase 1):**

- Tạm thời chưa tích hợp hệ thống với các cổng thanh toán trực tuyến (Payment Gateways) hay ngân hàng số.
- Không triển khai các phân hệ nghiệp vụ độc lập khác như Kế toán (Accounting), Phát hành Hóa đơn điện tử (E-invoicing) hay Quản trị Nguồn nhân lực (HR).
- Hệ thống được triển khai, kiểm thử trên môi trường nội bộ (Localhost) bằng nền tảng Container (Docker) và sử dụng dữ liệu giả lập (Demo data) thay vì dữ liệu doanh nghiệp thực tế.

### 1.3 Stakeholders (Các bên liên quan) và Vai trò

Hệ thống được thiết kế để phục vụ 4 nhóm đối tượng chính, mỗi nhóm sẽ được phân quyền và giao trách nhiệm rõ ràng nhằm đảm bảo an toàn thông tin:

- **Quản trị viên hệ thống (Admin):** Đóng vai trò là người điều phối kỹ thuật cao nhất. Nắm giữ toàn quyền trong việc thiết lập cấu hình tổng thể, quản lý phân quyền (Access Rights) cho các nhóm người dùng khác và phê duyệt các báo cáo thay đổi hệ thống.
- **Khách hàng (Customer / End-user):** Đóng vai trò là người dùng công cộng (Public User). Thực hiện các thao tác tìm kiếm thông tin thiết bị, đọc tin tức chuyên ngành và tương tác gửi yêu cầu tư vấn thông qua các biểu mẫu (Web Forms) mà không cần tạo tài khoản đăng nhập.
- **Nhân viên Quản lý Kho (Inventory Staff):** Chịu trách nhiệm trực tiếp đối với luồng di chuyển vật lý của hàng hóa. Thực hiện việc ghi nhận số lượng, tạo phiếu nhập/xuất/điều chuyển kho, và đặc biệt là kiểm soát tính chính xác của các mã Serial Number. Được quyền trích xuất các báo cáo tồn kho định kỳ.
- **Nhân viên Kinh doanh (Sales Executive):** Đại diện cho bộ phận tiếp thị và bán hàng. Sử dụng hệ thống để theo dõi, quản lý vòng đời của các khách hàng tiềm năng (Leads/Opportunities) trên giao diện CRM. Phụ trách việc cập nhật trạng thái đàm phán, gọi điện, gửi báo giá và trực tiếp chốt đơn hàng.

### 1.4 Câu chuyện Người dùng (User Stories)

Danh sách dưới đây mô tả các nhu cầu tương tác cốt lõi của các bên liên quan dưới góc nhìn thực tế (User Stories):

- **[US-01] Nhu cầu tra cứu sản phẩm (Khách hàng):** "Là một Khách hàng, tôi muốn có thể xem và lọc danh sách các thiết bị công nghệ theo từng danh mục cụ thể, *để* tôi có thể nhanh chóng định vị và tìm ra sản phẩm phù hợp nhất với nhu cầu của mình."
- **[US-02] Nhu cầu liên hệ tư vấn (Khách hàng):** "Là một Khách hàng, tôi muốn được cung cấp một biểu mẫu đăng ký thông tin trực tuyến rõ ràng, *để* tôi có thể gửi yêu cầu hỗ trợ đến bộ phận kinh doanh một cách nhanh chóng."
- **[US-03] Nhu cầu định danh thiết bị (Nhân viên Kho):** "Là một Nhân viên Kho, tôi muốn hệ thống yêu cầu tôi gán một mã Serial Number duy nhất cho từng thiết bị vật lý khi nhập kho, *để* tôi có thể quản lý chính xác tồn kho của từng sản phẩm cụ thể và phục vụ công tác đối soát bảo hành sau này."
- **[US-04] Nhu cầu kiểm soát dữ liệu (Nhân viên Kho):** "Là một Nhân viên Kho, tôi muốn hệ thống tự động phát ra cảnh báo lỗi nếu tôi vô tình nhập trùng lặp một mã Serial đã tồn tại, *để* tôi tránh được các sai sót về nhập liệu và đảm bảo tính nhất quán của cơ sở dữ liệu."
- **[US-05] Nhu cầu truy vết nguồn gốc (Nhân viên Kho):** "Là một Nhân viên Kho, tôi muốn có một công cụ truy vết (Traceability) để kiểm tra lịch sử luân chuyển của bất kỳ mã Serial nào, *để* tôi biết chính xác thiết bị đó đã được nhập về từ phiếu nào, nằm ở kho nào và xuất bán cho ai."
- **[US-06] Nhu cầu số hóa khách hàng (Nhân viên Sales):** "Là một Nhân viên Sales, tôi muốn hệ thống tự động khởi tạo một thẻ Cơ hội kinh doanh (Lead) mới trên CRM ngay khi có khách hàng gửi form từ website, *để* tôi không bị bỏ sót bất kỳ một tệp khách hàng tiềm năng nào."
- **[US-07] Nhu cầu tự động hóa nhắc việc (Nhân viên Sales):** "Là một Nhân viên Sales, tôi muốn hệ thống tự động thiết lập các tác vụ nhắc việc (Activity) mỗi khi tôi kéo thả Lead sang một giai đoạn mới, *để* tôi luôn nhớ lịch hẹn gọi điện hoặc gửi email chăm sóc đúng hạn."

---

## 2. Công nghệ & Môi trường

### 2.1 Tech Stack

| Thành phần | Công nghệ / Phiên bản | Mô tả |
| --- | --- | --- |
| **Nền tảng ERP** | Odoo (Phiên bản 18.0) | Cung cấp bộ khung quản trị doanh nghiệp toàn diện. |
| **Ngôn ngữ Backend** | Python (Phiên bản 3.10+) | Ngôn ngữ lập trình chính xử lý logic nghiệp vụ. |
| **Cơ sở dữ liệu (Database)** | PostgreSQL (Phiên bản 14+) | Quản trị cơ sở dữ liệu quan hệ mạnh mẽ, đảm bảo tính toàn vẹn dữ liệu. |
| **Frontend** | Odoo Website Builder + Custom CSS | Hỗ trợ thiết kế giao diện linh hoạt, đáp ứng. |
| **Môi trường triển khai** | Docker hoặc Ubuntu bare metal | Đảm bảo tính nhất quán giữa môi trường phát triển và vận hành. |
| **Quản lý mã nguồn (Source Control)** | Git + GitHub | Quản lý phiên bản và cộng tác nhóm. |
| **Công cụ thiết kế tài liệu** | draw.io, dbdiagram.io | Xây dựng sơ đồ Use Case, ERD và luồng quy trình. |

### 2.2 Môi trường triển khai

| Môi trường | Mô tả | URL |
| --- | --- | --- |
| **Development (Local)** | Triển khai trực tiếp trên máy tính cá nhân của từng lập trình viên thông qua Docker. | `http://localhost:8069` |
| **Demo (Shared)** | Triển khai trên máy chủ đám mây dùng chung cho cả nhóm để phục vụ công tác kiểm thử tích hợp và trình diễn sản phẩm. | *(Cấu hình sau)* |

### 2.3 Tài khoản hệ thống

Để phục vụ việc kiểm thử trên môi trường phát triển/demo, hệ thống thiết lập sẵn các tài khoản với phân quyền cụ thể:

| Loại tài khoản | Username | Password | Phân quyền (Role) |
| --- | --- | --- | --- |
| **Quản trị viên (Admin)** | `admin` | `admin` | Cung cấp quyền Administrator (toàn quyền thiết lập). |
| **Nhân viên Kho** | `kho_staff` | *(Cấu hình sau)* | Giới hạn quyền truy cập riêng cho phân hệ Inventory. |
| **Nhân viên Sales** | `sales_staff` | *(Cấu hình sau)* | Giới hạn quyền truy cập riêng cho phân hệ CRM. |

> ⚠️ **Lưu ý:** Tài khoản `admin/admin` với mật khẩu mặc định chỉ được phép sử dụng cho môi trường dev/demo cục bộ. Tuyệt đối không sử dụng cấu hình này khi triển khai hệ thống lên môi trường Production thực tế.

### 2.4 Cấu trúc thư mục & Quản lý mã nguồn

**Chiến lược quản lý nhánh (Git Branches):**

Dự án áp dụng mô hình quản lý nhánh Git chuyên nghiệp để phân tách luồng công việc:

- **Nhánh `main`:** Lưu trữ bộ mã nguồn gốc đã được kiểm thử (Stable Code), sẵn sàng để triển khai.
- **Nhánh `develop`:** Nhánh hội tụ, tổng hợp mã nguồn định kỳ từ các thành viên để phục vụ kiểm thử chung.
- **Nhánh `feature/*`:** Nhánh khởi tạo từ `develop` để mỗi thành viên phát triển tính năng riêng biệt.

**Cấu trúc thư mục dự án (Directory Structure):**

```text
VoPC-cmcts/
├── addons/                 ← Chứa các custom module phát triển riêng cho dự án
│   ├── cmcts_website/      ← Module tuỳ chỉnh giao diện trang chủ, e-commerce và web form
│   ├── cmcts_inventory/    ← Module tuỳ chỉnh nghiệp vụ kho, ràng buộc nhập/xuất theo Serial
│   └── cmcts_crm/          ← Module tuỳ chỉnh pipeline bán hàng và tự động hóa tạo Lead
├── config/                 ← Chứa file cấu hình hệ thống (odoo.conf)
├── data/                   ← Thư mục map volume lưu trữ dữ liệu PostgreSQL (được cấu hình gitignore)
├── docs/                   ← Chứa bộ tài liệu phân tích hệ thống (SRS, ERD, Test Cases)
├── backup/                 ← Chứa các file nén phục hồi cơ sở dữ liệu (.sql.gz) dự phòng
├── docker-compose.yml      ← File cấu hình môi trường Docker (Odoo, PostgreSQL)
└── README.md               ← Tài liệu hướng dẫn cài đặt và khởi chạy dự án
```

---

## 3. Yêu cầu hệ thống

### 3.1 Yêu cầu chức năng (Functional Requirements)

#### Nhóm Website (FR-W)

- **[FR-W01] Tối ưu hóa giao diện Trang chủ (Home Page):** Hệ thống cần cung cấp một trang chủ bắt mắt với khu vực Hero Banner động, trình bày rõ ràng các dịch vụ kinh doanh cốt lõi và làm nổi bật các dòng sản phẩm chiến lược để thu hút sự chú ý của khách hàng ngay khi truy cập.
- **[FR-W02] Quản lý danh mục và tìm kiếm sản phẩm (E-commerce):** Cho phép hiển thị danh sách thiết bị khoa học công nghệ dưới dạng lưới hoặc danh sách. Tích hợp thanh tìm kiếm thông minh, bộ lọc chi tiết theo mức giá, thương hiệu, và cấu trúc phân nhánh danh mục đa tầng giúp người dùng dễ dàng định vị sản phẩm.
- **[FR-W03] Biểu mẫu thu thập khách hàng tiềm năng (Contact Form):** Cung cấp biểu mẫu "Đăng ký tư vấn" trực quan với các trường thông tin bắt buộc (Họ tên, Số điện thoại, Địa chỉ Email). Form cần có cơ chế kiểm tra tính hợp lệ của dữ liệu đầu vào trước khi cho phép gửi.
- **[FR-W04] Phân hệ Thông tin và Truyền thông (Blog/Events):** Xây dựng các chuyên trang phụ trợ bao gồm "Về chúng tôi" (About Us) để khẳng định uy tín thương hiệu, trang "Blog" để cập nhật tin tức định kỳ và trang "Sự kiện" (Events) để quảng bá các hội thảo chuyên ngành.
- **[FR-W05] Tích hợp thông tin liên hệ và Bản đồ trực tuyến:** Trang "Contact Us" cung cấp đầy đủ thông tin pháp nhân của doanh nghiệp, tích hợp bản đồ Google Maps chỉ dẫn đường đi và cung cấp đa dạng các kênh liên lạc.
- **[FR-W06] Tương thích đa thiết bị (Responsive Design):** Giao diện Front-end phải được thiết kế theo chuẩn Responsive, tự động căn chỉnh và tối ưu hóa trải nghiệm hiển thị mượt mà trên nhiều kích thước màn hình khác nhau (Điện thoại, Máy tính bảng, Desktop).

#### Nhóm Quản lý Kho (FR-I) — Trọng tâm

- **[FR-I01] Cấu hình phương thức theo dõi đặc thù (Serial Tracking):** Hệ thống bắt buộc phải hỗ trợ cấu hình ở cấp độ sản phẩm, cho phép bật tính năng "Tracking by Unique Serial Number". Điều này đảm bảo mỗi thiết bị vật lý nhập/xuất đều được gắn một mã định danh duy nhất.
- **[FR-I02] Quản lý nghiệp vụ Nhập kho (Inbound Receipts):** Khi tiến hành tiếp nhận hàng hóa từ nhà cung cấp, nhân viên kho phải tạo Phiếu nhập và hệ thống yêu cầu bắt buộc phải quét mã vạch hoặc nhập thủ công chính xác từng mã Serial Number cho mỗi đơn vị sản phẩm trước khi xác nhận.
- **[FR-I03] Quản lý nghiệp vụ Xuất kho (Outbound Deliveries):** Tương tự quy trình nhập, mọi thao tác xuất kho giao hàng đều yêu cầu nhân viên chỉ định chính xác mã Serial Number của thiết bị đang nằm trong kho (On Hand). Hệ thống sẽ trừ tồn kho đúng sản phẩm vật lý đó.
- **[FR-I04] Điều chuyển luân phiên nội bộ (Internal Transfers):** Hỗ trợ lập phiếu điều chuyển thiết bị giữa các kho hoặc các vị trí (Locations) trong cùng một công ty. Quá trình này cũng yêu cầu kiểm soát chặt chẽ bằng việc scan mã Serial.
- **[FR-I05] Hệ thống Truy vết toàn diện (Traceability System):** Cung cấp công cụ theo dõi vòng đời của một mã Serial Number. Người dùng có thể tra cứu và xem được sơ đồ cây (Tree view) thể hiện chi tiết từ ngày nhập hàng, luân chuyển qua các kho nào, cho đến ngày xuất bán.
- **[FR-I06] Kiểm kê và đối soát kho định kỳ (Inventory Adjustments):** Cung cấp tính năng kiểm kê để so sánh giữa số lượng hàng thực tế trên kệ và số liệu đang ghi nhận trong phần mềm. Hệ thống tự động tạo các bút toán điều chỉnh sau khi quản lý phê duyệt.
- **[FR-I07] Hệ thống Báo cáo và Phân tích tồn kho (Reporting):** Trích xuất báo cáo tồn kho tại thời gian thực. Hỗ trợ các công cụ phân tích (Pivot, Graph) cho phép nhóm dữ liệu theo tên thiết bị, nhóm hàng hoặc kho bãi, đồng thời kết xuất dữ liệu ra file Excel.
- **[FR-I08] Kiểm soát tính toàn vẹn của dữ liệu (Duplicate Prevention):** Hệ thống tự động kiểm tra chéo mỗi khi người dùng nhập mã Serial. Nếu phát hiện một Serial Number đã được ghi nhận trước đó, hệ thống lập tức hiển thị cảnh báo lỗi và ngăn chặn hành vi lưu trữ để tránh trùng lặp.
- **[FR-I09] Bảng điều khiển Quản trị kho (Inventory Dashboard):** Cung cấp giao diện tổng quan cho Quản lý, hiển thị các biểu đồ thể hiện biến động nhập/xuất trong tháng, số lượng hàng chờ xử lý và các widget thống kê tổng giá trị tồn kho.

#### Nhóm CRM (FR-C)

- **[FR-C01] Cấu hình quy trình bán hàng chuẩn hóa (Sales Pipeline):** Thiết lập một chu trình chuyển đổi khách hàng rõ ràng dưới dạng bảng Kanban. Hệ thống sẽ có tối thiểu 6 giai đoạn (Stages): Tiếp nhận thông tin → Tư vấn sơ bộ → Gửi báo giá → Đàm phán thương lượng → Chốt hợp đồng (Won) → Khách từ chối (Lost).
- **[FR-C02] Khởi tạo Cơ hội kinh doanh tự động (Auto Lead Generation):** Hệ thống CRM được tích hợp luồng dữ liệu hai chiều với Website. Khi khách hàng điền form "Liên hệ tư vấn" trên Web, hệ thống tự động khởi tạo một thẻ Lead mới trong cột "Tiếp nhận" mà không cần nhập tay.
- **[FR-C03] Phân lớp và gắn thẻ khách hàng (Tagging System):** Cung cấp công cụ gắn nhãn (Tags) đa dạng để phân loại mức độ tiềm năng hoặc hạng khách hàng (Ví dụ: Khách VIP, Khách sỉ, Khách mới), giúp nhân viên kinh doanh dễ dàng lọc và lên chiến lược tiếp cận phù hợp.
- **[FR-C04] Lập lịch tác vụ và Nhắc việc tự động (Automated Activities):** Dựa trên cấu hình tự động, hệ thống sẽ tự động giao việc (Tạo Activity) cho nhân viên Sales như "Cần gọi điện lại", "Cần gửi email báo giá" mỗi khi một Lead bị di chuyển sang Stage mới.
- **[FR-C05] Kịch bản Chăm sóc qua Email tự động (Email Templates):** Hỗ trợ thiết kế sẵn các mẫu Email chuyên nghiệp. Khi Opportunity chuyển qua một bước nhất định, hệ thống cho phép kích hoạt luồng gửi email tự động kèm thông báo xác nhận đến khách hàng.

### 3.2 Yêu cầu phi chức năng (Non-Functional Requirements)

- **[NFR-01] Hiệu suất và Thời gian phản hồi (Performance):** Tối ưu hóa cơ sở dữ liệu và truy vấn để đảm bảo trang Website (Front-end) tải toàn bộ nội dung trong vòng dưới 3 giây. Đối với backend, các thao tác nặng như xác nhận (Validate) phiếu nhập/xuất kho phải phản hồi dưới 2 giây để không làm gián đoạn công việc.
- **[NFR-02] Tính khả dụng và Trải nghiệm người dùng (Usability):** Giao diện của cả Website và màn hình quản trị Odoo phải mang tính trực quan cao. Thiết kế tuân thủ nguyên tắc Mobile-first, hiển thị trơn tru, không vỡ layout trên các thiết bị có độ phân giải từ 375px trở lên (Smartphone, Tablet, Desktop).
- **[NFR-03] Bảo mật và Kiểm soát truy cập (Security & Access Rights):** Thiết lập cơ chế phân quyền (Role-based Access Control) chặt chẽ đến từng Menu. Nhân viên thuộc phân hệ Kho tuyệt đối không có quyền truy cập vào dữ liệu khách hàng (CRM) và ngược lại. Khách truy cập ẩn danh (Public User) chỉ xem được dữ liệu công khai trên Website.
- **[NFR-04] Cơ chế Sao lưu và Phục hồi (Backup & Recovery):** Cấu hình tự động sao lưu toàn bộ cơ sở dữ liệu PostgreSQL theo chu kỳ hàng ngày. Đảm bảo hệ thống có khả năng khôi phục (Restore) nguyên trạng dữ liệu một cách nhanh chóng trong trường hợp xảy ra sự cố dữ liệu.
- **[NFR-05] Ràng buộc tính nhất quán dữ liệu (Data Integrity):** Xây dựng các lớp ràng buộc dữ liệu nghiêm ngặt ở tầng Database và ORM. Đối tượng Serial Number được thiết lập thuộc tính Unique Index, bảo đảm tuyệt đối không xảy ra tình trạng một mã Serial xuất hiện hai lần trên toàn hệ thống.
- **[NFR-06] Khả năng mở rộng và Tích hợp trong tương lai (Scalability):** Hệ thống phải được thiết kế theo kiến trúc Module đặc trưng của Odoo. Các phân hệ hiện tại (CRM, Inventory, Website) hoạt động độc lập tương đối, cho phép dễ dàng cài đặt thêm các ứng dụng Kế toán, Nhân sự trong Phase 2 mà không phá vỡ cấu trúc đang có.

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
| **Luồng thay thế**   | **AF2a: Khách hàng sử dụng thanh tìm kiếm (Search bar)**<br>2a1. Tại bước 2, thay vì chọn danh mục, khách hàng gõ từ khóa trực tiếp vào thanh tìm kiếm.<br>2a2. Hệ thống truy vấn và hiển thị danh sách các sản phẩm chứa từ khóa tương ứng. |
| **Luồng ngoại lệ**   | **EF3a: Không tìm thấy sản phẩm**<br>3a1. Hệ thống không tìm thấy bất kỳ sản phẩm nào phù hợp với từ khóa tìm kiếm hoặc danh mục đã chọn.<br>3a2. Hệ thống hiển thị thông báo: "Không tìm thấy sản phẩm nào phù hợp".<br>*Usecase dừng lại.* |
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
| **Luồng thay thế**   | Không có |
| **Luồng ngoại lệ**   | **EF2a: Bỏ trống trường thông tin bắt buộc**<br>2a1. Khách hàng không điền đầy đủ các trường bắt buộc (ví dụ: Email, Số điện thoại).<br>2a2. Khi nhấn "Gửi thông tin", hệ thống hiển thị cảnh báo lỗi màu đỏ tại các trường bị thiếu.<br>2a3. Hệ thống ngăn chặn việc gửi form và yêu cầu khách hàng bổ sung.<br>*Usecase dừng lại.* |
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
| **Luồng thay thế**   | **AF3a: Import Serial Number bằng file Excel**<br>3a1. Tại bước 3, thay vì nhập thủ công, nhân viên chọn tính năng Import Excel.<br>3a2. Nhân viên tải lên file Excel chứa danh sách các mã Serial cần nhập.<br>3a3. Hệ thống tự động đọc và gán hàng loạt mã Serial vào phiếu nhập. |
| **Luồng ngoại lệ**   | **EF3a: Nhập trùng mã Serial Number đã tồn tại**<br>3a1. Hệ thống phát hiện mã Serial vừa nhập đã tồn tại trong kho dữ liệu.<br>3a2. Hệ thống hiển thị thông báo lỗi Duplicate (Trùng lặp dữ liệu).<br>3a3. Hệ thống ngăn chặn bước "Validate" và yêu cầu nhân viên kiểm tra lại mã Serial.<br>*Usecase dừng lại.* |
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
| **Luồng thay thế**   | **AF3a: Tự động chỉ định Serial Number (Auto Assign)**<br>3a1. Tại bước 3, nhân viên Kho nhấn nút "Auto Assign" thay vì chọn thủ công.<br>3a2. Hệ thống Odoo tự động lựa chọn các mã Serial nhập kho cũ nhất (theo nguyên tắc FIFO) để xuất. |
| **Luồng ngoại lệ**   | **EF3a: Mã Serial Number không có sẵn trong kho**<br>3a1. Nhân viên quét hoặc nhập một mã Serial không tồn tại ở vị trí kho hiện tại.<br>3a2. Hệ thống hiển thị cảnh báo lỗi và không ghi nhận mã Serial đó vào phiếu xuất.<br>3a3. Hệ thống ngăn chặn việc "Validate" phiếu xuất.<br>*Usecase dừng lại.* |
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
| **Luồng thay thế**   | Không có |
| **Luồng ngoại lệ**   | **EF4a: Không có quyền truy cập Vị trí đích**<br>4a1. Tại bước 4, hệ thống kiểm tra và phát hiện vị trí đích (Destination Location) đang bị khóa hoặc nhân viên không đủ thẩm quyền.<br>4a2. Hệ thống hiển thị thông báo lỗi Access Error.<br>4a3. Hệ thống hủy bỏ thao tác chuyển kho.<br>*Usecase dừng lại.* |
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
| **Luồng thay thế**   | Không có |
| **Luồng ngoại lệ**   | **EF2a: Mã Serial Number không hợp lệ hoặc không tồn tại**<br>2a1. Người dùng nhập sai định dạng hoặc mã Serial chưa từng được ghi nhận trên hệ thống.<br>2a2. Hệ thống không tìm thấy dữ liệu và hiển thị danh sách rỗng.<br>*Usecase dừng lại.* |
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
| **Luồng thay thế**   | **AF3a: Xem báo cáo dưới dạng biểu đồ (Graph) hoặc Pivot**<br>3a1. Tại bước 3, thay vì xem dạng danh sách (List), người dùng chuyển sang góc nhìn Pivot hoặc Graph.<br>3a2. Hệ thống hiển thị báo cáo phân tích trực quan theo dạng biểu đồ cột, tròn hoặc bảng tổng hợp. |
| **Luồng ngoại lệ**   | Không có |
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
| **Luồng thay thế**   | **AF3a: Đánh dấu Won/Lost trực tiếp**<br>3a1. Tại bước 3, nhân viên không kéo thả qua từng bước mà click trực tiếp vào nút "Mark Won" (Thành công) hoặc "Mark Lost" (Thất bại).<br>3a2. Nếu chọn "Mark Lost", hệ thống yêu cầu nhập lý do thất bại.<br>3a3. Hệ thống lập tức chuyển trạng thái Lead sang đóng (Closed) mà không cần đi qua các stage trung gian. |
| **Luồng ngoại lệ**   | Không có |
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
| **Luồng thay thế**   | **AF3a: Chăm sóc khách hàng qua Email**<br>3a1. Tại bước 3, thay vì gọi điện thoại, nhân viên chọn tính năng "Send Message" ngay trong khung Log của Lead.<br>3a2. Nhân viên soạn nội dung hoặc chọn Email Template có sẵn và nhấn Gửi.<br>3a3. Hệ thống lưu lại lịch sử email và tự động đánh dấu hoàn thành Activity hiện tại. |
| **Luồng ngoại lệ**   | **EF2a: Tác vụ chăm sóc (Activity) bị quá hạn**<br>2a1. Nhân viên mở hệ thống nhưng đã vượt qua thời hạn xử lý Activity.<br>2a2. Hệ thống đổi màu biểu tượng nhắc việc sang màu Đỏ để cảnh báo mức độ trễ hạn.<br>2a3. Nhân viên buộc phải xử lý ngay hoặc lên lịch lại kèm theo lý do chậm trễ. |
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
| **Luồng thay thế**   | **AF4a: In Báo giá ra giấy (Print PDF)**<br>4a1. Tại bước 4, thay vì chọn "Send by Email", nhân viên nhấn nút "Print PDF".<br>4a2. Hệ thống kết xuất file báo giá định dạng PDF tải về máy.<br>4a3. Nhân viên in ra giấy và gửi trực tiếp cho khách hàng. |
| **Luồng ngoại lệ**   | **EF3a: Thêm sản phẩm đang hết hàng (Out of Stock)**<br>3a1. Tại bước 3, nhân viên thêm một sản phẩm hiện có số lượng tồn kho bằng 0.<br>3a2. Hệ thống Odoo hiển thị cảnh báo màu đỏ (biểu tượng chấm than) ngay cạnh tên sản phẩm.<br>3a3. Nhân viên vẫn có thể tạo báo giá nhưng cần báo trước với khách về thời gian đặt hàng (Lead time). |
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
| **Luồng thay thế**   | **AF1a: Import danh mục sản phẩm từ Excel**<br>1a1. Tại bước 1, quản trị viên chọn tính năng "Import Records" thay vì tạo thủ công.<br>1a2. Tải lên file dữ liệu Excel chuẩn chứa hàng loạt sản phẩm thiết bị.<br>1a3. Hệ thống tự động tạo mới hàng loạt sản phẩm cùng các thiết lập tương ứng. |
| **Luồng ngoại lệ**   | **EF3a: Bỏ sót cấu hình Serial Tracking**<br>3a1. Tại bước 3, người khởi tạo quên chọn Tracking "By Unique Serial Number" mà để mặc định (No Tracking).<br>3a2. Hệ thống vẫn lưu sản phẩm thành công.<br>3a3. Hậu quả: Khi nhập kho, nhân viên sẽ không có trường nhập mã Serial. Bắt buộc Admin phải quay lại sửa cấu hình sản phẩm trước khi nhập kho. |
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
| **Luồng thay thế**   | **AF4a: Chủ động cấp mật khẩu (Change Password)**<br>4a1. Tại bước 4, thay vì nhấn gửi Email mời, Admin chọn "Action" > "Change Password".<br>4a2. Admin nhập mật khẩu khởi tạo trực tiếp cho nhân viên.<br>4a3. Nhân viên có thể đăng nhập ngay lập tức bằng mật khẩu Admin cung cấp. |
| **Luồng ngoại lệ**   | **EF3a: Phân quyền sai chức vụ**<br>3a1. Tại bước 3, Admin sơ suất cấp quyền hạn cao hơn mức cần thiết cho nhân viên.<br>3a2. Nhân viên có thể truy cập và xem được dữ liệu nhạy cảm của phòng ban khác (Ví dụ: xem doanh thu, giá nhập kho).<br>3a3. Phát sinh rủi ro bảo mật nội bộ, Admin phải ngay lập tức rà soát và gỡ bỏ quyền dư thừa. |
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
