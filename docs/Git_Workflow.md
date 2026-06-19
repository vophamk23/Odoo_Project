# Quy trình Phát triển và Triển khai Phần mềm (Development Workflow)

Tài liệu này quy định tiêu chuẩn làm việc nhóm khắt khe trong giai đoạn Phase 2. Toàn bộ Developer, Reviewer và QA bắt buộc tuân thủ quy trình này từ lúc nhận Task đến khi Deploy code lên server thực tế.

---

## 1. Quy trình nhận task và bắt đầu Dev

> [!IMPORTANT]
> Tuyệt đối không code trực tiếp trên nhánh `main` hoặc `develop`. Mọi tính năng phải được tách nhánh độc lập.

1. **Tiếp nhận Task:** 
   - Developer đăng nhập vào hệ thống quản lý công việc (Redmine/Jira).
   - Kiểm tra danh sách ticket được gán (Assigned to me).
2. **Cập nhật trạng thái:** 
   - Đổi trạng thái ticket sang `In Progress`. 
   - Đọc kỹ yêu cầu (Description). Nếu có sự thiếu logic trong yêu cầu, lập tức comment tag Leader để làm rõ trước khi code.
3. **Đồng bộ mã nguồn:** 
   ```bash
   git checkout develop
   git pull origin develop
   ```
4. **Tạo nhánh làm việc (Branching Strategy):** 
   - Cú pháp bắt buộc: `<loại>/<ID_Ticket>-<Tên_tính_năng_ngắn_gọn>`
   - Các loại nhánh: `feature` (Tính năng mới), `bugfix` (Sửa lỗi), `hotfix` (Sửa lỗi khẩn cấp trên production).
   - Ví dụ:
     ```bash
     git checkout -b feature/11056-setup-warranty-module
     # Hoặc
     git checkout -b bugfix/11099-fix-state-machine-logic
     ```

---

## 2. Quy trình Commit code và tạo Pull Request (PR)

> [!TIP]
> Chia nhỏ các commit theo từng cụm chức năng nhỏ sẽ giúp Reviewer dễ dàng kiểm tra code hơn. Không dồn 1 cục code khổng lồ vào 1 commit duy nhất.

1. **Kiểm tra tiêu chuẩn nội bộ (Local Test):** 
   - Chạy Odoo Unit Test trên máy ảo Docker đảm bảo Pass 100%.
   - Đảm bảo Terminal không văng Warning (Cảnh báo).
2. **Quy tắc Commit Message:** 
   - Áp dụng chuẩn [Conventional Commits].
   - Cú pháp: `<type>(<scope>): <Mô tả ngắn gọn>`
   - `type` bao gồm: `feat` (Thêm mới), `fix` (Sửa bug), `docs` (Tài liệu), `refactor` (Tối ưu code).
   - Ví dụ:
     ```bash
     git add .
     git commit -m "feat(warranty): Khởi tạo module cmcts_warranty và setup cấu trúc"
     git commit -m "fix(claim): Sửa lỗi không đếm đúng số lượng yêu cầu sửa chữa"
     ```
3. **Đẩy code lên GitHub:**
   ```bash
   git push origin feature/11056-setup-warranty-module
   ```
4. **Tạo Pull Request (PR):** 
   - Lên GitHub, gửi PR từ nhánh của bạn vào nhánh `develop`. 
   - Mô tả PR phải gắn link ticket Redmine (Ví dụ: `Closes #11056`).
   - Gán (Assign) 1 Senior Developer để Review.

---

## 3. Quy trình Review Code và Merge (Dành cho Reviewer)

> [!WARNING]
> Reviewer chịu trách nhiệm liên đới nếu Approve một đoạn code có bug logic làm sập hệ thống hoặc gây lỗi bảo mật.

1. **Checklist kiểm tra (Code Review):** 
   - Code có vi phạm quy tắc thụt lề, đặt tên biến (PEP8) không?
   - Cú pháp XML có đúng chuẩn Odoo không? Có thiếu thuộc tính `title` gây lỗi Accessibility không?
   - Có tuân thủ các Record Rules bảo mật không?
2. **Thao tác Review:**
   - **Nếu có lỗi:** Comment trực tiếp trên từng dòng code lỗi, chọn `Request changes`. Bắt buộc Developer viết code phải sửa lại và push commit mới.
   - **Nếu code đạt chuẩn:** Bấm `Approve`.
3. **Thao tác Merge:**
   - Sử dụng chế độ **Squash and merge** để gộp nhiều commit vụn vặt thành 1 commit duy nhất cho sạch lịch sử nhánh `develop`.
   - Tick chọn ô *Delete branch* để xóa nhánh `feature/` sau khi merge xong.

---

## 4. Quy trình Deploy và Kiểm thử (UAT)

> [!NOTE]
> Mọi thao tác Deploy lên Staging/Production phải được lưu log cẩn thận.

1. **Deploy lên môi trường Staging/Test:**
   - Truy cập vào server Staging qua giao thức SSH.
   - Cập nhật mã nguồn:
     ```bash
     git checkout develop
     git pull origin develop
     ```
   - Nạp lại Service Odoo và ép nâng cấp đúng module vừa chỉnh sửa:
     ```bash
     # Khởi động lại container Odoo
     docker restart cmcts_odoo
     
     # Update module
     docker exec -u odoo cmcts_odoo odoo -d vopc_cmcts -u cmcts_warranty
     ```
2. **Kiểm thử tích hợp (UAT):** 
   - Tester (QA) truy cập hệ thống Staging.
   - Thực hiện test theo kịch bản (Test Cases). Kiểm tra UI, phân quyền chéo, logic trạng thái.
3. **Đóng Ticket:** 
   - Nếu hệ thống chạy ổn định 100%, chuyển trạng thái ticket trên Redmine sang `Resolved` hoặc `Closed`. Luồng phát triển kết thúc.
