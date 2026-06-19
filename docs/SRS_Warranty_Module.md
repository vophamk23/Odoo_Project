# Tài Liệu Đặc Tả Yêu Cầu Phần Mềm (SRS)
**Dự án:** Hệ thống Quản lý Khách hàng & Hậu mãi (Phase 2)
**Module:** Quản lý Bảo Hành (cmcts_warranty)

---

## 1. Giới thiệu Tổng quan

### 1.1 Mục đích và Giá trị Cốt lõi của Module
Module **Quản lý Bảo Hành (Warranty Management)** được xây dựng nhằm giải quyết triệt để bài toán quản lý dịch vụ hậu mãi thủ công bằng sổ sách và Excel. Bằng việc tích hợp trực tiếp vào hệ sinh thái Odoo 18, module mang lại những giá trị cốt lõi sau:
- **Số hóa toàn diện dữ liệu bảo hành:** Khởi tạo hồ sơ số cho từng thiết bị bán ra, gắn liền với số Serial/Lô độc nhất, liên kết chặt chẽ với đơn hàng bán (Sales Order) và dữ liệu kho (Inventory).
- **Chuẩn hóa quy trình sửa chữa (RMA - Return Merchandise Authorization):** Tạo ra một luồng làm việc khép kín từ lúc khách hàng mang máy đến (Tiếp nhận) -> Phân công Kỹ thuật viên (Xử lý) -> Sửa chữa xong (Hoàn tất) hoặc từ chối do vi phạm quy định bảo hành.
- **Tự động hóa thông minh:** Tích hợp các hàm tính toán (Compute fields) và tiến trình chạy ngầm (Cronjobs) giúp hệ thống tự động cập nhật trạng thái phiếu hết hạn mỗi đêm, tự động đếm số lần máy bị hỏng, giảm thiểu tối đa sai sót do con người.

### 1.2 Đối tượng Phục vụ (Stakeholders) và Lợi ích
- **Ban Giám đốc / Quản lý Cấp cao:** Nắm bắt được biểu đồ tỷ lệ máy lỗi theo từng dòng sản phẩm, giám sát được hiệu suất xử lý (SLA) của bộ phận kỹ thuật để có chiến lược kinh doanh phù hợp.
- **Nhân viên Tiếp nhận (Receptionist / Cửa hàng trưởng):** Tiết kiệm 80% thời gian tra cứu. Khi khách mang máy tới, chỉ cần gõ số Serial là hệ thống sẽ báo ngay máy còn hạn bảo hành hay không, đã từng thay linh kiện gì trong quá khứ.
- **Kỹ thuật viên (Technician):** Được cấp tài khoản riêng biệt với giao diện tinh gọn. Chỉ nhìn thấy các phiếu việc mình được giao, có ô nhập liệu rõ ràng để ghi chú tình trạng hỏng hóc, linh kiện cần thay thế.
- **Khách hàng cuối (End-Users):** Được hưởng dịch vụ hậu mãi chuyên nghiệp, nhanh chóng và minh bạch nhờ quy trình nội bộ của công ty đã được trơn tru hóa.

---

## 2. Phân tích Chi tiết Người Dùng Hệ Thống (Actors)

Hệ thống thiết lập cơ chế phân quyền bảo mật chặt chẽ dành cho 3 nhóm đối tượng (Actor) biệt lập:

1. **Admin (Quản trị viên Hệ thống):** 
   - Có toàn quyền truy cập sâu vào cấu hình Database.
   - Chịu trách nhiệm tạo tài khoản cho nhân viên mới, thiết lập phân quyền (Gán user vào nhóm Tiếp nhận hoặc Kỹ thuật viên).
   - Kiểm soát Cronjob và các cấu hình kỹ thuật cấp thấp.

2. **Nhân viên tiếp nhận (Manager - Nhóm Quản lý Bảo hành):**
   - **Đặc quyền:** Sở hữu quyền cao nhất trong luồng nghiệp vụ bảo hành (Full CRUD: Create, Read, Update, Delete).
   - **Nhiệm vụ:** Tạo Phiếu bảo hành mới khi xuất kho thành công. Tạo mới các "Yêu cầu sửa chữa" khi khách mang máy lỗi đến. Là người phân công (Assign) Yêu cầu sửa chữa đó cho một Kỹ thuật viên cụ thể. Có quyền chỉnh sửa sai sót hoặc xóa các bản nháp nếu nhập sai.

