# Test Cases Toàn Bộ Hệ Thống (Phase 1)

## 1. Nhóm KHO (Inventory)

| ID     | Mô tả                          | Các bước thực hiện                                                         | Kết quả mong đợi                                   | Kết quả thực tế | Pass/Fail |
| ------ | ------------------------------ | -------------------------------------------------------------------------- | -------------------------------------------------- | --------------- | --------- |
| TC-K01 | Nhập kho với serial mới hợp lệ | 1. Tạo phiếu Receipts <br>2. Thêm sản phẩm <br>3. Điền serial mới <br>4. Validate      | Phiếu Done, tồn kho tăng đúng                      |                 |           |
| TC-K02 | Nhập kho với serial đã tồn tại | 1. Tạo phiếu Receipts <br>2. Điền serial đã có trong kho <br>3. Validate           | Hệ thống báo lỗi, không cho validate               |                 |           |
| TC-K03 | Xuất kho đúng serial đã chọn   | 1. Tạo phiếu Delivery <br>2. Check Availability <br>3. Chọn serial <br>4. Validate     | Phiếu Done, serial không còn On Hand, tồn kho giảm |                 |           |
| TC-K04 | Chuyển kho nội bộ              | 1. Tạo Internal Transfer <br>2. From/To đúng vị trí <br>3. Chọn serial <br>4. Validate | Serial xuất hiện đúng ở vị trí mới                 |                 |           |
| TC-K05 | Tra cứu lịch sử serial đầy đủ  | 1. Vào Lot/Serial Numbers <br>2. Tìm serial có 3 bước <br>3. Nhấn Traceability     | Hiển thị đủ: nhập → chuyển → xuất                  |                 |           |

## 2. Nhóm WEBSITE

| ID     | Mô tả                              | Các bước thực hiện                                     | Kết quả mong đợi                                          | Kết quả thực tế | Pass/Fail |
| ------ | ---------------------------------- | ------------------------------------------------------ | --------------------------------------------------------- | --------------- | --------- |
| TC-W01 | Submit form tư vấn đủ thông tin    | 1. Vào /tu-van <br>2. Điền đủ trường bắt buộc <br>3. Submit  | Trang hiện thông báo cảm ơn, Lead xuất hiện trong CRM     |                 |           |
| TC-W02 | Submit form thiếu Email (bắt buộc) | 1. Vào /tu-van <br>2. Bỏ trống Email <br>3. Nhấn Submit        | Form không submit, hiện thông báo lỗi "Email là bắt buộc" |                 |           |
| TC-W03 | Email thông báo sau submit         | 1. Submit form hợp lệ <br>2. Vào localhost:8025  | Email thông báo xuất hiện trong Mailhog trong vòng 1 phút |                 |           |
| TC-W04 | Lọc sản phẩm theo danh mục         | 1. Vào /shop <br>2. Chọn danh mục "Thiết bị mạng"          | Chỉ hiện Router và Switch, không hiện Laptop              |                 |           |
| TC-W05 | Trang responsive trên mobile       | 1. F12 → chọn iPhone SE (375px) <br>2. Lần lượt mở trang | Tất cả trang không vỡ layout, nút bấm được                |                 |           |

## 3. Nhóm CRM

| ID     | Mô tả                            | Các bước thực hiện                                               | Kết quả mong đợi                                                 | Kết quả thực tế | Pass/Fail |
| ------ | -------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------- | --------------- | --------- |
| TC-C01 | Activity tự tạo khi chuyển stage | 1. Mở opportunity <br>2. Chuyển sang "Đang tư vấn" <br>3. Xem Activities | Activity tự xuất hiện đúng cấu hình                          |                 |           |
| TC-C02 | Lead tự tạo từ form website      | 1. Submit form /tu-van <br>2. Vào CRM → All Leads                    | Lead mới xuất hiện với thông tin đúng, stage "Tiếp nhận yêu cầu" |                 |           |
| TC-C03 | Lọc khách hàng theo tag          | 1. Vào CRM → Customers <br>2. Filter tag = "VIP"                     | Chỉ hiện khách có tag VIP, không hiện khách khác                 |                 |           |

## Kết quả tổng hợp

| Nhóm     | Tổng TC | Pass | Fail | Tỷ lệ |
| -------- | ------- | ---- | ---- | ----- |
| KHO      | 5       |      |      |       |
| WEB      | 5       |      |      |       |
| CRM      | 3       |      |      |       |
| **Tổng** | **13**  |      |      |       |

Ngày thực hiện: .../.../2026
Người thực hiện: Phạm Công Võ
