# Test Cases Toàn Bộ Hệ Thống (Phase 1)

Dưới đây là đặc tả kịch bản kiểm thử (Test Cases) chi tiết cho từng luồng nghiệp vụ.

## 1. Nhóm KHO (Inventory)

#### TC-K01: Nhập kho với serial mới hợp lệ

| Trường thông tin    | Chi tiết                                                                                                                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Test Case ID**    | TC-K01                                                                                                                                                                                            |
| **Description**     | Kiểm tra việc nhập một thiết bị mới vào kho và gán mã Serial Number hoàn toàn mới.                                                                                                                |
| **Pre-conditions**  | Sản phẩm đã được tạo và cấu hình "Tracking by Unique Serial Number". Mã Serial chuẩn bị nhập chưa từng tồn tại trên hệ thống.                                                                     |
| **Steps**           | 1. Tạo phiếu Nhập kho (Receipts).<br>2. Thêm dòng sản phẩm tương ứng.<br>3. Mở Detailed Operations và nhập mã Serial mới cùng số lượng 1.<br>4. Nhấn nút Validate để xác nhận.                    |
| **Expected Result** | Phiếu chuyển sang trạng thái "Done". Số lượng tồn kho (On Hand) của sản phẩm tăng lên 1. Mã Serial mới xuất hiện trong danh sách Lots/Serial Numbers với trạng thái "In Stock" tại đúng kho đích. |
| **Actual Result**   |                                                                                                                                                                                                   |
| **Status**          |                                                                                                                                                                                                   |
| **Comments**        |                                                                                                                                                                                                   |

#### TC-K02: Nhập kho với serial đã tồn tại

| Trường thông tin    | Chi tiết                                                                                                                                                   |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Test Case ID**    | TC-K02                                                                                                                                                     |
| **Description**     | Kiểm tra hệ thống có ngăn chặn việc nhập trùng lặp một mã Serial đã có trong kho hay không.                                                                |
| **Pre-conditions**  | Có ít nhất 1 mã Serial đang "On Hand" trong kho.                                                                                                           |
| **Steps**           | 1. Tạo phiếu Nhập kho (Receipts).<br>2. Thêm sản phẩm và điền mã Serial ĐÃ TỒN TẠI vào ô Serial.<br>3. Nhấn nút Validate.                                  |
| **Expected Result** | Hệ thống hiển thị thông báo lỗi "Serial Number already exists" (hoặc tương tự). Phiếu nhập không được xác nhận (Validate bị chặn). Tồn kho không thay đổi. |
| **Actual Result**   |                                                                                                                                                            |
| **Status**          |                                                                                                                                                            |
| **Comments**        |                                                                                                                                                            |

#### TC-K03: Xuất kho đúng serial đã chọn

| Trường thông tin    | Chi tiết                                                                                                                                                                                           |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Test Case ID**    | TC-K03                                                                                                                                                                                             |
| **Description**     | Kiểm tra quy trình xuất đúng hàng hóa thực tế bằng cách chỉ định Serial cụ thể.                                                                                                                    |
| **Pre-conditions**  | Kho đang có sẵn hàng (On Hand > 0) và có Serial tương ứng.                                                                                                                                         |
| **Steps**           | 1. Tạo phiếu Xuất kho (Delivery).<br>2. Thêm sản phẩm và bấm Check Availability.<br>3. Mở Detailed Operations, chọn đích danh mã Serial có sẵn trong danh sách thả xuống.<br>4. Nhấn nút Validate. |
| **Expected Result** | Phiếu chuyển sang trạng thái "Done". Mã Serial đó không còn nằm trong kho (On Hand giảm đúng 1 đơn vị). Trong lịch sử Serial đó ghi nhận thông tin khách hàng nhận hàng.                           |
| **Actual Result**   |                                                                                                                                                                                                    |
| **Status**          |                                                                                                                                                                                                    |
| **Comments**        |                                                                                                                                                                                                    |

#### TC-K04: Chuyển kho nội bộ

| Trường thông tin    | Chi tiết                                                                                                                                                               |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Test Case ID**    | TC-K04                                                                                                                                                                 |
| **Description**     | Kiểm tra việc luân chuyển một mã Serial từ vị trí này sang vị trí khác trong cùng kho.                                                                                 |
| **Pre-conditions**  | Có sẵn một mã Serial tại Vị trí nguồn (Source Location). Vị trí đích đã được tạo và không bị khóa.                                                                     |
| **Steps**           | 1. Tạo phiếu Internal Transfer.<br>2. Chọn Source Location và Destination Location hợp lệ.<br>3. Chọn sản phẩm và chọn mã Serial cần luân chuyển.<br>4. Nhấn Validate. |
| **Expected Result** | Mã Serial biến mất ở Vị trí nguồn và xuất hiện tại Vị trí đích. Tổng số lượng tồn kho công ty không thay đổi. Phiếu chuyển kho ở trạng thái "Done".                    |
| **Actual Result**   |                                                                                                                                                                        |
| **Status**          |                                                                                                                                                                        |
| **Comments**        |                                                                                                                                                                        |

