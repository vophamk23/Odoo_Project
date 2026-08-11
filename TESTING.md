# 🧪 Hướng Dẫn Chạy Kiểm Thử (Testing Guide)

Tài liệu này cung cấp chi tiết toàn bộ các API, danh mục kịch bản kiểm thử (test cases) và hướng dẫn thực thi kiểm thử thông qua **Excel Automation** và **Postman** cho hệ thống **T4 Gate Keeper**.

---

## 📋 I. Danh Mục Chi Tiết API & Kịch Bản Kiểm Thử (API Test Cases Directory)

Hệ thống có tổng cộng hơn **80 kịch bản kiểm thử (test cases)** giả lập toàn bộ các hành vi tích hợp, các lỗi kết nối, lỗi dữ liệu đầu vào và các ràng buộc bảo mật.

---

### 1. API Xác Thực Hệ Thống (Auth Token)
* **Endpoint:** `POST /auth/token`
* **Mô tả:** Cấp phát Access Token và Refresh Token dựa trên cơ chế OAuth2 Client Credentials để bảo mật giao tiếp giữa các Controller và Server Odoo.

#### Danh sách kịch bản kiểm thử:
| ID | Tên Kịch Bản | Trạng Thái Mong Đợi (HTTP) | Kết Quả / Thông Điệp Kỳ Vọng |
| :--- | :--- | :---: | :--- |
| **1.A** | Đăng nhập thành công với client_credentials | `200 OK` | Trả về Access Token & Refresh Token hợp lệ |
| **1.B** | Làm mới token bằng refresh_token hợp lệ | `200 OK` | Trả về Access Token mới |
| **1.C** | Body JSON không hợp lệ (malformed JSON) | `400 Bad Request` | `"Invalid JSON body."` |
| **1.D** | Thiếu `refresh_token` khi `grant_type = refresh_token` | `400 Bad Request` | `"refresh_token is required."` |
| **1.E** | `client_id` không tồn tại | `401 Unauthorized` | `"No application found for the given client_id."` |
| **1.F** | `client_secret` bị sai | `401 Unauthorized` | `"Invalid client_secret for the given client_id."` |
| **1.G** | Thiếu `client_secret` | `401 Unauthorized` | `"client_secret is required."` |
| **1.H** | `refresh_token` hết hạn hoặc không hợp lệ | `401 Unauthorized` | `"Invalid or expired refresh_token"` |
| **1.I** | Thiếu `client_id` khi `grant_type = client_credentials` | `401 Unauthorized` | `"client_id is required."` |
| **1.J** | Đăng nhập thiếu `grant_type` | `200 OK` | Tự động fallback và đăng nhập thành công |
| **1.K** | IP không nằm trong Allowed IPs của Application | `403 Forbidden` | `"IP not in allowed list"` |
| **1.L** | Rate limit bị vượt quá | `429 Too Many Requests` | `"Rate limit exceeded"` |

---

### 2. API Đăng Ký Bộ Điều Khiển (Controller Register)
* **Endpoint:** `POST /api/v1/ControllerRegister`
* **Mô tả:** Thiết bị Controller gửi thông tin phần cứng lên Server Odoo khi mới lắp đặt hoặc khởi động lại để lưu trữ thông tin cấu hình.

