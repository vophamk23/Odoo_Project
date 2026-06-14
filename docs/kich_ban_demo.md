# 🎭 KỊCH BẢN DEMO HỆ THỐNG ODOO (PHASE 1)
> Tài liệu này hướng dẫn chi tiết từng bước thao tác để trình diễn toàn bộ quy trình nghiệp vụ từ lúc tiếp cận khách hàng trên Website, xử lý cơ hội bán hàng bằng CRM, cho đến khâu quản lý kho và xuất nhập hàng hóa theo số Serial.

---

## 🟢 PHẦN 1: QUY TRÌNH KINH DOANH (WEB ➡️ CRM ➡️ CHỐT ĐƠN)

Quy trình này trình diễn khả năng tự động hóa và luồng chảy dữ liệu liền mạch từ người dùng ẩn danh trên web thành một đơn hàng chính thức.

### Bước 1: Khách hàng truy cập và Đăng ký tư vấn
1. Mở trình duyệt ở chế độ **Ẩn danh (Incognito)** để đóng vai Khách hàng.
2. Truy cập vào đường link: `http://localhost:8069/tu-van`
3. Tại giao diện Form Đăng ký, điền các thông tin giả lập:
   - **Họ và tên:** `Nguyễn Khách VIP`
   - **Số điện thoại:** `0988.123.456`
   - **Email:** `khachvip@gmail.com`
   - **Giải pháp quan tâm:** Chọn `Hạ tầng Server & Máy chủ`
   - **Nhu cầu:** `Cần mua 10 máy chủ cấu hình cao và 1 hệ thống lưu trữ NAS.`
4. Bấm nút **Gửi Đăng Ký**. Màn hình sẽ chuyển sang trang "Cảm ơn".

### Bước 2: Hệ thống chạy ngầm (Automation)
Ngay lúc này, code Python đã cấy trong hệ thống sẽ tự động thực hiện 3 việc:
- **(1)** Đẩy thẳng dữ liệu vào CRM tạo thành 1 Lead mới.
- **(2)** Gửi 1 email thông báo nội bộ cho team Sales.
- **(3)** Gửi 1 email xác nhận và cảm ơn đến địa chỉ `khachvip@gmail.com`.
*(Demo email: Mở Cài đặt -> Kỹ thuật -> Email -> Thư để cho khách/thầy giáo xem giao diện HTML của email).*

### Bước 3: Sales tiếp nhận và Xử lý Cơ hội (CRM)
1. Thu nhỏ tab ẩn danh lại, quay về trình duyệt chính (Tài khoản Admin).
2. Vào ứng dụng **CRM**. Tại cột đầu tiên **Mới (New)**, bạn sẽ thấy xuất hiện một thẻ ghi: `Website Lead - Nguyễn Khách VIP`.
3. Bấm vào thẻ đó để xem chi tiết. Toàn bộ SĐT, Email, Nhu cầu đều đã được điền sẵn chính xác 100%.
4. **Kéo thả thẻ Lead** từ cột `Mới` sang các cột `Đang đánh giá` ➡️ `Đã gửi báo giá`.

### Bước 4: Tạo Báo giá và Chốt đơn
1. Ngay bên trong thẻ Lead của `Nguyễn Khách VIP`, bấm nút **Tạo Báo Giá (New Quotation)**.
2. Tại bảng Chi tiết đơn hàng, bấm `Thêm sản phẩm` -> Chọn `Apple MacBook Pro M4 Pro` -> Số lượng: `1`.
3. Bấm nút **Xác nhận (Confirm)**. 
4. Lúc này, Báo giá đã biến thành **Đơn Bán Hàng (Sale Order)**. Cùng lúc đó, hệ thống sinh ra một **Phiếu Giao Hàng** kết nối thẳng xuống Kho (xuất hiện biểu tượng chiếc Xe tải góc phải trên cùng).

---

## 🔵 PHẦN 2: QUY TRÌNH KHO VẬN (SẢN PHẨM ➡️ NHẬP ➡️ CHUYỂN ➡️ XUẤT)