#### TC-K05: Tra cứu lịch sử serial đầy đủ

| Trường thông tin    | Chi tiết                                                                                                                                                                                                    |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Test Case ID**    | TC-K05                                                                                                                                                                                                      |
| **Description**     | Kiểm tra tính năng truy xuất nguồn gốc (Traceability) của một mã Serial đã trải qua nhiều bước.                                                                                                             |
| **Pre-conditions**  | Chọn một mã Serial đã từng Nhập kho, Chuyển nội bộ và Xuất kho (thực hiện TC-K01, TC-K04, TC-K03 theo thứ tự trước).                                                                                        |
| **Steps**           | 1. Truy cập vào menu Lots/Serial Numbers.<br>2. Tìm kiếm mã Serial đó và mở chi tiết.<br>3. Nhấn vào nút "Traceability" (hoặc Truy vết).                                                                    |
| **Expected Result** | Hệ thống hiển thị sơ đồ dạng cây (tree view) liệt kê đầy đủ cả 3 bước dịch chuyển: Phiếu nhập gốc → Phiếu chuyển kho → Phiếu xuất kho cuối cùng. Mỗi bước ghi rõ ngày giờ thực hiện và tên phiếu tương ứng. |
| **Actual Result**   |                                                                                                                                                                                                             |
| **Status**          |                                                                                                                                                                                                             |
| **Comments**        |                                                                                                                                                                                                             |

#### TC-K06: Kiểm kê và điều chỉnh tồn kho

| Trường thông tin    | Chi tiết                                                                                                                                                                                                                                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Test Case ID**    | TC-K06                                                                                                                                                                                                                                                                                                              |
| **Description**     | Kiểm tra chức năng kiểm kê kho khi phát hiện chênh lệch giữa số liệu thực tế và hệ thống.                                                                                                                                                                                                                           |
| **Pre-conditions**  | Kho đang có tồn kho của ít nhất 1 sản phẩm theo Serial Number.                                                                                                                                                                                                                                                      |
| **Steps**           | 1. Vào Inventory > Physical Inventory.<br>2. Tìm sản phẩm cần kiểm kê, ghi nhận số lượng hệ thống đang hiển thị.<br>3. Nhập số lượng thực tế vào cột "Counted Quantity" (nhập khác với số hệ thống để tạo chênh lệch).<br>4. Nhập lý do điều chỉnh vào phần ghi chú.<br>5. Nhấn "Apply All" để xác nhận điều chỉnh. |
| **Expected Result** | Tồn kho cập nhật đúng theo số lượng thực tế vừa nhập. Hệ thống tạo bút toán điều chỉnh (Inventory Adjustment) lưu lại ngày giờ và lý do thay đổi.                                                                                                                                                                   |
| **Actual Result**   |                                                                                                                                                                                                                                                                                                                     |
| **Status**          |                                                                                                                                                                                                                                                                                                                     |
| **Comments**        |                                                                                                                                                                                                                                                                                                                     |

---

## 2. Nhóm WEBSITE

#### TC-W01: Submit form tư vấn đủ thông tin

| Trường thông tin    | Chi tiết                                                                                                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Test Case ID**    | TC-W01                                                                                                                                                                                     |
| **Description**     | Đảm bảo khách hàng gửi thành công yêu cầu tư vấn nếu điền đủ thông tin.                                                                                                                    |
| **Pre-conditions**  | Website đang hoạt động, truy cập được trang `/tu-van`.                                                                                                                                     |
| **Steps**           | 1. Vào đường dẫn `/tu-van`.<br>2. Điền đầy đủ các trường bắt buộc (Tên, Email, Điện thoại).<br>3. Nhấn Submit.                                                                             |
| **Expected Result** | Màn hình chuyển sang trang thông báo Cảm ơn (Thank you). CRM ghi nhận một Lead mới chứa đầy đủ thông tin khách vừa điền (Tên, Email, SĐT khớp 100%). Lead nằm ở stage "Tiếp nhận yêu cầu". |
| **Actual Result**   |                                                                                                                                                                                            |
| **Status**          |                                                                                                                                                                                            |
| **Comments**        |                                                                                                                                                                                            |

#### TC-W02: Submit form thiếu Email (bắt buộc)