3. **Kỹ thuật viên (Technician - Nhóm Nhân viên Bảo hành):**
   - **Đặc quyền:** Quyền hạn bị giới hạn ở mức cơ bản để đảm bảo an toàn dữ liệu gốc.
   - **Nhiệm vụ:** Chỉ được cấp quyền Xem (Read-only) trên danh sách Phiếu bảo hành gốc để tra cứu cấu hình máy. Đối với Yêu cầu sửa chữa (Claim), KTV chỉ được phép Cập nhật trạng thái (Từ "Tiếp nhận" sang "Đang xử lý") và điền ghi chú sửa chữa trên những Phiếu mà mình được chỉ định. Tuyệt đối không có quyền Tạo mới hay Xóa dữ liệu.

---

## 3. Cấu trúc Dữ liệu Chi tiết (Data Dictionary)

Hệ thống được thiết kế tối ưu với 2 thực thể chính mang quan hệ 1-N (Một phiếu bảo hành có thể có nhiều lần đem đi sửa). Cả 2 bảng đều được kế thừa `mail.thread` để ghi log lịch sử thay đổi (Chatter).

### 3.1 Bảng Phiếu Bảo Hành (`cmcts_warranty.warranty`)
Đóng vai trò là "Sổ hộ khẩu" của mỗi thiết bị.
- `name` (Char, readonly): Mã số phiếu định danh duy nhất (Format: WH/0001) được sinh tự động bằng Sequence.
- `product_id` (Many2one, required): Trỏ đến bảng danh mục `product.product`.
- `lot_id` (Many2one, required): Trỏ đến bảng `stock.lot`. Được thiết lập ràng buộc Unique (Duy nhất) để không có 2 phiếu bảo hành trên cùng 1 số Serial.
- `partner_id` (Many2one, required): Trỏ đến thông tin khách hàng `res.partner`.
- `sale_order_id` (Many2one): Liên kết đến đơn mua hàng gốc `sale.order`.
- `sale_date` (Date, default=today): Ngày xuất bán, làm mốc tính thời gian.
- `warranty_months` (Integer, default=12): Số tháng được bảo hành.
- `expiry_date` (Date, compute, store): Hàm `@api.depends` tự động cộng `sale_date` với `warranty_months` để ra ngày hết hạn.
- `state` (Selection): 3 trạng thái tĩnh (`valid`: Còn hiệu lực, `expired`: Hết hạn, `cancelled`: Đã hủy). Trường này bật `tracking=True` để lưu lịch sử khi hệ thống chạy cronjob chuyển trạng thái.
- `claim_count` (Integer, compute): Đếm tổng số lượng bản ghi `warranty.claim` liên kết với phiếu này để hiển thị lên Smart Button.

### 3.2 Bảng Yêu Cầu Sửa Chữa (`cmcts_warranty.warranty.claim`)
Ghi nhận cụ thể từng sự cố phát sinh trong quá trình sử dụng của khách hàng.
- `name` (Char, readonly): Mã số phiếu sửa chữa (Format: CLM/0001).
- `warranty_id` (Many2one, required): Khóa ngoại bắt buộc trỏ về bảng Phiếu bảo hành gốc.
- `technician_id` (Many2one): Kỹ thuật viên được giao việc. Trường này sử dụng thuộc tính `domain` để danh sách sổ xuống chỉ hiển thị những User thuộc nhóm "Kỹ thuật viên".
- `received_date` (Date, default=today): Ngày tiếp nhận máy lỗi.
- `return_date` (Date): Ngày hẹn trả máy cho khách. Ràng buộc Validation bắt buộc `return_date` >= `received_date`.
- `issue_description` (Text, required): Tình trạng máy lúc nhận (Khách báo lỗi gì, ngoại hình trầy xước ra sao).
- `resolution_note` (Text): Báo cáo kỹ thuật (KTV đã thay linh kiện gì, nguyên nhân lỗi do đâu).
- `state` (Selection): Biến trạng thái quy trình với 4 bước bắt buộc. Bật `tracking=True` để quản lý xem ai chuyển trạng thái lúc mấy giờ.

---

## 4. Sơ Đồ Chuyển Trạng Thái và Khóa Dữ Liệu (State Machine & Readonly Logic)

Luồng trạng thái của **Yêu Cầu Sửa Chữa (Claim)** tuân thủ nguyên tắc "Tiến tới" (Forward-only) để phản ánh đúng thực tế sửa chữa vật lý:

```text
[ 1_received ] (Mới tiếp nhận: KTV chuẩn bị mở máy)
      │
      ├── (Bắt đầu làm)  → [ 2_processing ] (Đang sửa chữa: Đang tháo máy, chờ linh kiện)
      │
      ├── (Test OK)      → [ 3_done ]       (Hoàn thành: Đã lắp lại, test OK, chờ khách lấy)
      │
      └── (Từ chối)      → [ 4_rejected ]   (Từ chối: Khách làm rơi vỡ, vào nước, rách tem)
```