#### Danh sách kịch bản kiểm thử:
| ID | Tên Kịch Bản | Trạng Thái Mong Đợi (HTTP) | Kết Quả / Thông Điệp Kỳ Vọng |
| :--- | :--- | :---: | :--- |
| **2.A** | Đăng ký Controller sảnh Hà Nội (Đầy đủ trường) | `200 OK` | `"Controller registered successfully"` |
| **2.A2** | Đăng ký Controller kho HCM | `200 OK` | `"Controller registered successfully"` |
| **2.A3** | Đăng ký Controller Server Room Hà Nội | `200 OK` | `"Controller registered successfully"` |
| **2.A4** | Đăng ký Controller Đà Nẵng | `200 OK` | `"Controller registered successfully"` |
| **2.B** | Đăng ký với yêu cầu tối thiểu (chỉ required fields) | `200 OK` | `"Controller registered successfully"` |
| **2.C** | Thiếu trường `firmware_version` | `200 OK` | Hệ thống vẫn chấp nhận đăng ký |
| **2.D** | Thiếu trường `ip_address` | `200 OK` | Hệ thống vẫn chấp nhận đăng ký |
| **2.E** | Thiếu trường `mac_address` | `200 OK` | Hệ thống vẫn chấp nhận đăng ký |
| **2.F** | Thiếu trường `installed_at` | `200 OK` | Hệ thống vẫn chấp nhận đăng ký |
| **2.G** | Tự động tạo Controller mới hoàn toàn khi chưa có | `200 OK` | `"Controller registered successfully"` |
| **2.H** | Đăng ký thay thế thiết bị cũ (`replaces_sn`) | `200 OK` | Chuyển toàn bộ Device trực thuộc sang Controller mới |
| **2.I** | Đăng ký lặp lại cùng Controller (Cập nhật thông tin) | `200 OK` | Cập nhật IP/MAC/Firmware thành công |
| **2.J** | Thiếu trường bắt buộc `serial_number` | `400 Bad Request` | Báo lỗi thiếu trường bắt buộc |
| **2.K** | Thiếu trường bắt buộc `branch_code` | `400 Bad Request` | Báo lỗi thiếu trường bắt buộc |
| **2.L** | Đăng ký với `branch_code` không tồn tại trong DB | `400 Bad Request` | `"Invalid branch_code provided"` |
| **2.M** | Gọi API không kèm Authorization Header | `401 Unauthorized` | `"Missing Authorization"` |
| **2.N** | Gọi API với token sai/hết hạn | `401 Unauthorized` | `"Invalid or expired access token."` |

---

### 3. API Đăng Ký Thiết Bị Đầu Cuối (Device Register)
* **Endpoint:** `POST /api/v1/DeviceRegister`
* **Mô tả:** Đăng ký các thiết bị con (như đầu đọc thẻ RFID, đầu đọc vân tay) thuộc quyền quản lý của một Controller cụ thể.

#### Danh sách kịch bản kiểm thử:
| ID | Tên Kịch Bản | Trạng Thái Mong Đợi (HTTP) | Kết Quả / Thông Điệp Kỳ Vọng |
| :--- | :--- | :---: | :--- |
| **5.A** | Đăng ký thiết bị sảnh vào Hà Nội (Đầy đủ trường) | `200 OK` | `"Devices register successfully"` |
| **5.A2** | Đăng ký thêm thiết bị cho các Controller khác | `200 OK` | `"Devices register successfully"` |
| **5.B** | Đăng ký thiết bị với yêu cầu tối thiểu | `200 OK` | `"Devices register successfully"` |
| **5.C** | Khuyết trường `port_or_channel` | `200 OK` | Hệ thống vẫn cho đăng ký |
| **5.D** | Khuyết trường `device_model_code` | `200 OK` | Hệ thống vẫn cho đăng ký |
| **5.E** | Khuyết trường `status` | `200 OK` | Hệ thống mặc định trạng thái |
| **5.F** | Khuyết trường `is_active` | `200 OK` | Hệ thống mặc định active = true |
| **5.C2** | Đăng ký lặp lại thiết bị đã có (Cập nhật thông tin) | `200 OK` | Cập nhật thành công |
| **5.D_extra**| Đăng ký thiết bị thứ hai cùng thuộc một Controller | `200 OK` | Đăng ký thành công |
| **5.G** | Thiếu trường bắt buộc `serial_number` | `400 Bad Request` | `"Device Register must contain (controller_sn,serial_number)"` |
| **5.H** | Thiếu trường bắt buộc `controller_sn` | `400 Bad Request` | `"Device Register must contain (controller_sn,serial_number)"` |
| **5.I** | `controller_sn` chỉ định không tồn tại | `400 Bad Request` | `"Can not find controller serial number"` |
| **5.K** | Gọi đăng ký không kèm token | `401 Unauthorized` | `"Missing Authorization"` |
| **5.L** | Gọi đăng ký với token sai | `401 Unauthorized` | `"Invalid or expired access token."` |
| **-** | **[Ràng buộc] Trùng lặp port/channel trên cùng Controller**| `400 Bad Request` | `"Device port or channel must be unique per controller."` |

