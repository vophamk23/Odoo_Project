# 🧪 Hướng Dẫn Chạy Kiểm Thử (Testing Guide)

Tài liệu này hướng dẫn chạy các kịch bản kiểm thử API tích hợp thông qua **Excel Automation** và **Postman** cho hệ thống **T4 Gate Keeper**.

---

## 📌 Chuẩn Bị Môi Trường
Trước khi chạy test, đảm bảo môi trường Docker đã được khởi động:
1. Chạy file [start_docker.bat](file:///C:/Users/ASUS/Desktop/Phase%203/docker/start_docker.bat) để dựng dịch vụ Odoo 19:
   ```bash
   docker/start_docker.bat
   ```
   * **Odoo API URL:** `http://localhost:8070`
   * **Database:** `gatekeeper_phase3_db`

---

## 1. Kiểm Thử Tự Động Qua Excel (Excel Automation)
Bộ test này tự động chạy hơn 80 kịch bản gọi API giả lập thiết bị Controller gửi lên máy chủ Odoo, đối khớp kết quả thực tế với mong đợi.

### Bước 1.1: Cài đặt thư viện Python cần thiết
Mở Terminal tại thư mục dự án và chạy:
```bash
pip install openpyxl requests
```

### Bước 1.2: Thực thi kiểm thử tự động
Bạn có thể chạy bằng 2 cách:
* **Cách 1 (Nhanh nhất):** Double-click chạy trực tiếp file [run_tests.bat](file:///C:/Users/ASUS/Desktop/Phase%203/run_tests.bat) ở thư mục gốc.
* **Cách 2 (Sử dụng lệnh):**
  ```bash
  python tests/run_excel_tests.py
  ```

### Bước 1.3: Đọc kết quả kiểm thử
* Script kiểm thử sẽ tự động đọc danh sách kịch bản trong file [api_test_cases.xlsx](file:///C:/Users/ASUS/Desktop/Phase%203/tests/api_test_cases.xlsx).
* Sau khi hoàn tất, kết quả chi tiết từng case (Pass/Fail, HTTP status, Response chi tiết, Latency) sẽ được xuất ra file: [api_test_results.xlsx](file:///C:/Users/ASUS/Desktop/Phase%203/tests/api_test_results.xlsx).
* Nếu chạy qua file `.bat`, file kết quả Excel này sẽ tự động mở lên khi chạy xong.

*(Mẹo: Bạn có thể chọn chạy hoặc bỏ qua một test case bằng cách điền chữ `x` hoặc để trống tại cột **Run?** trong file Excel kịch bản)*

---

## 2. Kiểm Thử Thủ Công/Theo Nhóm Qua Postman (Postman Collections)
Các bộ sưu tập kiểm thử được dựng sẵn giúp bạn dễ dàng import vào Postman để kiểm tra phản hồi API trực quan.

### Bước 2.1: Import Collections vào Postman
Mở ứng dụng Postman, chọn **Import** và kéo thả các file sau vào:
1. [0_api_response_tests.postman_collection.json](file:///C:/Users/ASUS/Desktop/Phase%203/tests/0_api_response_tests.postman_collection.json): Chứa toàn bộ kịch bản kiểm tra mã lỗi HTTP Status Codes & thông báo trả về.
2. [GateKeeper.postman_collection.json](file:///C:/Users/ASUS/Desktop/Phase%203/tests/http_scenarios/GateKeeper.postman_collection.json): Chứa các luồng đăng ký thiết bị, heartbeat, đồng bộ vân tay/khuôn mặt và nhật ký quẹt thẻ.

### Bước 2.2: Cấu hình và Chạy
* Đảm bảo Odoo đang chạy ở địa chỉ `http://localhost:8070`.
* Bạn có thể bấm chọn từng API request riêng lẻ để gửi dữ liệu thử nghiệm, hoặc chọn **Run Collection** để chạy tự động toàn bộ nhóm API.