**Các Quy tắc Ràng buộc (Business Logic Constraints):**
1. **Validation chặn lùi quy trình:** Sử dụng hàm `@api.constrains('state')`. Hệ thống sẽ quăng lỗi (UserError) nếu người dùng cố tình chuyển trạng thái từ `3_done` (Hoàn thành) ngược về `1_received` hoặc `2_processing`.
2. **Khóa cứng dữ liệu (Readonly UI):** Trên file XML (Giao diện Form), hệ thống sử dụng thuộc tính `readonly="state in ['3_done', '4_rejected']"`. Khi phiếu đạt trạng thái cuối cùng, giao diện sẽ mờ đi và khóa toàn bộ các trường nhập liệu. Không ai có thể sửa đổi nội dung phiếu (ngay cả Tiếp nhận) nhằm đảm bảo bằng chứng lịch sử (Audit trail).

---

## 5. Ma trận Phân Quyền Chi Tiết (Access Rights & Record Rules)

Bảo mật là yếu tố then chốt. Module áp dụng hệ thống phân quyền 2 lớp cực kỳ chặt chẽ của Odoo: Lớp Object (ir.model.access) và Lớp Record (ir.rule).

### 5.1 Cấp độ Bảng dữ liệu (ir.model.access.csv)
| Model / Chức năng | Nhóm: Kỹ thuật viên (User) | Nhóm: Tiếp nhận (Manager) |
| :--- | :---: | :---: |
| **Bảng Phiếu bảo hành gốc (warranty)** | Chỉ Đọc `[1, 0, 0, 0]` | Toàn Quyền `[1, 1, 1, 1]` |
| **Bảng Yêu cầu sửa chữa (claim)** | Đọc & Sửa `[1, 1, 0, 0]` | Toàn Quyền `[1, 1, 1, 1]` |

### 5.2 Cấp độ Dòng dữ liệu (Record Rules - warranty_rules.xml)
Để tránh tình trạng nhân viên kỹ thuật A vào sửa hoặc xem trộm kết quả sửa chữa của nhân viên kỹ thuật B, hệ thống áp dụng bộ lọc dòng dữ liệu (Domain Filter):
- **Luật của Tiếp nhận:** `[(1, '=', 1)]` -> Có quyền nhìn thấy và thao tác trên mọi Phiếu của toàn công ty.
- **Luật của Kỹ thuật viên:** `['|', ('technician_id', '=', False), ('technician_id', '=', user.id)]` -> KTV chỉ được phép nhìn thấy và thao tác (Sửa) các phiếu sửa chữa **chưa được phân công cho ai** hoặc **đã được phân công đích danh cho tài khoản của họ**.

**Kết luận Bảo mật:** Kiến trúc bảo mật đa tầng này giúp module sẵn sàng triển khai thực tế tại các trung tâm bảo hành có quy mô hàng trăm nhân sự mà không lo ngại vấn đề rò rỉ hay phá hoại dữ liệu.

### 5.3 Bảng Tổng hợp Quyền hạn Thực tế trên Giao diện (UI Access Matrix)
Sự kết hợp giữa Access Rights và Record Rules tạo ra kết quả phân quyền thực tế trên màn hình của người dùng như sau:

| Thao tác trên phần mềm | User Không phân quyền | User Kỹ thuật viên | User Quản lý / Tiếp nhận |
| :--- | :---: | :--- | :--- |
| **Thấy Menu "Bảo Hành" trên App** | ❌ Chặn | ✅ Có thể truy cập | ✅ Có thể truy cập |
| **Tạo mới Phiếu Bảo Hành** | ❌ Chặn | ❌ Chặn (Ẩn nút Create) | ✅ Toàn quyền |
| **Sửa Phiếu Bảo Hành** | ❌ Chặn | ❌ Chặn (Readonly) | ✅ Toàn quyền |
| **Tạo mới Yêu Cầu Sửa Chữa** | ❌ Chặn | ❌ Chặn (Ẩn nút Create) | ✅ Toàn quyền |
| **Xem danh sách Yêu Cầu Sửa Chữa** | ❌ Chặn | ⚠️ Chỉ thấy phiếu của mình & phiếu chưa ai nhận | ✅ Thấy toàn bộ phiếu |
| **Sửa Yêu Cầu Sửa Chữa (Ghi chú, Đổi trạng thái)** | ❌ Chặn | ⚠️ Chỉ sửa được phiếu do mình phụ trách | ✅ Toàn quyền |
| **Xóa dữ liệu (Nút Delete)** | ❌ Chặn | ❌ Chặn (Báo lỗi AccessError) | ✅ Toàn quyền |