---

### 4. API Gửi Tín Hiệu Sống (Controller Heartbeat)
* **Endpoint:** `POST /api/v1/ControllerHeartbeat`
* **Mô tả:** Controller định kỳ gửi tín hiệu ping kèm danh sách trạng thái của các Device trực thuộc (`online` hoặc `offline`) lên server để giám sát.

#### Danh sách kịch bản kiểm thử:
| ID | Tên Kịch Bản | Trạng Thái Mong Đợi (HTTP) | Kết Quả / Thông Điệp Kỳ Vọng |
| :--- | :--- | :---: | :--- |
| **3.A** | Heartbeat thành công, cập nhật trạng thái thiết bị | `200 OK` | `"Success"`, đổi trạng thái Device |
| **3.A2** | Heartbeat báo tất cả thiết bị đều offline | `200 OK` | `"Success"`, đổi trạng thái Device sang offline |
| **3.A3** | Heartbeat gửi mảng thiết bị rỗng (không có device) | `200 OK` | `"Success"` |
| **3.B** | Thiếu trường bắt buộc `controller_sn` | `400 Bad Request` | `"Missing controller_sn"` |
| **3.C** | Thiếu trường bắt buộc `devices` (danh sách trạng thái) | `400 Bad Request` | `"Missing devices_status"` |
| **3.D** | `controller_sn` không tồn tại | `400 Bad Request` | `"Không tìm thấy Controller với serial số: CTRL-FAKE-999"` |
| **3.E** | Gọi heartbeat không có token | `401 Unauthorized` | Trả về mã 401 |
| **3.F** | Gọi heartbeat với token sai | `401 Unauthorized` | Trả về mã 401 |

---

### 5. API Lấy Cấu Hình Điều Khiển (Controller Get Config / Remote Command)
* **Endpoint:** `POST /api/v1/ControllerGetConfig`
* **Mô tả:** Lấy thông tin cấu hình hệ thống bao gồm múi giờ (timezone) của chi nhánh và thông tin chi tiết của tất cả các Device trực thuộc.

#### Danh sách kịch bản kiểm thử:
| ID | Tên Kịch Bản | Trạng Thái Mong Đợi (HTTP) | Kết Quả / Thông Điệp Kỳ Vọng |
| :--- | :--- | :---: | :--- |
| **8.A** | Lấy cấu hình thành công (Controller có nhiều device) | `200 OK` | Trả về cấu hình kèm thông tin timezone & các device |
| **8.B** | Lấy cấu hình thành công (Controller không có device nào) | `200 OK` | Trả về cấu hình với mảng `devices` rỗng |
| **8.C** | Thiếu trường bắt buộc `controller_sn` | `400 Bad Request` | `"Controller ID is required."` |
| **8.D** | `controller_sn` không tồn tại trong DB | `400 Bad Request` | `"Can not find controller with ID ..."` |
| **8.E/F** | Không có token hoặc token không hợp lệ | `401 Unauthorized` | Trả về mã 401 |

---

### 6. API Trạng Thái Đồng Bộ Nhân Viên (Controller Employee Sync Status)
* **Endpoint:** `GET /api/v1/ControllerEmployeeSyncStatus`
* **Mô tả:** Thiết bị gọi định kỳ để kiểm tra xem Server Odoo có cập nhật dữ liệu nhân sự mới nào cần đồng bộ xuống hay không.