| Trường thông tin    | Chi tiết                                                                                                           |
| ------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Test Case ID**    | TC-W02                                                                                                             |
| **Description**     | Kiểm tra hệ thống validation của form liên hệ để tránh spam hoặc thiếu thông tin liên lạc.                         |
| **Pre-conditions**  | Website đang hoạt động. Trường Email được cấu hình là bắt buộc.                                                    |
| **Steps**           | 1. Vào trang `/tu-van`.<br>2. Bỏ trống trường Email, điền các trường còn lại.<br>3. Nhấn Submit.                   |
| **Expected Result** | Form không được gửi đi. Trình duyệt hiển thị cảnh báo đỏ yêu cầu nhập Email. Không có Lead nào được tạo trong CRM. |
| **Actual Result**   |                                                                                                                    |
| **Status**          |                                                                                                                    |
| **Comments**        |                                                                                                                    |

#### TC-W03: Email thông báo sau submit

| Trường thông tin    | Chi tiết                                                                                                                                                                           |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Test Case ID**    | TC-W03                                                                                                                                                                             |
| **Description**     | Đảm bảo hệ thống gửi email thông báo nội bộ sau khi khách hàng submit form thành công.                                                                                             |
| **Pre-conditions**  | Odoo đã cấu hình Outgoing Mail Server. Thực hiện sau TC-W01 thành công.                                                                                                            |
| **Steps**           | 1. Khách hàng submit form `/tu-van` hợp lệ (giống TC-W01).<br>2. Nhân viên Sales đăng nhập Odoo, vào CRM > Lead mới vừa tạo.<br>3. Kiểm tra phần Chatter (hộp chat) bên dưới Lead. |
| **Expected Result** | Trong Chatter của Lead ghi nhận log tự động: email thông báo đã được gửi đi. Nội dung email chứa đầy đủ thông tin khách hàng đã điền trên form.                                    |
| **Actual Result**   |                                                                                                                                                                                    |
| **Status**          |                                                                                                                                                                                    |
| **Comments**        |                                                                                                                                                                                    |

#### TC-W04: Lọc sản phẩm theo danh mục

| Trường thông tin    | Chi tiết                                                                                                                                                                   |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Test Case ID**    | TC-W04                                                                                                                                                                     |
| **Description**     | Kiểm tra chức năng điều hướng và lọc sản phẩm trong cửa hàng E-commerce.                                                                                                   |
| **Pre-conditions**  | Đã tạo các sản phẩm mẫu thuộc nhiều danh mục khác nhau (Thiết bị mạng, Laptop...).                                                                                         |
| **Steps**           | 1. Vào trang `/shop`.<br>2. Tại thanh sidebar bên trái, click chọn danh mục "Thiết bị mạng".                                                                               |
| **Expected Result** | Giao diện tự động load lại chỉ hiển thị các sản phẩm thuộc danh mục "Thiết bị mạng" (Router, Switch...). Các sản phẩm thuộc danh mục khác (như Laptop) bị ẩn đi hoàn toàn. |
| **Actual Result**   |                                                                                                                                                                            |
| **Status**          |                                                                                                                                                                            |
| **Comments**        |                                                                                                                                                                            |

#### TC-W05: Trang responsive trên mobile

| Trường thông tin    | Chi tiết                                                                                                                                                                             |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Test Case ID**    | TC-W05                                                                                                                                                                               |
| **Description**     | Kiểm tra tính tương thích giao diện của website trên thiết bị di động có màn hình nhỏ.                                                                                               |
| **Pre-conditions**  | Mở trình duyệt Chrome trên máy tính.                                                                                                                                                 |
| **Steps**           | 1. Nhấn F12 để mở Developer Tools.<br>2. Bật chế độ Device Toolbar, chọn thiết bị iPhone SE (kích thước ngang 375px).<br>3. Lần lượt truy cập Trang chủ, Shop và trang Liên hệ.      |
| **Expected Result** | Tất cả các trang đều co giãn hợp lý, không bị vỡ layout, không xuất hiện thanh cuộn ngang. Menu hamburger hiển thị và hoạt động tốt. Các nút bấm đủ lớn để ấn trên màn hình cảm ứng. |
| **Actual Result**   |                                                                                                                                                                                      |
| **Status**          |                                                                                                                                                                                      |
| **Comments**        |                                                                                                                                                                                      |

---

## 3. Nhóm CRM

#### TC-C01: Activity tự tạo khi chuyển stage

| Trường thông tin    | Chi tiết                                                                                                                                                                      |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Test Case ID**    | TC-C01                                                                                                                                                                        |
| **Description**     | Kiểm tra tính năng tự động hóa (Automated Actions) sinh ra công việc nhắc nhở nhân viên khi chuyển bước pipeline.                                                             |
| **Pre-conditions**  | Đã cấu hình Automated Action sinh Activity khi chuyển Stage. Có sẵn 1 Lead ở cột "Tiếp nhận yêu cầu".                                                                                       |
| **Steps**           | 1. Mở giao diện Kanban của CRM.<br>2. Kéo (Drag) thẻ Khách hàng từ cột "Tiếp nhận yêu cầu" sang cột "Đang tư vấn".<br>3. Mở chi tiết Lead đó ra và xem phần Activities.                     |
| **Expected Result** | Một Activity mới (ví dụ: "Gọi điện tư vấn") tự động xuất hiện với màu xanh (chưa quá hạn). Nội dung, hạn chót và người được giao đúng như đã cấu hình trong Automated Action. |
| **Actual Result**   |                                                                                                                                                                               |
| **Status**          |                                                                                                                                                                               |
| **Comments**        |                                                                                                                                                                               |