Phần này trình diễn khả năng quản lý kho chính xác đến từng thiết bị duy nhất thông qua Serial Number, chống thất thoát hàng hóa.

### Bước 1: Khởi tạo Sản phẩm và bật Serial
1. Vào ứng dụng **Kho vận (Inventory)** ➡️ Menu **Sản phẩm (Products)**.
2. Bấm nút **Mới (New)** để tạo sản phẩm.
   - **Tên:** `Máy chủ Dell PowerEdge R750`
   - **Loại sản phẩm:** `Sản phẩm lưu kho (Storable Product)`
3. Chuyển sang tab **Kho vận (Inventory)**.
4. Kéo xuống phần **Truy xuất nguồn gốc (Traceability)** -> Tích chọn **Theo Số seri duy nhất (By Unique Serial Number)**.
5. Bấm biểu tượng đám mây để **Lưu**.

### Bước 2: Nhập hàng từ Nhà cung cấp
1. Vẫn ở ứng dụng Kho vận, quay ra Bảng điều khiển (Tổng quan).
2. Tại thẻ **Nhận hàng (Receipts)**, bấm **dấu 3 chấm** -> Chọn **Mới (Mới)**.
3. Điền thông tin:
   - **Nhận từ:** `Nhà cung cấp Dell Việt Nam`
   - **Sản phẩm:** Chọn `Máy chủ Dell PowerEdge R750`
   - **Nhu cầu (Demand):** Điền số `2` (Nhập 2 cái).
4. Khai báo Serial Number:
   - Bấm vào biểu tượng **Tùy chọn chi tiết (Detail Operations)** ở ngay cuối dòng sản phẩm (Biểu tượng danh sách 3 gạch).
   - Thêm 2 dòng và gõ tay 2 số Serial: `DELL-R750-001` và `DELL-R750-002`.
5. Bấm **Xác nhận (Validate)**. Hai chiếc máy chủ với mã Serial cụ thể đã nằm gọn trong Kho tổng (`WH/Stock`).

### Bước 3: Dịch chuyển nội bộ (Chuyển kho)
1. Quay ra Bảng điều khiển. Thẻ **Dịch chuyển nội bộ (Internal Transfers)** -> Bấm tạo **Mới**.
2. Thiết lập dịch chuyển:
   - **Từ:** Kho Tổng (`WH/Stock`)
   - **Đến:** Kho Trưng Bày (`WH/Showroom` hoặc tạo một Virtual Location).
3. Bấm thêm sản phẩm `Máy chủ Dell PowerEdge R750`. Nhu cầu: `1`.
4. Bấm biểu tượng Chi tiết, phần mềm sẽ ép bạn phải chọn chính xác mã Serial cần chuyển. Bạn chọn mã `DELL-R750-001`.
5. Bấm **Xác nhận (Validate)**. Lúc này máy `001` đã chuyển sang kho Showroom, máy `002` vẫn nằm ở kho Tổng.

### Bước 4: Xuất kho giao khách (Kết thúc chu trình)
1. Quay lại ứng dụng **Bán hàng (Sales)** hoặc **CRM**, mở lại cái Đơn Bán Hàng của anh `Nguyễn Khách VIP` ban nãy (Giả sử ảnh mua Máy chủ Dell thay vì Macbook).
2. Bấm vào biểu tượng chiếc **Xe tải (Giao hàng - Delivery)**.
3. Trong phiếu xuất kho, bạn sẽ không thể bấm Xác nhận ngay. Hệ thống yêu cầu nhân viên kho phải quét hoặc điền đúng mã Serial của cái máy xuất đi.
4. Bấm biểu tượng Chi tiết ở dòng sản phẩm -> Chỗ **Số Seri/Lô**, bạn chọn mã `DELL-R750-002` (Vì máy 001 đã mang đi trưng bày).
5. Bấm **Xác nhận (Validate)**.

🎉 **KẾT QUẢ:**
- Giao dịch hoàn tất. 
- Mở danh sách Serial Number, bạn sẽ thấy máy `001` đang ở Showroom, còn máy `002` có trạng thái "Đã chuyển cho khách hàng". Không ai có thể gian lận hay tráo đổi được hàng của công ty!