#### Danh sách kịch bản kiểm thử:
| ID | Tên Kịch Bản | Trạng Thái Mong Đợi (HTTP) | Kết Quả / Thông Điệp Kỳ Vọng |
| :--- | :--- | :---: | :--- |
| **6.A** | Kiểm tra khi dữ liệu nhân sự thay đổi (Cần sync) | `200 OK` | `{"data": {"update": true}}` |
| **6.B** | Kiểm tra khi dữ liệu đã đồng bộ hoàn tất (Không cần sync)| `200 OK` | `{"data": {"update": false}}` |
| **6.C** | Thiếu trường tham số `controller_sn` trên URL | `400 Bad Request` | `"Can not find controller with id False"` |
| **6.D** | `controller_sn` không tồn tại | `400 Bad Request` | `"Can not find controller serial number..."` |
| **6.E/F** | Lỗi xác thực token | `401 Unauthorized` | Trả về mã 401 |

---

### 7. API Đồng Bộ Nhân Sự Phân Trang (Controller Employee Sync)
* **Endpoint:** `POST /api/v1/ControllerEmployeeSync`
* **Mô tả:** Sử dụng thuật toán phân trang con trỏ (Cursor-Based Pagination) để kéo toàn bộ hoặc một phần danh sách nhân viên cần thêm mới (`new`), cập nhật (`update`), hoặc bị vô hiệu hóa (`deleted`) thuộc phạm vi quản lý của chi nhánh.

#### Danh sách kịch bản kiểm thử:
| ID | Tên Kịch Bản | Trạng Thái Mong Đợi (HTTP) | Kết Quả / Thông Điệp Kỳ Vọng |
| :--- | :--- | :---: | :--- |
| **3_ES.A**| Đồng bộ lần đầu (nạp toàn bộ dữ liệu, mặc định size=15) | `200 OK` | Trả về thông tin danh sách nhân sự mới tạo |
| **3_ES.B**| Đồng bộ khi không có sự thay đổi nào xảy ra | `200 OK` | Trả về kết quả các mảng new/update/deleted đều rỗng |
| **3_ES.C**| Thiếu trường bắt buộc `controller_sn` | `400 Bad Request` | `"Controller ID is required."` |
| **3_ES.D**| `controller_sn` không tồn tại | `400 Bad Request` | `"Can not find controller with ID ..."` |
| **3_ES.E/F**| Lỗi xác thực token | `401 Unauthorized` | Trả về mã 401 |
| **3_ES.G**| Test phân trang con trỏ: Gọi trang 1 (page_size = 2) | `200 OK` | Trả về 2 bản ghi kèm `next_cursor_id` và `has_next_page = true` |
| **3_ES.H**| Test phân trang con trỏ: Gọi trang 2 với Cursor | `200 OK` | Sử dụng `next_cursor_id` của trang 1 để đọc tiếp dữ liệu |
| **3_ES.I**| Đồng bộ kết hợp mốc `last_sync_at` (sync delta) & cursor | `200 OK` | Lọc dữ liệu thay đổi và phân trang |

---

### 8. API Xác Nhận Đồng Bộ Thành Công (Controller Sync Ack)
* **Endpoint:** `POST /api/v1/ControllerSyncAck`
* **Mô tả:** Gửi tín hiệu xác nhận Controller đã lưu toàn bộ thông tin nhân sự thành công để Server cập nhật mốc thời gian đồng bộ cuối cùng.

