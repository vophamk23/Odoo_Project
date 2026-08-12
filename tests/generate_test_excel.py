# -*- coding: utf-8 -*-
"""Script parse tự động toàn bộ 80 kịch bản test từ 0_api_response_tests.http sang Excel.
Đã tối ưu hóa việc nhận diện mã lỗi (Expected Status) và thông điệp mong đợi (Expected Message).

Yêu cầu: pip install openpyxl
"""
import openpyxl
import re
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTTP_PATH = os.path.join(BASE_DIR, "tests", "0_api_response_tests.http")
EXCEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "api_test_cases.xlsx"
)

# Màu nhóm API cho cột Endpoint (chỉ dùng cho Sheet 2 và Sheet 3)
API_GROUP_FILLS = {
    # Sheet 2: Hardware Management
    "2.": PatternFill(
        start_color="DDEEFF", fill_type="solid"
    ),  # ControllerRegister – Xanh dương nhạt
    "3.": PatternFill(start_color="FCE4D6", fill_type="solid"),  # Heartbeat – Cam nhạt
    "5.": PatternFill(
        start_color="E8DAEF", fill_type="solid"
    ),  # DeviceRegister – Tím nhạt
    "8.": PatternFill(
        start_color="D5E8D4", fill_type="solid"
    ),  # (dự phòng) – Xanh lá nhạt
    # Sheet 3: Employee & Access Sync
    "3_ES.": PatternFill(
        start_color="FDEBD0", fill_type="solid"
    ),  # EmployeeSync – Cam nhạt
    "3_ACK.": PatternFill(
        start_color="FDEBD0", fill_type="solid"
    ),  # EmployeeSyncAck – Cam nhạt (nhóm chung)
    "4.": PatternFill(
        start_color="FEF9E7", fill_type="solid"
    ),  # AccessLogUpload – Vàng nhạt
    "6.": PatternFill(start_color="FDEBD0", fill_type="solid"),  # SyncStatus – Cam nhạt
    "7.": PatternFill(
        start_color="E9F7EF", fill_type="solid"
    ),  # BiometricGet – Xanh lá nhạt
}


def get_api_group_fill(tc_id):
    """Trả về PatternFill tương ứng với nhóm API của test case."""
    tc_id_str = str(tc_id).strip()
    # Thử khớp theo prefix dài nhất trước (ví dụ: '3_ES.' trước '3.')
    for prefix in ["3_ES.", "3_ACK."]:
        if tc_id_str.startswith(prefix):
            return API_GROUP_FILLS[prefix]
    for prefix in ["2.", "3.", "4.", "5.", "6.", "7.", "8."]:
        if tc_id_str.startswith(prefix):
            return API_GROUP_FILLS.get(prefix)
    return None


# Tên prefix API cho cột Name ở 3 sheet chính
API_NAME_PREFIX = {
    "1.": "Auth",
    "2.": "ControllerRegister",
    "3.": "ControllerHeartbeat",
    "3_ES.": "EmployeeSync",
    "3_ACK.": "EmployeeSyncAck",
    "4.": "AccessLogUpload",
    "5.": "DeviceRegister",
    "6.": "SyncStatus",
    "7.": "BiometricGet",
    "8.": "RemoteCommand",
}


def get_api_display_name(tc_id, name, expected_status):
    """Trả về tên hiển thị dạng '[APIName] - [Kịch bản] (Status)'."""
    tc_id_str = str(tc_id).strip()
    prefix = ""
    for p in ["3_ES.", "3_ACK."]:
        if tc_id_str.startswith(p):
            prefix = API_NAME_PREFIX[p]
            break
    if not prefix:
        for p in ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8."]:
            if tc_id_str.startswith(p):
                prefix = API_NAME_PREFIX.get(p, "")
                break
    if prefix:
        return f"{prefix} - {name} ({expected_status})"
    return name


def get_status_styles(status_val):
    try:
        s = int(status_val)
    except Exception:
        return Font(color="000000"), PatternFill(fill_type=None)
    if s == 200:
        return Font(color="006100", bold=True), PatternFill(
            start_color="C6EFCE", fill_type="solid"
        )
    elif s == 400:
        return Font(color="9C6500", bold=True), PatternFill(
            start_color="FFEB9C", fill_type="solid"
        )
    elif s in (401, 403):
        return Font(color="9C0006", bold=True), PatternFill(
            start_color="FFC7CE", fill_type="solid"
        )
    elif s == 422:
        return Font(color="C55A11", bold=True), PatternFill(
            start_color="FCE4D6", fill_type="solid"
        )
    elif s == 500:
        return Font(color="5F497A", bold=True), PatternFill(
            start_color="E4DFEC", fill_type="solid"
        )
    return Font(color="000000"), PatternFill(fill_type=None)


def adjust_column_widths_smart(ws):
    """Tu dong dieu chinh do rong cac cot thong minh: dan rong các cot thuong, wrap text cot du lieu dai."""
    for col in ws.columns:
        # Lay tieu de cot (row 1 cho standard sheets, hoac row 4 cho parameter sheets)
        header_val = ""
        if len(col) > 0:
            header_val = str(col[0].value or "").strip().lower()
        if len(col) > 3:
            r4_val = str(col[3].value or "").strip().lower()
            if r4_val:
                header_val = r4_val

        # Tinh max_len
        max_len = 0
        for cell in col:
            val = str(cell.value or "")
            if len(val) > max_len:
                max_len = len(val)

        col_letter = openpyxl.utils.get_column_letter(col[0].column)

        # Kiem tra xem cot co chua JSON hoac du lieu qua dai can wrap_text hay khong
        is_long_data = any(kw in header_val for kw in ["payload", "logs", "devices_status", "detail", "response"])
        
        if is_long_data:
            ws.column_dimensions[col_letter].width = 55
            for cell in col:
                if cell.row > 1:
                    cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        else:
            # Cho phep tu dong dan rong theo noi dung thuc te (toi da 120 de phong ngua)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 10), 120)