#### TC-C02: Lead tự tạo từ form website

| Trường thông tin    | Chi tiết                                                                                                                                                                                                                |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Test Case ID**    | TC-C02                                                                                                                                                                                                                  |
| **Description**     | Tái khẳng định tích hợp luồng dữ liệu thông suốt từ Website vào CRM.                                                                                                                                                    |
| **Pre-conditions**  | Đã thực hiện TC-W01 thành công.                                                                                                                                                                                         |
| **Steps**           | 1. Truy cập vào phân hệ CRM.<br>2. Kiểm tra danh sách hiển thị ở cột đầu tiên (Tiếp nhận yêu cầu / Mới).                                                                                                                |
| **Expected Result** | Lead mới vừa được Khách hàng submit trên Web nằm ngay ngắn ở cột đầu tiên. Các trường Tên, Số điện thoại, Email khớp 100% với form đã điền. Lead chưa được gán cho nhân viên nào (hoặc gán đúng theo rule đã cấu hình). |
| **Actual Result**   |                                                                                                                                                                                                                         |
| **Status**          |                                                                                                                                                                                                                         |
| **Comments**        |                                                                                                                                                                                                                         |

#### TC-C03: Lọc khách hàng theo tag

| Trường thông tin    | Chi tiết                                                                                                                           |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Test Case ID**    | TC-C03                                                                                                                             |
| **Description**     | Kiểm tra khả năng quản lý thẻ (Tag) và bộ lọc tìm kiếm để phân loại khách hàng thân thiết.                                         |
| **Pre-conditions**  | Đã gắn tag "VIP" cho khách hàng A. Các khách hàng khác không có tag này.                                                           |
| **Steps**           | 1. Vào menu CRM > Customers.<br>2. Nhập từ khóa "VIP" vào thanh tìm kiếm và chọn bộ lọc `Tags = VIP`.                              |
| **Expected Result** | Danh sách hiển thị chỉ còn duy nhất khách hàng A (hoặc những khách có tag VIP). Những khách hàng không có tag VIP bị ẩn hoàn toàn. |
| **Actual Result**   |                                                                                                                                    |
| **Status**          |                                                                                                                                    |
| **Comments**        |                                                                                                                                    |

#### TC-C04: Email tự động gửi đúng khi chuyển stage

| Trường thông tin    | Chi tiết                                                                                                                                                                                                                                                  |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Test Case ID**    | TC-C04                                                                                                                                                                                                                                                    |
| **Description**     | Kiểm tra email template tự động gửi đúng nội dung khi nhân viên chuyển Opportunity sang bước mới.                                                                                                                                                         |
| **Pre-conditions**  | Đã cấu hình email template cho stage "Gửi báo giá". Odoo đã cấu hình Outgoing Mail Server. Có sẵn 1 Opportunity đang ở stage "Đang tư vấn".                                                                                                               |
| **Steps**           | 1. Mở Opportunity đang ở stage "Đang tư vấn".<br>2. Kéo hoặc chọn chuyển sang stage "Gửi báo giá".<br>3. Vào phần Chatter của Opportunity kiểm tra log email.<br>4. Kiểm tra hộp thư của khách hàng (nếu có email thật) hoặc xem log trong Outgoing Mail. |
| **Expected Result** | Một email với nội dung template "Gửi báo giá" được gửi tự động. Trong Chatter ghi nhận log email đã gửi thành công. Tên khách hàng, thông tin sản phẩm trong email khớp với Opportunity.                                                                  |
| **Actual Result**   |                                                                                                                                                                                                                                                           |
| **Status**          |                                                                                                                                                                                                                                                           |
| **Comments**        |                                                                                                                                                                                                                                                           |

---

## Kết quả tổng hợp

| Nhóm     | Tổng TC | Pass | Fail | Tỷ lệ | Ghi chú |
| -------- | ------- | ---- | ---- | ----- | ------- |
| KHO      | 6       |      |      |       |         |
| WEB      | 5       |      |      |       |         |
| CRM      | 4       |      |      |       |         |
| **Tổng** | **15**  |      |      |       |         |

- **Ngày thực hiện:** .../.../2026
- **Người thực hiện:** Phạm Công Võ