#### Danh sách kịch bản kiểm thử:
| ID | Tên Kịch Bản | Trạng Thái Mong Đợi (HTTP) | Kết Quả / Thông Điệp Kỳ Vọng |
| :--- | :--- | :---: | :--- |
| **3_ACK.A**| Báo nhận thành công và gửi kèm mốc thời gian | `200 OK` | `"Success"`, ghi nhận thời gian đồng bộ |
| **3_ACK.B**| Báo nhận thành công không gửi kèm mốc (Server tự lấy giờ)| `200 OK` | `"Success"`, tự động lấy giờ hiện tại |
| **3_ACK.C**| Thiếu trường bắt buộc `controller_sn` | `400 Bad Request` | `"Controller serial number is required."` |
| **3_ACK.D**| `controller_sn` không tồn tại | `400 Bad Request` | `"Can not find controller serial number..."` |
| **3_ACK.E**| Gọi báo nhận không có token | `401 Unauthorized` | Trả về mã 401 |
| **3_ACK.F**| Định dạng trường `sync_timestamp` bị sai | `500 Internal Error` | Trả về lỗi định dạng thời gian |

---

### 9. API Lấy Chi Tiết Sinh Trắc Học Nhân Viên (Employee Biometric Get)
* **Endpoint:** `POST /api/v1/EmployeeBiometricGet`
* **Mô tả:** Lấy dữ liệu sinh trắc học chi tiết (mẫu vân tay base64, mẫu khuôn mặt, ảnh đại diện) của một nhân viên cụ thể theo mã `emp_id`.

#### Danh sách kịch bản kiểm thử:
| ID | Tên Kịch Bản | Trạng Thái Mong Đợi (HTTP) | Kết Quả / Thông Điệp Kỳ Vọng |
| :--- | :--- | :---: | :--- |
| **7.A** | Lấy biometric thành công | `200 OK` | Trả về mẫu sinh trắc học và avatar dạng Base64 |
| **7.B** | Nhân viên không có mẫu sinh trắc học trong DB | `200 OK` | Trả về kết quả với các trường biometric trống |
| **7.C** | Thiếu trường bắt buộc `controller_sn` | `400 Bad Request` | `"Controller ID is required."` |
| **7.D** | Thiếu trường bắt buộc `emp_id` | `400 Bad Request` | `"Employee ID is required."` |
| **7.E** | `controller_sn` không tồn tại | `400 Bad Request` | `"Can not find controller with ID ..."` |
| **7.F** | **Nhân viên thuộc chi nhánh khác với Controller** | `400 Bad Request` | `"Không tìm thấy Controller hoặc Nhân viên hợp lệ"` (Chặn xem chéo) |
| **7.G/H** | Lỗi xác thực token | `401 Unauthorized` | Trả về mã 401 |

---

### 10. API Tải Nhật Ký Truy Cập (Access Log Upload)
* **Endpoint:** `POST /api/v1/AccessLogUpload`
* **Mô tả:** Controller đẩy nhật ký quẹt thẻ RFID/quẹt vân tay/quẹt khuôn mặt của các Device trực thuộc lên Server.
* **Cơ chế đặc biệt:** Server tự động kiểm tra xem thời điểm quẹt thẻ (`access_time`) có vi phạm làm việc ngoài giờ hành chính (08:00 - 17:00) hay ngày cuối tuần hay không. Nếu có, tự động tạo cảnh báo `invalid_access` tại Area tương ứng.