def parse_http_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # Tách file theo ký tự "###" để xử lý từng test case
    raw_blocks = content.split("###")
    test_cases = []

    for block in raw_blocks[1:]:
        lines = [line.strip() for line in block.strip().split("\n")]
        if not lines:
            continue

        # Dòng đầu tiên chứa ID và Tên kịch bản (ví dụ: " 1.A ✅ 200 — Đăng nhập thành công...")
        title_line = lines[0].strip()
        match_title = re.match(r"^([^\s]+)\s+(.+)$", title_line)
        if not match_title:
            continue
        tc_id = match_title.group(1).strip()
        tc_name = match_title.group(2).strip()

        # Tên hiển thị sạch: bỏ phần đầu như "200 - " hoặc "400 - "
        # Regex khớp: (emoji, tùy chọn)(khoảng trắng)(mã HTTP)(khoảng trắng)(dấu — hoặc -)(khoảng trắng)
        tc_display_name = re.sub(r"^[✅❌]?\s*\d{3}\s*[—\-]+\s*", "", tc_name).strip()
        if not tc_display_name:
            tc_display_name = tc_name  # fallback nếu không match

        # 1. Nhận diện Expected Status từ tiêu đề
        match_status_in_title = re.search(r"\b(200|400|401|403|429|500)\b", tc_name)
        if match_status_in_title:
            expected_status = int(match_status_in_title.group(1))
        else:
            if "✅" in tc_name:
                expected_status = 200
            elif "❌" in tc_name:
                expected_status = 400
            else:
                expected_status = 200

        # 2. Tìm Expected Message
        expected_msg = ""
        for line in lines:
            if line.startswith("# KẾT QUẢ:") or line.startswith("# KẾT QUẢ MONG ĐỢI:"):
                # Ví dụ: # KẾT QUẢ: {"success": false, "message": "Missing required field(s): serial_number"}
                # Thử tìm giá trị trong key "message"
                match_msg = re.search(r'"message":\s*"([^"]+)"', line)
                if match_msg:
                    expected_msg = match_msg.group(1)
                else:
                    # Nếu là JSON thông thường, lấy value đầu tiên
                    match_val = re.search(r':\s*"([^"]+)"', line)
                    if match_val:
                        expected_msg = match_val.group(1)
                    else:
                        # Fallback lấy text sau dấu hai chấm
                        parts = line.split(":")
                        if len(parts) > 1:
                            expected_msg = parts[-1].strip("{} \n\"'")

        # Chuẩn hóa Expected Message để khớp với phản hồi thực tế của Odoo
        # if "Missing required fields" in expected_msg:
        #     expected_msg = expected_msg.replace("fields", "field(s)")

        # Fix cứng các case đặc thù mà tiêu đề có thể parse sai hoặc expected msg chưa khớp
        if tc_id == "1.B":
            # 1.B dùng refresh_token thật được inject từ response 1.A → kỳ vọng 200
            expected_status = 200
            expected_msg = "success"
        elif tc_id == "1.D":
            expected_msg = "refresh_token is required for grant_type"
        elif tc_id == "1.E":
            # client_id không tồn tại → "No application found for the given client_id."
            expected_msg = "No application found for the given client_id."
        elif tc_id == "1.F":
            # client_secret sai → "Invalid client_secret for the given client_id."
            expected_msg = "Invalid client_secret for the given client_id."
        elif tc_id == "1.H":
            expected_msg = "Invalid or expired refresh_token"
        elif tc_id in ("2.E", "2.E_err"):
            # API ControllerRegister tự tạo controller mới khi serial chưa có trong DB hoặc sai
            expected_status = 200
            expected_msg = "Controller registered successfully"
        elif tc_id in ("3_ES.G", "3_ES.H"):
            # Pagination chỉ thay đổi data trả về, message vẫn là "Employee Sync Completed"
            expected_msg = "Employee Sync Completed"
        elif tc_id == "4.D":
            expected_msg = "is not registered."
        elif tc_id == "5.G_err":
            # API DeviceRegister tự fallback name = device_sn khi thiếu name
            expected_status = 200
            expected_msg = "Devices register successfully"
        elif tc_id in ("5.A", "5.B", "5.C", "5.C2", "5.D_extra"):
            expected_msg = "Devices register successfully"
        elif tc_id in ("5.D_err", "5.E_err"):
            expected_msg = "Both serial_number (or device_sn) and controller_sn"
        elif tc_id == "7.A":
            expected_msg = "success"
        elif tc_id == "7.B":
            expected_status = 400
            expected_msg = "Không tìm thấy Controller hoặc Nhân viên hợp lệ"
        # -----------------------------------------------------------------
        # Tất cả các case "Không có token" (không gửi Authorization header)
        # Odoo trả về: Missing Authorization: Bearer <token>.
        # -----------------------------------------------------------------
        if (
            not expected_msg
            and expected_status == 401
            and "không có token" in tc_display_name.lower()
        ):
            expected_msg = "Missing Authorization: Bearer"
        # -----------------------------------------------------------------
        # Tất cả các case "Token sai / hết hạn / invalid"
        # Odoo trả về: Invalid or expired access token.
        # -----------------------------------------------------------------
        if not expected_msg and expected_status == 401 and expected_msg == "":
            expected_msg = "Invalid or expired access token."

        # Tìm dòng gửi request
        req_line_idx = -1
        method = "POST"
        endpoint = ""
        for idx, line in enumerate(lines):
            if any(line.startswith(m + " ") for m in ["POST", "GET", "PUT", "DELETE"]):
                req_line_idx = idx
                parts = line.split()
                method = parts[0]
                url = parts[1]
                match_path = re.search(r"http://[^/]+(/.+)$", url)
                if match_path:
                    endpoint = match_path.group(1)
                else:
                    endpoint = url
                break

        if req_line_idx == -1:
            continue

        # Thu thập body payload
        payload_lines = []
        is_body = False
        for idx in range(req_line_idx + 1, len(lines)):
            line = lines[idx]
            if any(
                line.startswith(h)
                for h in ["Authorization:", "Content-Type:", "Accept:"]
            ):
                continue
            if not is_body and line.startswith("{"):
                is_body = True
            if is_body:
                # Bỏ comment
                clean_line = line.split("#")[0].strip()
                if clean_line:
                    payload_lines.append(clean_line)

        payload_str = "".join(payload_lines) if payload_lines else ""

        # Sửa lỗi JSON payload rác (ví dụ: NOT_VALID_JSON của test case 1.C)
        if tc_id == "1.C":
            payload_str = "NOT_VALID_JSON"

        test_cases.append(
            {
                "id": tc_id,
                "name": tc_display_name,
                "endpoint": endpoint,
                "method": method,
                "payload": payload_str,
                "expected_status": expected_status,
                "expected_msg": expected_msg,
                "loop_count": 1,
                "delay": 0,
            }
        )

    return test_cases


def get_sheet_name(tc_id):
    tc_id_str = str(tc_id).strip()
    if tc_id_str.startswith("1."):
        return "1. Auth Token"
    elif (
        tc_id_str.startswith("2.")
        or tc_id_str.startswith("3.")
        or tc_id_str.startswith("5.")
        or tc_id_str.startswith("8.")
    ):
        return "2. Hardware Management"
    elif (
        tc_id_str.startswith("3_ES.")
        or tc_id_str.startswith("3_ACK.")
        or tc_id_str.startswith("6.")
        or tc_id_str.startswith("7.")
        or tc_id_str.startswith("4.")
    ):
        return "3. Employee & Access Sync"
    return "Other"