#### Danh sách kịch bản kiểm thử:
| ID | Tên Kịch Bản | Trạng Thái Mong Đợi (HTTP) | Kết Quả / Thông Điệp Kỳ Vọng |
| :--- | :--- | :---: | :--- |
| **4.A** | Gửi 1 bản ghi log truy cập thành công | `200 OK` | `"Success"`, ghi nhận log vào DB |
| **4.A2**| Gửi nhiều log đồng thời (dạng Batch) | `200 OK` | Ghi nhận toàn bộ danh sách log thành công |
| **4.A3**| Gửi log bị trùng lặp thời gian & nhân viên | `200 OK` | `"Success"`, nhưng số dòng được ghi nhận = 0 (tự bỏ qua trùng) |
| **4.B** | Gửi log ngoài giờ hành chính (22h đêm) | `200 OK` | Ghi log thành công + **kích hoạt cảnh báo vi phạm giờ làm** |
| **4.C** | Gửi log quẹt ngày Chủ Nhật | `200 OK` | Ghi log thành công + **kích hoạt cảnh báo vi phạm ngày nghỉ** |
| **4.D** | Thiếu trường bắt buộc `controller_sn` | `400 Bad Request` | `"Controller serial number is required."` |
| **4.E** | Thiếu dữ liệu mảng thiết bị `devices` | `400 Bad Request` | `"No device data provided."` |
| **4.F** | `controller_sn` chỉ định không tồn tại | `400 Bad Request` | `"Controller with serial number ... is not registered."` |
| **4.G** | Gửi danh sách log trống | `200 OK` | `"Success"`, không ghi nhận thêm log |
| **4.H** | Thiết bị gửi log không trực thuộc Controller này | `200 OK` | Bỏ qua ghi nhận thiết bị lạ |

---

## 🔌 II. Hướng Dẫn Thiết Lập & Chạy Kiểm Thử (Test Execution Guide)

### 1. Khởi Động Môi Trường
Đảm bảo môi trường Docker đã được khởi động:
1. Chạy file [start_docker.bat](docker/start_docker.bat) để dựng dịch vụ Odoo 19:
   ```bash
   docker/start_docker.bat
   ```
   * **Odoo API URL:** `http://localhost:8070`
   * **Database:** `gatekeeper_phase3_db`

### 2. Kiểm Thử Tự Động Qua Excel (Excel Automation)
Bộ test này tự động chạy toàn bộ hơn 80 kịch bản nêu ở mục I thông qua script Python.

#### Bước 2.1: Cài đặt thư viện Python cần thiết
Mở terminal và thực thi lệnh:
```bash
pip install openpyxl requests
```

#### Bước 2.2: Thực thi kiểm thử tự động
Bạn có thể chọn 1 trong 2 cách:
* **Cách 1 (Nhanh nhất):** Double-click chạy trực tiếp file [run_tests.bat](run_tests.bat).
* **Cách 2 (Sử dụng lệnh):**
  ```bash
  python tests/run_excel_tests.py
  ```

#### Bước 2.3: Đọc kết quả kiểm thử
* Script kiểm thử sẽ tự động đọc danh sách kịch bản trong file [api_test_cases.xlsx](tests/api_test_cases.xlsx).
* Sau khi hoàn tất, kết quả chi tiết từng case (Pass/Fail, HTTP status thực tế, Response chi tiết, Latency) sẽ được xuất ra file: [api_test_results.xlsx](tests/api_test_results.xlsx).
* Nếu chạy qua file `.bat`, file kết quả Excel này sẽ tự động mở lên khi chạy xong.

*(Mẹo: Bạn có thể chọn chạy hoặc bỏ qua một test case bằng cách điền chữ `x` hoặc để trống tại cột **Run?** trong file Excel kịch bản)*

---

### 3. Kiểm Thử Thủ Công/Theo Nhóm Qua Postman (Postman Collections)
Để kiểm tra từng API trực tiếp trên giao diện:

#### Bước 3.1: Import Collections vào Postman
Mở Postman, chọn **Import** và kéo thả các file sau vào:
1. [0_api_response_tests.postman_collection.json](tests/0_api_response_tests.postman_collection.json): Chứa các kịch bản kiểm tra mã lỗi HTTP Status.
2. [GateKeeper.postman_collection.json](tests/http_scenarios/GateKeeper.postman_collection.json): Chứa các luồng API nghiệp vụ tích hợp.

#### Bước 3.2: Thực thi
Bấm chọn từng API request để gửi dữ liệu thử nghiệm, hoặc chọn **Run Collection** để chạy tự động toàn bộ nhóm API.