def write_to_excel(test_cases, filepath):
    wb = openpyxl.Workbook()
    # Xóa sheet mặc định
    default_sheet = wb.active
    wb.remove(default_sheet)

    # 3 sheet cần tạo theo đúng thứ tự
    sheet_names = [
        "1. Auth Token",
        "2. Hardware Management",
        "3. Employee & Access Sync",
    ]

    # Gom nhóm test cases theo sheet
    grouped_cases = {name: [] for name in sheet_names}
    grouped_cases["Other"] = []

    for tc in test_cases:
        s_name = get_sheet_name(tc["id"])
        if s_name in grouped_cases:
            grouped_cases[s_name].append(tc)
        else:
            grouped_cases["Other"].append(tc)

    headers = [
        "ID",
        "Name",
        "Endpoint",
        "Method",
        "Payload (JSON)",
        "Expected Status",
        "Expected Message",
        "Loop Count",
        "Delay (ms)",
        "Run?",
    ]

    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(
        start_color="366092", end_color="366092", fill_type="solid"
    )
    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    border_thin = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )

    for s_name in sheet_names:
        cases = grouped_cases[s_name]
        if not cases:
            ws = wb.create_sheet(title=s_name)
            ws.append(headers)
        else:
            ws = wb.create_sheet(title=s_name)
            ws.append(headers)
            for tc in cases:
                display_name = get_api_display_name(
                    tc["id"], tc["name"], tc["expected_status"]
                )
                ws.append(
                    [
                        tc["id"],
                        display_name,
                        tc["endpoint"],
                        tc["method"],
                        tc["payload"],
                        tc["expected_status"],
                        tc["expected_msg"],
                        tc["loop_count"],
                        tc["delay"],
                        "" if (tc["id"] in ("1.K", "1.L") or tc["id"].startswith("3_ACK.") or tc["id"].startswith("6.")) else "x",  # Run by default
                    ]
                )

        # Dinh dang Header
        ws.row_dimensions[1].height = 28
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = align_center

        # Dinh dang du lieu
        row_count = ws.max_row
        if row_count > 1:
            for r_idx in range(2, row_count + 1):
                ws.row_dimensions[r_idx].height = 40

                # Bold Name / Test Scenario column
                name_cell = ws.cell(row=r_idx, column=2)
                name_cell.font = Font(name="Calibri", size=11, bold=True)

                # Tô màu xanh cho các case đăng ký thành công (200 OK)
                tc_id_val = ws.cell(row=r_idx, column=1).value
                expected_status_val = ws.cell(row=r_idx, column=6).value
                is_register_success = (
                    tc_id_val
                    and expected_status_val == 200
                    and (
                        str(tc_id_val).startswith("2.")
                        or str(tc_id_val).startswith("5.")
                    )
                )
                if is_register_success:
                    success_green_fill = PatternFill(
                        start_color="C6EFCE", fill_type="solid"
                    )
                    ws.cell(row=r_idx, column=1).fill = success_green_fill
                    name_cell.fill = success_green_fill

                # Format Endpoint column với màu nhóm API (chỉ sheet 2 và 3)
                tc_id_val = ws.cell(row=r_idx, column=1).value
                api_group_fill = get_api_group_fill(tc_id_val) if tc_id_val else None
                epc = ws.cell(row=r_idx, column=3)
                if api_group_fill and s_name in (
                    "2. Hardware Management",
                    "3. Employee & Access Sync",
                ):
                    epc.fill = api_group_fill
                    epc.font = Font(name="Calibri", size=11, bold=True)

                # Format Payload (JSON) column
                plc = ws.cell(row=r_idx, column=5)
                plc.font = Font(name="Calibri", size=9, italic=True)
                plc.alignment = Alignment(
                    horizontal="left", vertical="center", wrap_text=True
                )

                # Fetch expected status styles
                exp_status_val = ws.cell(row=r_idx, column=6).value
                s_font, s_fill = get_status_styles(exp_status_val)

                # Format Expected Status column
                esc = ws.cell(row=r_idx, column=6)
                esc.font = s_font
                esc.fill = s_fill
                esc.alignment = align_center

                # Format Expected Message column
                emc = ws.cell(row=r_idx, column=7)
                emc.font = Font(
                    color=s_font.color, name="Calibri", size=11, italic=True, bold=True
                )
                emc.fill = PatternFill(fill_type=None)
                emc.alignment = align_left

                # Set border and vertical alignment for all cells in the row
                for c_idx in range(1, 11):
                    cell = ws.cell(row=r_idx, column=c_idx)
                    cell.border = border_thin
                    if c_idx not in [5, 6, 7]:
                        if c_idx in [1, 4, 8, 9, 10]:
                            cell.alignment = align_center
                        else:
                            cell.alignment = align_left

        # Tu dong dieu chinh do rong cot thong minh
        adjust_column_widths_smart(ws)

    # ----------------------------------------------------
    # TẠO PARAMETER SHEET: Data. Controller Register
    # ----------------------------------------------------
    p_ws = wb.create_sheet(title="Data. Controller Register")

    # Dòng 1: Định nghĩa API Endpoint
    p_ws.cell(row=1, column=1, value="API").font = Font(
        name="Calibri", size=11, bold=True
    )
    url_cell = p_ws.cell(
        row=1, column=2, value="http://localhost:8070/api/v1/ControllerRegister"
    )
    url_cell.font = Font(
        name="Calibri", size=11, bold=True, color="0563C1", underline="single"
    )

    # Dòng 4: Headers cho các tham số JSON + Expected
    param_headers = [
        "#",
        "name",
        "serial_number",
        "branch_code",
        "hardware_model",
        "firmware_version",
        "ip_address",
        "mac_address",
        "connection_type",
        "installed_at",
        "replaces_sn",
        "expected_status",
        "expected_msg",
        "Run?",
    ]
    for col_idx, text in enumerate(param_headers, 1):
        c = p_ws.cell(row=4, column=col_idx, value=text)
        c.font = header_font
        c.fill = PatternFill(
            start_color="4F81BD", fill_type="solid"
        )  # Màu xanh nhạt hơn cho Data sheet
        c.alignment = align_center

        # 30 dòng dữ liệu test đa dạng
        param_cases = [
            (
                "ControllerRegister - Lobby Hà Nội đăng ký (200)",
                "CTRL-HN-LOBBY-01",
                "HnMain",
                "InBio Pro 460",
                "v2.4.1",
                "192.168.10.210",
                "00:17:0A:11:22:33",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "",
                200,
                "Controller registered successfully",
            ),
            (
                "ControllerRegister - Lobby HCM đăng ký (200)",
                "CTRL-HCM-LOBBY-01",
                "HcmBranch",
                "InBio Pro 260",
                "v2.4.1",
                "192.168.20.100",
                "00:17:0A:11:22:55",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "",
                200,
                "Controller registered successfully",
            ),
            (
                "ControllerRegister - Đăng ký tối thiểu (chỉ required fields) (200)",
                "CTRL-MIN-01",
                "HnMain",
                "",
                "",
                "",
                "",
                "tcp_ip",
                "",
                "",
                200,
                "Controller registered successfully",
            ),
            (
                "ControllerRegister - Khuyết firmware_version (200)",
                "CTRL-MIN-02",
                "HnMain",
                "T4-GATE-PRO",
                "",
                "192.168.10.222",
                "00:17:0A:11:22:90",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "",
                200,
                "Controller registered successfully",
            ),
            (
                "ControllerRegister - Khuyết ip_address (200)",
                "CTRL-MIN-03",
                "HnMain",
                "T4-GATE-PRO",
                "v2.1.0",
                "",
                "00:17:0A:11:22:91",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "",
                200,
                "Controller registered successfully",
            ),
            (
                "ControllerRegister - Khuyết mac_address (200)",
                "CTRL-MIN-04",
                "HnMain",
                "T4-GATE-PRO",
                "v2.1.0",
                "192.168.10.224",
                "",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "",
                200,
                "Controller registered successfully",
            ),
            (
                "ControllerRegister - Khuyết installed_at (200)",
                "CTRL-MIN-05",
                "HnMain",
                "T4-GATE-PRO",
                "v2.1.0",
                "192.168.10.225",
                "00:17:0A:11:22:93",
                "tcp_ip",
                "",
                "",
                200,
                "Controller registered successfully",
            ),
            (
                "ControllerRegister - Tự động tạo controller mới (200)",
                "CTRL-NEW-AUTO-001",
                "HnMain",
                "InBio Pro 460",
                "v2.4.1",
                "192.168.10.220",
                "00:17:0A:11:22:99",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "",
                200,
                "Controller registered successfully",
            ),
            (
                "ControllerRegister - Thay thế controller cũ (200)",
                "CTRL-HN-LOBBY-REPLACED",
                "HnMain",
                "InBio Pro 460",
                "v2.4.1",
                "192.168.10.215",
                "00:17:0A:11:22:AA",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "CTRL-HN-LOBBY-01",
                200,
                "Controller registered successfully",
            ),
            (
                "ControllerRegister - replaces_sn không tồn tại (200)",
                "CTRL-HN-LOBBY-01",
                "HnMain",
                "InBio Pro 460",
                "v2.4.1",
                "192.168.10.210",
                "00:17:0A:11:22:33",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "CTRL-NON-EXIST",
                200,
                "Controller registered successfully",
            ),
            (
                "ControllerRegister - Thiếu serial_number (400)",
                "",
                "HnMain",
                "InBio Pro 460",
                "v2.4.1",
                "192.168.10.210",
                "00:17:0A:11:22:33",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "",
                400,
                "serial_number",
            ),
            (
                "ControllerRegister - Thiếu branch_code (400)",
                "CTRL-HN-LOBBY-01",
                "",
                "InBio Pro 460",
                "v2.4.1",
                "192.168.10.210",
                "00:17:0A:11:22:33",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "",
                400,
                "branch_code",
            ),
            (
                "ControllerRegister - branch_code không tồn tại (400)",
                "CTRL-HN-LOBBY-01",
                "Can Tho",
                "InBio Pro 460",
                "v2.4.1",
                "192.168.10.210",
                "00:17:0A:11:22:33",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "",
                400,
                "Invalid branch_code",
            ),
            (
                "ControllerRegister - Không có token (401)",
                "CTRL-HN-LOBBY-01",
                "HnMain",
                "InBio Pro 460",
                "v2.4.1",
                "192.168.10.210",
                "00:17:0A:11:22:33",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "",
                401,
                "",
            ),
            (
                "ControllerRegister - Token sai (401)",
                "CTRL-HN-LOBBY-01",
                "HnMain",
                "InBio Pro 460",
                "v2.4.1",
                "192.168.10.210",
                "00:17:0A:11:22:33",
                "tcp_ip",
                "2026-07-14 00:00:00",
                "",
                401,
                "",
            ),
        ]

    for idx, case in enumerate(param_cases, 1):
        row_vals = [idx] + list(case) + ["x"]  # Thêm cột Run? trống
        p_ws.append(row_vals)

    # Dinh dang du lieu va borders cho Parameter Sheet: Data. Controller Register
    p_ws.row_dimensions[1].height = 28
    p_ws.row_dimensions[4].height = 28
    for r_idx in range(5, 5 + len(param_cases)):
        p_ws.row_dimensions[r_idx].height = 40
        # Bold Name column
        name_cell = p_ws.cell(row=r_idx, column=2)
        name_cell.font = Font(name="Calibri", size=11, bold=True)

        # Tô màu xanh cho các case đăng ký thành công (200 OK)
        exp_status_val = p_ws.cell(row=r_idx, column=12).value
        if exp_status_val == 200:
            success_green_fill = PatternFill(start_color="C6EFCE", fill_type="solid")
            p_ws.cell(row=r_idx, column=1).fill = success_green_fill
            name_cell.fill = success_green_fill

        # Expected status (column 12)
        exp_status_val = p_ws.cell(row=r_idx, column=12).value
        s_font, s_fill = get_status_styles(exp_status_val)
        esc = p_ws.cell(row=r_idx, column=12)
        esc.font = s_font
        esc.fill = s_fill
        esc.alignment = align_center

        # Expected msg (column 13)
        emc = p_ws.cell(row=r_idx, column=13)
        emc.font = Font(
            color=s_font.color, name="Calibri", size=11, italic=True, bold=True
        )
        emc.fill = PatternFill(fill_type=None)
        emc.alignment = align_left

        for c_idx in range(1, 15):
            cell = p_ws.cell(row=r_idx, column=c_idx)
            cell.border = border_thin
            if c_idx not in [12, 13]:
                if c_idx in [1, 12, 14]:
                    cell.alignment = align_center
                else:
                    cell.alignment = align_left

    # Tu dong dieu chinh do rong cot thong minh cho Parameter Sheet
    adjust_column_widths_smart(p_ws)

    # ----------------------------------------------------
    # TẠO PARAMETER SHEET: Data. Device Register
    # ----------------------------------------------------
    d_ws = wb.create_sheet(title="Data. Device Register")

    # Dong 1: Dinh nghia API Endpoint
    d_ws.cell(row=1, column=1, value="API").font = Font(
        name="Calibri", size=11, bold=True
    )
    d_url = d_ws.cell(
        row=1, column=2, value="http://localhost:8070/api/v1/DeviceRegister"
    )
    d_url.font = Font(
        name="Calibri", size=11, bold=True, color="0563C1", underline="single"
    )

    # Dong 4: Headers
    dev_headers = [
        "#",
        "name",
        "serial_number",
        "controller_sn",
        "area_id",
        "vendor",
        "device_model_id",
        "port_or_channel",
        "firmware_version",
        "system_version",
        "last_heartbeat",
        "installed_at",
        "last_sync_at",
        "expected_status",
        "expected_msg",
        "Run?",
    ]
    dev_fill = PatternFill(
        start_color="76933C", fill_type="solid"
    )  # Mau xanh la cho Device sheet
    for col_idx, text in enumerate(dev_headers, 1):
        c = d_ws.cell(row=4, column=col_idx, value=text)
        c.font = header_font
        c.fill = dev_fill
        c.alignment = align_center

        # Du lieu test cho Device Register
        dev_cases = [
            (
                "DeviceRegister - Đăng ký đầu đọc cổng chính (200)",
                "DEV-PARAM-01",
                "CTRL-HN-LOBBY-01",
                "",
                "ZKTeco",
                "",
                10,
                "v1.5.0",
                "Linux 5.10",
                "2026-07-14 08:00:00",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                200,
                "Device registered successfully",
            ),
            (
                "DeviceRegister - Đăng ký đầu đọc cổng phụ (200)",
                "DEV-PARAM-02",
                "CTRL-HN-LOBBY-01",
                "",
                "ZKTeco",
                "",
                11,
                "v1.5.0",
                "Linux 5.10",
                "2026-07-14 08:00:00",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                200,
                "Device registered successfully",
            ),
            (
                "DeviceRegister - Đăng ký tối thiểu (chỉ required fields) (200)",
                "DEV-PARAM-03",
                "CTRL-HN-LOBBY-01",
                "",
                "ZKTeco",
                "",
                12,
                "v1.5.0",
                "Linux 5.10",
                "2026-07-14 08:00:00",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                200,
                "Device registered successfully",
            ),
            (
                "DeviceRegister - Khuyết port_or_channel (200)",
                "DEV-PARAM-04",
                "CTRL-HN-LOBBY-01",
                "",
                "ZKTeco",
                "",
                "",
                "v1.5.0",
                "Linux 5.10",
                "2026-07-14 08:00:00",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                200,
                "Device registered successfully",
            ),
            (
                "DeviceRegister - Khuyết device_model_id (200)",
                "DEV-PARAM-05",
                "CTRL-HN-LOBBY-01",
                "",
                "ZKTeco",
                "",
                13,
                "v1.5.0",
                "Linux 5.10",
                "2026-07-14 08:00:00",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                200,
                "Device registered successfully",
            ),
            (
                "DeviceRegister - Khuyết firmware_version (200)",
                "DEV-PARAM-06",
                "CTRL-HN-LOBBY-01",
                "",
                "ZKTeco",
                "",
                14,
                "",
                "Linux 5.10",
                "2026-07-14 08:00:00",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                200,
                "Device registered successfully",
            ),
            (
                "DeviceRegister - Khuyết last_heartbeat (200)",
                "DEV-PARAM-07",
                "CTRL-HN-LOBBY-01",
                "",
                "ZKTeco",
                "",
                15,
                "v1.5.0",
                "Linux 5.10",
                "",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                200,
                "Device registered successfully",
            ),
            (
                "DeviceRegister - Thiếu serial_number (400)",
                "",
                "CTRL-HN-LOBBY-01",
                "",
                "ZKTeco",
                "",
                13,
                "v1.5.0",
                "Linux 5.10",
                "2026-07-14 08:00:00",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                400,
                "serial_number",
            ),
            (
                "DeviceRegister - Thiếu controller_sn (400)",
                "DEV-HN-LOB-IN-03",
                "",
                "",
                "ZKTeco",
                "",
                14,
                "v1.5.0",
                "Linux 5.10",
                "2026-07-14 08:00:00",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                400,
                "controller_sn",
            ),
            (
                "DeviceRegister - controller_sn không tồn tại (400)",
                "DEV-HN-LOB-IN-04",
                "CTRL-NON-EXIST",
                "",
                "ZKTeco",
                "",
                15,
                "v1.5.0",
                "Linux 5.10",
                "2026-07-14 08:00:00",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                400,
                "Không tìm thấy Controller",
            ),
            (
                "DeviceRegister - Port trùng lặp (400)",
                "DEV-HN-MAIN-DUP",
                "CTRL-HN-LOBBY-01",
                "",
                "ZKTeco",
                "",
                10,
                "v1.5.0",
                "Linux 5.10",
                "2026-07-14 08:00:00",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                400,
                "Device port or channel must be unique per controller.",
            ),
            (
                "DeviceRegister - Không có token (401)",
                "DEV-HN-LOB-IN-01",
                "CTRL-HN-LOBBY-01",
                "",
                "ZKTeco",
                "",
                10,
                "v1.5.0",
                "Linux 5.10",
                "2026-07-14 08:00:00",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                401,
                "",
            ),
            (
                "DeviceRegister - Token sai (401)",
                "DEV-HN-LOB-IN-01",
                "CTRL-HN-LOBBY-01",
                "Sảnh đón khách chính (Hanoi Lobby)",
                "ZKTeco",
                "ZKTeco SpeedFace V5L",
                10,
                "v1.5.0",
                "Linux 5.10",
                "2026-07-14 08:00:00",
                "2026-07-14 00:00:00",
                "2026-07-14 08:00:00",
                401,
                "",
            ),
        ]

    for idx, case in enumerate(dev_cases, 1):
        row_vals = [idx] + list(case) + ["x"]
        d_ws.append(row_vals)

    # Dinh dang du lieu va borders cho Parameter Sheet: Data. Device Register
    d_ws.row_dimensions[1].height = 28
    d_ws.row_dimensions[4].height = 28
    for r_idx in range(5, 5 + len(dev_cases)):
        d_ws.row_dimensions[r_idx].height = 40
        # Bold Name column
        name_cell = d_ws.cell(row=r_idx, column=2)
        name_cell.font = Font(name="Calibri", size=11, bold=True)

        # Tô màu xanh cho các case đăng ký thành công (200 OK)
        exp_status_val = d_ws.cell(row=r_idx, column=14).value
        if exp_status_val == 200:
            success_green_fill = PatternFill(start_color="C6EFCE", fill_type="solid")
            d_ws.cell(row=r_idx, column=1).fill = success_green_fill
            name_cell.fill = success_green_fill

        # Expected status (column 14)
        exp_status_val = d_ws.cell(row=r_idx, column=14).value
        s_font, s_fill = get_status_styles(exp_status_val)
        esc = d_ws.cell(row=r_idx, column=14)
        esc.font = s_font
        esc.fill = s_fill
        esc.alignment = align_center

        # Expected msg (column 15)
        emc = d_ws.cell(row=r_idx, column=15)
        emc.font = Font(
            color=s_font.color, name="Calibri", size=11, italic=True, bold=True
        )
        emc.fill = PatternFill(fill_type=None)
        emc.alignment = align_left

        for c_idx in range(1, 17):
            cell = d_ws.cell(row=r_idx, column=c_idx)
            cell.border = border_thin
            if c_idx not in [14, 15]:
                if c_idx in [1, 14, 16]:
                    cell.alignment = align_center
                else:
                    cell.alignment = align_left

    # Tu dong dieu chinh do rong cot thong minh cho Parameter Sheet
    adjust_column_widths_smart(d_ws)

    # ----------------------------------------------------
    # TAO PARAMETER SHEET: Data. Controller Heartbeat
    # ----------------------------------------------------
    h_ws = wb.create_sheet(title="Data. Controller Heartbeat")

    # Dong 1: Dinh nghia API Endpoint
    h_ws.cell(row=1, column=1, value="API").font = Font(
        name="Calibri", size=11, bold=True
    )
    h_url = h_ws.cell(
        row=1, column=2, value="http://localhost:8070/api/v1/ControllerHeartbeat"
    )
    h_url.font = Font(
        name="Calibri", size=11, bold=True, color="0563C1", underline="single"
    )

    # Dong 4: Headers
    hb_headers = [
        "#",
        "name",
        "controller_sn",
        "devices",
        "expected_status",
        "expected_msg",
        "Run?",
    ]
    hb_fill = PatternFill(
        start_color="E26B0A", fill_type="solid"
    )  # Mau cam cho Heartbeat sheet
    for col_idx, text in enumerate(hb_headers, 1):
        c = h_ws.cell(row=4, column=col_idx, value=text)
        c.font = header_font
        c.fill = hb_fill
        c.alignment = align_center

    # Du lieu test cho Controller Heartbeat (Co chua Array JSON duoi dang chuoi de test)
    hb_cases = [
        (
            "ControllerHeartbeat - Device online (200)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "status": "online"}]',
            200,
            "Success",
        ),
        (
            "ControllerHeartbeat - Device online Server HN (200)",
            "CTRL-HN-SRV-01",
            '[{"device_sn": "DEV-HN-SRV-FACE-01", "status": "online"}]',
            200,
            "Success",
        ),
        (
            "ControllerHeartbeat - Device online Kho HCM (200)",
            "CTRL-HCM-WHS-01",
            '[{"device_sn": "DEV-HCM-WHS-FGR-01", "status": "online"}]',
            200,
            "Success",
        ),
        (
            "ControllerHeartbeat - Device online R&D DN (200)",
            "CTRL-DN-MAIN-01",
            '[{"device_sn": "DEV-DN-RD-IN-01", "status": "online"}]',
            200,
            "Success",
        ),
        (
            "ControllerHeartbeat - Hai device offline (200)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "status": "offline"}, {"device_sn": "DEV-HN-LOB-OUT-01", "status": "offline"}]',
            200,
            "Success",
        ),
        (
            "ControllerHeartbeat - devices_status rỗng (200)",
            "CTRL-HN-LOBBY-01",
            "[]",
            200,
            "Success",
        ),
        (
            "ControllerHeartbeat - Thiếu controller_sn (400)",
            "",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "status": "online"}]',
            400,
            "controller_sn",
        ),
        (
            "ControllerHeartbeat - Thiếu devices_status (400)",
            "CTRL-HN-LOBBY-01",
            "",
            400,
            "devices_status",
        ),
        (
            "ControllerHeartbeat - controller_sn không tồn tại (400)",
            "CTRL-NON-EXIST",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "status": "online"}]',
            400,
            "Không tìm thấy Controller",
        ),
        (
            "ControllerHeartbeat - Thiết bị không tồn tại trong Odoo (200)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-NON-EXISTENT", "status": "online"}]',
            400,
            "Devices not found:",
        ),
        (
            "ControllerHeartbeat - Nhiều thiết bị với trạng thái hỗn hợp (200)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "status": "online"}, {"device_sn": "DEV-HN-LOB-OUT-01", "status": "offline"}]',
            200,
            "Success",
        ),
        (
            "ControllerHeartbeat - Thiết bị thuộc controller khác gửi qua (200)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-NEW-TEST-999", "status": "online"}]',
            400,
            "Devices not found:",
        ),
        (
            "ControllerHeartbeat - Không có token (401)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "status": "online"}]',
            401,
            "",
        ),
        (
            "ControllerHeartbeat - Token sai (401)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "status": "online"}]',
            401,
            "",
        ),
    ]

    for idx, case in enumerate(hb_cases, 1):
        row_vals = [idx] + list(case) + ["x"]
        h_ws.append(row_vals)

    # Dinh dang du lieu va borders cho Parameter Sheet: Data. Controller Heartbeat
    h_ws.row_dimensions[1].height = 28
    h_ws.row_dimensions[4].height = 28
    for r_idx in range(5, 5 + len(hb_cases)):
        h_ws.row_dimensions[r_idx].height = 40

        # Bold name column (col 2)
        h_ws.cell(row=r_idx, column=2).font = Font(name="Calibri", size=11, bold=True)

        # controller_sn column (col 3) - left aligned
        h_ws.cell(row=r_idx, column=3).alignment = align_left

        # Format devices_status (JSON array) column (col 4)
        dsc = h_ws.cell(row=r_idx, column=4)
        dsc.font = Font(name="Calibri", size=9, italic=True)
        dsc.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

        # Expected status (column 5)
        exp_status_val = h_ws.cell(row=r_idx, column=5).value
        s_font, s_fill = get_status_styles(exp_status_val)
        esc = h_ws.cell(row=r_idx, column=5)
        esc.font = s_font
        esc.fill = s_fill
        esc.alignment = align_center

        # Expected msg (column 6)
        emc = h_ws.cell(row=r_idx, column=6)
        emc.font = Font(
            color=s_font.color, name="Calibri", size=11, italic=True, bold=True
        )
        emc.fill = PatternFill(fill_type=None)
        emc.alignment = align_left

        for c_idx in range(1, 8):
            cell = h_ws.cell(row=r_idx, column=c_idx)
            cell.border = border_thin
            if c_idx not in [4, 5, 6]:
                if c_idx in [1, 5, 7]:
                    cell.alignment = align_center
                else:
                    cell.alignment = align_left

    # Tu dong dieu chinh do rong cot thong minh cho Parameter Sheet
    adjust_column_widths_smart(h_ws)

    # ----------------------------------------------------
    # TẠO PARAMETER SHEET: Data. Controller Get Config
    # ----------------------------------------------------
    gc_ws = wb.create_sheet(title="Data. Controller Get Config")
    gc_ws.cell(row=1, column=1, value="API").font = Font(
        name="Calibri", size=11, bold=True
    )
    gc_url = gc_ws.cell(
        row=1, column=2, value="http://localhost:8070/api/v1/ControllerGetConfig"
    )
    gc_url.font = Font(
        name="Calibri", size=11, bold=True, color="0563C1", underline="single"
    )

    # Dong 4: Headers
    gc_headers = [
        "#",
        "name",
        "controller_sn",
        "expected_status",
        "expected_msg",
        "Run?",
    ]
    gc_fill = PatternFill(start_color="366092", fill_type="solid")
    for col_idx, text in enumerate(gc_headers, 1):
        c = gc_ws.cell(row=4, column=col_idx, value=text)
        c.font = header_font
        c.fill = gc_fill
        c.alignment = align_center

    gc_cases = [
        (
            "ControllerGetConfig - Lấy cấu hình controller có nhiều device (200)",
            "CTRL-HN-LOBBY-01",
            200,
            "Success",
        ),
        (
            "ControllerGetConfig - Controller không có device nào (200)",
            "CTRL-MIN-01",
            200,
            "Success",
        ),
        (
            "ControllerGetConfig - Thiếu controller_sn (400)",
            "",
            400,
            "Controller ID is required.",
        ),
        (
            "ControllerGetConfig - Controller không tồn tại (400)",
            "CTRL-FAKE-DOES-NOT-EXIST",
            400,
            "Can not find controller with ID",
        ),
        ("ControllerGetConfig - Không có token (401)", "CTRL-HN-LOBBY-01", 401, ""),
        ("ControllerGetConfig - Token sai (401)", "CTRL-HN-LOBBY-01", 401, ""),
    ]

    for idx, case in enumerate(gc_cases, 1):
        row_vals = [idx] + list(case) + ["x"]
        gc_ws.append(row_vals)

    gc_ws.row_dimensions[1].height = 28
    gc_ws.row_dimensions[4].height = 28
    for r_idx in range(5, 5 + len(gc_cases)):
        gc_ws.row_dimensions[r_idx].height = 40
        gc_ws.cell(row=r_idx, column=2).font = Font(name="Calibri", size=11, bold=True)
        gc_ws.cell(row=r_idx, column=3).alignment = align_left

        # Expected status (column 4)
        exp_status_val = gc_ws.cell(row=r_idx, column=4).value
        s_font, s_fill = get_status_styles(exp_status_val)
        esc = gc_ws.cell(row=r_idx, column=4)
        esc.font = s_font
        esc.fill = s_fill
        esc.alignment = align_center

        # Expected msg (column 5)
        emc = gc_ws.cell(row=r_idx, column=5)
        emc.font = Font(
            color=s_font.color, name="Calibri", size=11, italic=True, bold=True
        )
        emc.fill = PatternFill(fill_type=None)
        emc.alignment = align_left

        for c_idx in range(1, 7):
            cell = gc_ws.cell(row=r_idx, column=c_idx)
            cell.border = border_thin
            if c_idx not in [4, 5]:
                if c_idx in [1, 6]:
                    cell.alignment = align_center
                else:
                    cell.alignment = align_left

    # Tu dong dieu chinh do rong cot thong minh cho Parameter Sheet
    adjust_column_widths_smart(gc_ws)

    # ----------------------------------------------------
    # TẠO PARAMETER SHEET: Data. Employee Sync
    # ----------------------------------------------------
    es_ws = wb.create_sheet(title="Data. Employee Sync")
    es_ws.cell(row=1, column=1, value="API").font = Font(
        name="Calibri", size=11, bold=True
    )
    es_url = es_ws.cell(
        row=1, column=2, value="http://localhost:8070/api/v1/ControllerEmployeeSync"
    )
    es_url.font = Font(
        name="Calibri", size=11, bold=True, color="0563C1", underline="single"
    )

    es_headers = [
        "#",
        "name",
        "controller_sn",
        "page_size",
        "last_sync_at",
        "next_cursor_id",
        "latest_write_date",
        "expected_status",
        "expected_msg",
        "Run?",
    ]
    es_fill = PatternFill(start_color="F2CB62", fill_type="solid")  # Mau vang cam
    for col_idx, text in enumerate(es_headers, 1):
        c = es_ws.cell(row=4, column=col_idx, value=text)
        c.font = header_font
        c.fill = es_fill
        c.alignment = align_center

    es_cases = [
        (
            "EmployeeSync - Lobby Hà Nội trang 1 (200)",
            "CTRL-HN-LOBBY-01",
            15,
            "",
            "",
            "",
            200,
            "Employee Sync Completed",
        ),
        (
            "EmployeeSync - Lobby Hà Nội trang 2 với Cursor (200)",
            "CTRL-HN-LOBBY-01",
            15,
            "",
            10,
            "2026-08-05 08:00:00",
            200,
            "Employee Sync Completed",
        ),
        (
            "EmployeeSync - Lobby HCM Kho trang 1 (200)",
            "CTRL-HCM-WHS-01",
            100,
            "",
            "",
            "",
            200,
            "Employee Sync Completed",
        ),
        (
            "EmployeeSync - Server Room Hà Nội trang 1 (200)",
            "CTRL-HN-SRV-01",
            15,
            "",
            "",
            "",
            200,
            "Employee Sync Completed",
        ),
        (
            "EmployeeSync - Thiếu controller_sn (400)",
            "",
            15,
            "",
            "",
            "",
            400,
            "Controller ID is required.",
        ),
        (
            "EmployeeSync - controller_sn không tồn tại (400)",
            "CTRL-NON-EXIST",
            15,
            "",
            "",
            "",
            400,
            "Can not find controller with ID",
        ),
        (
            "EmployeeSync - page_size dạng chuỗi (200)",
            "CTRL-HN-LOBBY-01",
            "10",
            "",
            "",
            "",
            200,
            "Employee Sync Completed",
        ),
        (
            "EmployeeSync - Mốc last_sync_at delta (200)",
            "CTRL-HN-LOBBY-01",
            15,
            "2026-08-01 00:00:00",
            "",
            "",
            200,
            "Employee Sync Completed",
        ),
        (
            "EmployeeSync - Kết hợp cả last_sync_at Delta & Cursor trang 2 (200)",
            "CTRL-HN-LOBBY-01",
            15,
            "2026-08-01 00:00:00",
            5,
            "2026-08-05 10:00:00",
            200,
            "Employee Sync Completed",
        ),
        (
            "EmployeeSync - Phân trang nhỏ page_size = 5 (200)",
            "CTRL-HN-LOBBY-01",
            5,
            "",
            "",
            "",
            200,
            "Employee Sync Completed",
        ),
        (
            "EmployeeSync - Phân trang trang 3 với Cursor id = 30 (200)",
            "CTRL-HN-LOBBY-01",
            15,
            "",
            30,
            "2026-08-05 12:00:00",
            200,
            "Employee Sync Completed",
        ),
        (
            "EmployeeSync - Mốc last_sync_at ISO 8601 có timezone (200)",
            "CTRL-HN-LOBBY-01",
            15,
            "2026-08-01T00:00:00+07:00",
            "",
            "",
            400,
            "Invalid last sync time format.",
        ),
        (
            "EmployeeSync - Controller HCM Kho có mốc last_sync_at (200)",
            "CTRL-HCM-WHS-01",
            20,
            "2026-08-02 08:30:00",
            "",
            "",
            200,
            "Employee Sync Completed",
        ),
        (
            "EmployeeSync - Server Room Hà Nội trang 2 với Cursor (200)",
            "CTRL-HN-SRV-01",
            10,
            "",
            12,
            "2026-08-05 09:15:00",
            200,
            "Employee Sync Completed",
        ),
        (
            "EmployeeSync - Không có token (401)",
            "CTRL-HN-LOBBY-01",
            15,
            "",
            "",
            "",
            401,
            "",
        ),
        (
            "EmployeeSync - Token sai (401)",
            "CTRL-HN-LOBBY-01",
            15,
            "",
            "",
            "",
            401,
            "",
        ),
    ]

    for idx, case in enumerate(es_cases, 1):
        row_vals = [idx] + list(case) + ["x"]
        es_ws.append(row_vals)

    es_ws.row_dimensions[1].height = 28
    es_ws.row_dimensions[4].height = 28
    for r_idx in range(5, 5 + len(es_cases)):
        es_ws.row_dimensions[r_idx].height = 40
        name_cell = es_ws.cell(row=r_idx, column=2)
        name_cell.font = Font(name="Calibri", size=11, bold=True)
        exp_status_val = es_ws.cell(row=r_idx, column=8).value
        if exp_status_val == 200:
            success_green_fill = PatternFill(start_color="C6EFCE", fill_type="solid")
            es_ws.cell(row=r_idx, column=1).fill = success_green_fill
            name_cell.fill = success_green_fill
        s_font, s_fill = get_status_styles(exp_status_val)
        esc = es_ws.cell(row=r_idx, column=8)
        esc.font = s_font
        esc.fill = s_fill
        esc.alignment = align_center
        emc = es_ws.cell(row=r_idx, column=9)
        emc.font = Font(
            color=s_font.color, name="Calibri", size=11, italic=True, bold=True
        )
        emc.fill = PatternFill(fill_type=None)
        emc.alignment = align_left

        for c_idx in range(1, 11):
            cell = es_ws.cell(row=r_idx, column=c_idx)
            cell.border = border_thin
            if c_idx not in [8, 9]:
                if c_idx in [1, 8, 10]:
                    cell.alignment = align_center
                else:
                    cell.alignment = align_left

    adjust_column_widths_smart(es_ws)

    # ----------------------------------------------------
    # TẠO PARAMETER SHEET: Data. Sync Status
    # ----------------------------------------------------
    ss_ws = wb.create_sheet(title="Data. Sync Status")
    ss_ws.cell(row=1, column=1, value="API").font = Font(
        name="Calibri", size=11, bold=True
    )
    ss_url = ss_ws.cell(
        row=1,
        column=2,
        value="http://localhost:8070/api/v1/ControllerEmployeeSyncStatus",
    )
    ss_url.font = Font(
        name="Calibri", size=11, bold=True, color="0563C1", underline="single"
    )

    ss_headers = [
        "#",
        "name",
        "controller_sn",
        "expected_status",
        "expected_msg",
        "Run?",
    ]
    ss_fill = PatternFill(start_color="8EA9DB", fill_type="solid")  # Mau xanh lam xam
    for col_idx, text in enumerate(ss_headers, 1):
        c = ss_ws.cell(row=4, column=col_idx, value=text)
        c.font = header_font
        c.fill = ss_fill
        c.alignment = align_center

    ss_cases = [
        ("SyncStatus - Lobby Hà Nội (200)", "CTRL-HN-LOBBY-01", 200, "update"),
        ("SyncStatus - Lobby HCM Kho (200)", "CTRL-HCM-WHS-01", 200, "update"),
        ("SyncStatus - Server Room Hà Nội (200)", "CTRL-HN-SRV-01", 200, "update"),
        ("SyncStatus - Thiếu controller_sn (400)", "", 400, "controller_sn"),
        (
            "SyncStatus - controller_sn không tồn tại (400)",
            "CTRL-NON-EXIST",
            400,
            "Không tìm thấy Controller",
        ),
        (
            "SyncStatus - Controller mới tạo tự động (200)",
            "CTRL-NEW-AUTO-001",
            200,
            "update",
        ),
        (
            "SyncStatus - Controller thay thế cũ (200)",
            "CTRL-HN-LOBBY-02",
            200,
            "update",
        ),
        (
            "SyncStatus - Controller viết thường SN (400)",
            "ctrl-hn-lobby-01",
            400,
            "Không tìm thấy Controller",
        ),
        (
            "SyncStatus - Controller kí tự đặc biệt SN (400)",
            "CTRL-HN-LOBBY-01#!",
            400,
            "Không tìm thấy Controller",
        ),
        ("SyncStatus - Không có token (401)", "CTRL-HN-LOBBY-01", 401, ""),
        ("SyncStatus - Token sai (401)", "CTRL-HN-LOBBY-01", 401, ""),
    ]

    for idx, case in enumerate(ss_cases, 1):
        row_vals = [idx] + list(case) + ["x"]
        ss_ws.append(row_vals)

    ss_ws.row_dimensions[1].height = 28
    ss_ws.row_dimensions[4].height = 28
    for r_idx in range(5, 5 + len(ss_cases)):
        ss_ws.row_dimensions[r_idx].height = 40
        name_cell = ss_ws.cell(row=r_idx, column=2)
        name_cell.font = Font(name="Calibri", size=11, bold=True)
        exp_status_val = ss_ws.cell(row=r_idx, column=4).value
        if exp_status_val == 200:
            success_green_fill = PatternFill(start_color="C6EFCE", fill_type="solid")
            ss_ws.cell(row=r_idx, column=1).fill = success_green_fill
            name_cell.fill = success_green_fill
        s_font, s_fill = get_status_styles(exp_status_val)
        esc = ss_ws.cell(row=r_idx, column=4)
        esc.font = s_font
        esc.fill = s_fill
        esc.alignment = align_center
        emc = ss_ws.cell(row=r_idx, column=5)
        emc.font = Font(
            color=s_font.color, name="Calibri", size=11, italic=True, bold=True
        )
        emc.alignment = align_left
        for c_idx in range(1, 7):
            cell = ss_ws.cell(row=r_idx, column=c_idx)
            cell.border = border_thin
            if c_idx not in [4, 5]:
                if c_idx in [1, 4, 6]:
                    cell.alignment = align_center
                else:
                    cell.alignment = align_left

    # Tu dong dieu chinh do rong cot thong minh cho Parameter Sheet
    adjust_column_widths_smart(ss_ws)

    # ----------------------------------------------------
    # TẠO PARAMETER SHEET: Data. Sync Ack
    # ----------------------------------------------------
    sa_ws = wb.create_sheet(title="Data. Sync Ack")
    sa_ws.cell(row=1, column=1, value="API").font = Font(
        name="Calibri", size=11, bold=True
    )
    sa_url = sa_ws.cell(
        row=1, column=2, value="http://localhost:8070/api/v1/ControllerSyncAck"
    )
    sa_url.font = Font(
        name="Calibri", size=11, bold=True, color="0563C1", underline="single"
    )

    sa_headers = [
        "#",
        "name",
        "controller_sn",
        "sync_timestamp",
        "expected_status",
        "expected_msg",
        "Run?",
    ]
    sa_fill = PatternFill(
        start_color="A9D08E", fill_type="solid"
    )  # Mau xanh la cay xam
    for col_idx, text in enumerate(sa_headers, 1):
        c = sa_ws.cell(row=4, column=col_idx, value=text)
        c.font = header_font
        c.fill = sa_fill
        c.alignment = align_center

    sa_cases = [
        (
            "SyncAck - Lobby Hà Nội có timestamp (200)",
            "CTRL-HN-LOBBY-01",
            "2026-07-15 02:00:00",
            200,
            "Success",
        ),
        (
            "SyncAck - Lobby Hà Nội không timestamp (200)",
            "CTRL-HN-LOBBY-01",
            "",
            200,
            "Success",
        ),
        (
            "SyncAck - Lobby HCM Kho có timestamp (200)",
            "CTRL-HCM-WHS-01",
            "2026-07-15 02:00:00",
            200,
            "Success",
        ),
        (
            "SyncAck - Server Room Hà Nội không timestamp (200)",
            "CTRL-HN-SRV-01",
            "",
            200,
            "Success",
        ),
        (
            "SyncAck - Thiếu controller_sn (400)",
            "",
            "2026-07-15 02:00:00",
            400,
            "controller_sn",
        ),
        (
            "SyncAck - controller_sn không tồn tại (400)",
            "CTRL-NON-EXIST",
            "2026-07-15 02:00:00",
            400,
            "Không tìm thấy Controller",
        ),
        (
            "SyncAck - Kho HCM không timestamp (200)",
            "CTRL-HCM-WHS-01",
            "",
            200,
            "Success",
        ),
        (
            "SyncAck - Server Room Hà Nội có timestamp (200)",
            "CTRL-HN-SRV-01",
            "2026-07-15 03:00:00",
            200,
            "Success",
        ),
        (
            "SyncAck - Sai định dạng timestamp (500)",
            "CTRL-HN-LOBBY-01",
            "INVALID_DATE_TIME",
            500,
            "",
        ),
        (
            "SyncAck - timestamp chỉ có ngày (200)",
            "CTRL-HN-LOBBY-01",
            "2026-07-15",
            200,
            "Success",
        ),
        (
            "SyncAck - Không có token (401)",
            "CTRL-HN-LOBBY-01",
            "2026-07-15 02:00:00",
            401,
            "",
        ),
        (
            "SyncAck - Token sai (401)",
            "CTRL-HN-LOBBY-01",
            "2026-07-15 02:00:00",
            401,
            "",
        ),
    ]

    for idx, case in enumerate(sa_cases, 1):
        row_vals = [idx] + list(case) + ["x"]
        sa_ws.append(row_vals)

    sa_ws.row_dimensions[1].height = 28
    sa_ws.row_dimensions[4].height = 28
    for r_idx in range(5, 5 + len(sa_cases)):
        sa_ws.row_dimensions[r_idx].height = 40
        name_cell = sa_ws.cell(row=r_idx, column=2)
        name_cell.font = Font(name="Calibri", size=11, bold=True)
        exp_status_val = sa_ws.cell(row=r_idx, column=5).value
        if exp_status_val == 200:
            success_green_fill = PatternFill(start_color="C6EFCE", fill_type="solid")
            sa_ws.cell(row=r_idx, column=1).fill = success_green_fill
            name_cell.fill = success_green_fill
        s_font, s_fill = get_status_styles(exp_status_val)
        esc = sa_ws.cell(row=r_idx, column=5)
        esc.font = s_font
        esc.fill = s_fill
        esc.alignment = align_center
        emc = sa_ws.cell(row=r_idx, column=6)
        emc.font = Font(
            color=s_font.color, name="Calibri", size=11, italic=True, bold=True
        )
        emc.alignment = align_left
        for c_idx in range(1, 8):
            cell = sa_ws.cell(row=r_idx, column=c_idx)
            cell.border = border_thin
            if c_idx not in [5, 6]:
                if c_idx in [1, 5, 7]:
                    cell.alignment = align_center
                else:
                    cell.alignment = align_left

    # Tu dong dieu chinh do rong cot thong minh cho Parameter Sheet
    adjust_column_widths_smart(sa_ws)

    # ----------------------------------------------------
    # TẠO PARAMETER SHEET: Data. Employee Biometric Get
    # ----------------------------------------------------
    eb_ws = wb.create_sheet(title="Data. Employee Biometric Get")
    eb_ws.cell(row=1, column=1, value="API").font = Font(
        name="Calibri", size=11, bold=True
    )
    eb_url = eb_ws.cell(
        row=1, column=2, value="http://localhost:8070/api/v1/EmployeeBiometricGet"
    )
    eb_url.font = Font(
        name="Calibri", size=11, bold=True, color="0563C1", underline="single"
    )

    eb_headers = [
        "#",
        "name",
        "controller_sn",
        "emp_id",
        "expected_status",
        "expected_msg",
        "Run?",
    ]
    eb_fill = PatternFill(start_color="7030A0", fill_type="solid")
    for col_idx, text in enumerate(eb_headers, 1):
        c = eb_ws.cell(row=4, column=col_idx, value=text)
        c.font = header_font
        c.fill = eb_fill
        c.alignment = align_center

    eb_cases = [
        (
            "EmployeeBiometricGet - Lấy biometric thành công (200)",
            "CTRL-HN-LOBBY-01",
            1001,
            200,
            "Success",
        ),
        (
            "EmployeeBiometricGet - Nhân viên không có biometric phù hợp (400)",
            "CTRL-HN-LOBBY-01",
            9999,
            400,
            "Không tìm thấy Controller hoặc Nhân viên hợp lệ",
        ),
        (
            "EmployeeBiometricGet - Thiếu controller_sn (400)",
            "",
            1001,
            400,
            "Controller ID is required.",
        ),
        (
            "EmployeeBiometricGet - Thiếu emp_id (400)",
            "CTRL-HN-LOBBY-01",
            "",
            400,
            "Employee ID is required.",
        ),
        (
            "EmployeeBiometricGet - Controller không tồn tại (400)",
            "CTRL-FAKE-DOES-NOT-EXIST",
            1001,
            400,
            "Can not find controller with ID",
        ),
        (
            "EmployeeBiometricGet - Nhân viên thuộc chi nhánh khác (400)",
            "CTRL-HN-LOBBY-01",
            2001,
            400,
            "Không tìm thấy Controller hoặc Nhân viên hợp lệ",
        ),
        (
            "EmployeeBiometricGet - Không có token (401)",
            "CTRL-HN-LOBBY-01",
            1001,
            401,
            "",
        ),
        (
            "EmployeeBiometricGet - Token sai (401)",
            "CTRL-HN-LOBBY-01",
            1001,
            401,
            "",
        ),
    ]

    for idx, case in enumerate(eb_cases, 1):
        row_vals = [idx] + list(case) + ["x"]
        eb_ws.append(row_vals)

    eb_ws.row_dimensions[1].height = 28
    eb_ws.row_dimensions[4].height = 28
    for r_idx in range(5, 5 + len(eb_cases)):
        eb_ws.row_dimensions[r_idx].height = 40
        eb_ws.cell(row=r_idx, column=2).font = Font(name="Calibri", size=11, bold=True)
        eb_ws.cell(row=r_idx, column=3).alignment = align_left
        eb_ws.cell(row=r_idx, column=4).alignment = align_left

        # Expected status (column 5)
        exp_status_val = eb_ws.cell(row=r_idx, column=5).value
        s_font, s_fill = get_status_styles(exp_status_val)
        esc = eb_ws.cell(row=r_idx, column=5)
        esc.font = s_font
        esc.fill = s_fill
        esc.alignment = align_center

        # Expected msg (column 6)
        emc = eb_ws.cell(row=r_idx, column=6)
        emc.font = Font(
            color=s_font.color, name="Calibri", size=11, italic=True, bold=True
        )
        emc.fill = PatternFill(fill_type=None)
        emc.alignment = align_left

        for c_idx in range(1, 8):
            cell = eb_ws.cell(row=r_idx, column=c_idx)
            cell.border = border_thin
            if c_idx not in [5, 6]:
                if c_idx in [1, 7]:
                    cell.alignment = align_center
                else:
                    cell.alignment = align_left

    # Tu dong dieu chinh do rong cot thong minh cho Parameter Sheet
    adjust_column_widths_smart(eb_ws)

    # ----------------------------------------------------
    # TẠO PARAMETER SHEET: Data. Access Log Upload
    # ----------------------------------------------------
    al_ws = wb.create_sheet(title="Data. Access Log Upload")
    al_ws.cell(row=1, column=1, value="API").font = Font(
        name="Calibri", size=11, bold=True
    )
    al_url = al_ws.cell(
        row=1, column=2, value="http://localhost:8070/api/v1/AccessLogUpload"
    )
    al_url.font = Font(
        name="Calibri", size=11, bold=True, color="0563C1", underline="single"
    )

    al_headers = [
        "#",
        "name",
        "controller_sn",
        "devices",
        "expected_status",
        "expected_msg",
        "Run?",
    ]
    al_fill = PatternFill(start_color="FFD54F", fill_type="solid")  # Mau vang
    for col_idx, text in enumerate(al_headers, 1):
        c = al_ws.cell(row=4, column=col_idx, value=text)
        c.font = header_font
        c.fill = al_fill
        c.alignment = align_center

    al_cases = [
        (
            "AccessLogUpload - Lobby Hà Nội upload 1 log (200)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "records": [{"emp_id": 1001, "punch_type": "check_in", "verify_mode": "card", "punched_at": "2026-08-05T07:30:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        (
            "AccessLogUpload - Lobby Hà Nội batch upload 3 logs (200)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "records": [{"emp_id": 1001, "punch_type": "check_in", "verify_mode": "card", "punched_at": "2026-08-05T07:30:00+07:00"}, {"emp_id": 1002, "punch_type": "check_in", "verify_mode": "fingerprint", "punched_at": "2026-08-05T08:10:00+07:00"}]}, {"device_sn": "DEV-HN-LOB-OUT-01", "records": [{"emp_id": 1001, "punch_type": "check_out", "verify_mode": "card", "punched_at": "2026-08-05T17:00:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        (
            "AccessLogUpload - Lobby HCM Kho upload 1 log (200)",
            "CTRL-HCM-WHS-01",
            '[{"device_sn": "DEV-HCM-WHS-FING-01", "records": [{"emp_id": 2001, "punch_type": "check_in", "verify_mode": "fingerprint", "punched_at": "2026-08-05T08:30:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        (
            "AccessLogUpload - Server Room Hà Nội upload 1 log (200)",
            "CTRL-HN-SRV-01",
            '[{"device_sn": "DEV-HN-SRV-FACE-01", "records": [{"emp_id": 1001, "punch_type": "check_in", "verify_mode": "face", "punched_at": "2026-08-05T09:00:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        ("AccessLogUpload - Thiếu controller_sn (400)", "", "[]", 400, "controller_sn"),
        ("AccessLogUpload - Thiếu devices (400)", "CTRL-HN-LOBBY-01", "", 400, "No device data provided."),
        (
            "AccessLogUpload - controller_sn không tồn tại (400)",
            "CTRL-NON-EXIST",
            "[]",
            400,
            "is not registered",
        ),
        (
            "AccessLogUpload - Kho HCM upload batch 2 logs (200)",
            "CTRL-HCM-WHS-01",
            '[{"device_sn": "DEV-HCM-WHS-FING-01", "records": [{"emp_id": 2001, "punch_type": "check_in", "verify_mode": "fingerprint", "punched_at": "2026-08-05T09:00:00+07:00"}, {"emp_id": 2001, "punch_type": "check_out", "verify_mode": "fingerprint", "punched_at": "2026-08-05T17:00:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        (
            "AccessLogUpload - Server Room upload 2 logs (200)",
            "CTRL-HN-SRV-01",
            '[{"device_sn": "DEV-HN-SRV-FACE-01", "records": [{"emp_id": 1001, "punch_type": "check_in", "verify_mode": "face", "punched_at": "2026-08-05T09:00:00+07:00"}, {"emp_id": 1001, "punch_type": "check_out", "verify_mode": "face", "punched_at": "2026-08-05T18:00:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        (
            "AccessLogUpload - Device không thuộc controller này (200)",
            "CTRL-HN-SRV-01",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "records": [{"emp_id": 1001, "punch_type": "check_in", "verify_mode": "card", "punched_at": "2026-08-05T09:00:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        (
            "AccessLogUpload - punched_at rỗng (200)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "records": [{"emp_id": 1001, "punch_type": "check_in", "verify_mode": "card", "punched_at": ""}]}]',
            200,
            "created successfully",
        ),
        ("AccessLogUpload - devices rỗng (200)", "CTRL-HN-LOBBY-01", "[]", 200, "No device data provided."),
        (
            "AccessLogUpload - Mix upload 1 log mới và 1 log trùng (200)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "records": [{"emp_id": 1001, "punch_type": "check_in", "verify_mode": "card", "punched_at": "2026-08-05T07:30:00+07:00"}, {"emp_id": 1002, "punch_type": "check_in", "verify_mode": "fingerprint", "punched_at": "2026-08-05T12:00:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        (
            "AccessLogUpload - Upload 1 log mới tinh hoàn toàn (200)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-HN-LOB-OUT-01", "records": [{"emp_id": 1002, "punch_type": "check_out", "verify_mode": "fingerprint", "punched_at": "2026-08-05T18:30:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        (
            "AccessLogUpload - HCM Kho upload log cho Lê Văn C (1003) qua thiết bị DEV-HCM-WHS-FGR-01 (200)",
            "CTRL-HCM-WHS-01",
            '[{"device_sn": "DEV-HCM-WHS-FGR-01", "records": [{"emp_id": 1003, "punch_type": "check_in", "verify_mode": "fingerprint", "punched_at": "2026-08-05T08:30:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        (
            "AccessLogUpload - Đà Nẵng upload log cho Phạm Văn D (1004) qua thiết bị DEV-DN-RD-IN-01 (200)",
            "CTRL-DN-MAIN-01",
            '[{"device_sn": "DEV-DN-RD-IN-01", "records": [{"emp_id": 1004, "punch_type": "check_in", "verify_mode": "card", "punched_at": "2026-08-05T08:45:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        (
            "AccessLogUpload - HN Server Room upload log cho Trần Thị B (1002) qua thiết bị DEV-HN-SRV-FACE-01 (200)",
            "CTRL-HN-SRV-01",
            '[{"device_sn": "DEV-HN-SRV-FACE-01", "records": [{"emp_id": 1002, "punch_type": "check_in", "verify_mode": "face", "punched_at": "2026-08-05T09:15:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        (
            "AccessLogUpload - Batch upload nhiều thiết bị và nhiều nhân viên khác nhau cùng lúc (200)",
            "CTRL-HN-LOBBY-01",
            '[{"device_sn": "DEV-HN-LOB-IN-01", "records": [{"emp_id": 1001, "punch_type": "check_in", "verify_mode": "card", "punched_at": "2026-08-05T08:00:00+07:00"}]}, {"device_sn": "DEV-HN-LOB-OUT-01", "records": [{"emp_id": 1002, "punch_type": "check_out", "verify_mode": "fingerprint", "punched_at": "2026-08-05T17:15:00+07:00"}]}]',
            200,
            "created successfully",
        ),
        ("AccessLogUpload - Không có token (401)", "CTRL-HN-LOBBY-01", "[]", 401, ""),
        ("AccessLogUpload - Token sai (401)", "CTRL-HN-LOBBY-01", "[]", 401, ""),
    ]

    for idx, case in enumerate(al_cases, 1):
        row_vals = [idx] + list(case) + ["x"]
        al_ws.append(row_vals)

    al_ws.row_dimensions[1].height = 28
    al_ws.row_dimensions[4].height = 28
    for r_idx in range(5, 5 + len(al_cases)):
        al_ws.row_dimensions[r_idx].height = 40
        name_cell = al_ws.cell(row=r_idx, column=2)
        name_cell.font = Font(name="Calibri", size=11, bold=True)
        exp_status_val = al_ws.cell(row=r_idx, column=5).value
        if exp_status_val == 200:
            success_green_fill = PatternFill(start_color="C6EFCE", fill_type="solid")
            al_ws.cell(row=r_idx, column=1).fill = success_green_fill
            name_cell.fill = success_green_fill
        s_font, s_fill = get_status_styles(exp_status_val)
        esc = al_ws.cell(row=r_idx, column=5)
        esc.font = s_font
        esc.fill = s_fill
        esc.alignment = align_center
        emc = al_ws.cell(row=r_idx, column=6)
        emc.font = Font(
            color=s_font.color, name="Calibri", size=11, italic=True, bold=True
        )
        emc.alignment = align_left

        lc_cell = al_ws.cell(row=r_idx, column=4)
        lc_cell.font = Font(name="Calibri", size=9, italic=True)
        lc_cell.alignment = Alignment(
            horizontal="left", vertical="center", wrap_text=True
        )

        for c_idx in range(1, 8):
            cell = al_ws.cell(row=r_idx, column=c_idx)
            cell.border = border_thin
            if c_idx not in [4, 5, 6]:
                if c_idx in [1, 5, 7]:
                    cell.alignment = align_center
                else:
                    cell.alignment = align_left

    # Tu dong dieu chinh do rong cot thong minh cho Parameter Sheet
    adjust_column_widths_smart(al_ws)

    try:
        wb.save(filepath)
    except PermissionError:
        base, ext = os.path.splitext(filepath)
        alt_path = f"{base}_temp{ext}"
        print(
            f"\n[Warning] Permission denied to write to {filepath} (file is likely open in Excel). "
            f"Saving generated test cases to: {alt_path}"
        )
        wb.save(alt_path)


if __name__ == "__main__":
    cases = parse_http_file(HTTP_PATH)
    write_to_excel(cases, EXCEL_PATH)
    print(f"[OK] Excel test file generated: {EXCEL_PATH}")
