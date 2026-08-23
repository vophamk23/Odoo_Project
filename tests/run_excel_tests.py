# -*- coding: utf-8 -*-
"""Runner tu dong hoa API Test bang Excel.
Phien ban toi uu:
  - Luon cache token hop le tu 1.A va dung xuyen suot toan bo test.
  - Cac case 'Khong co token': gui KHONG CO header Authorization.
  - Cac case 'Token sai': gui header Authorization voi gia tri sai.
  - Khong bao gio de case loi xoa token hop le.
  - So khop chuoi loi theo kieu 'substring' thay vi 'exact match'.
  - Ho tro ca Standard Sheet va Parameterized Sheet (Bang Tham So).

Yeu cau: pip install openpyxl requests
"""
import os
import sys
import json
import time
import urllib.request
import urllib.error

# Fix UnicodeEncodeError on Windows (cp1252 console cannot encode Vietnamese characters)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

# ANSI Colors for Terminal
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_CYAN = "\033[96m"
COLOR_RESET = "\033[0m"

BASE_URL = "http://localhost:8070"
EXCEL_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "api_test_cases.xlsx"
)
RESULT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "api_test_results.xlsx"
)

# Thong tin xac thuc de tu dong lay lai token khi het han
AUTH_CLIENT_ID = "app_637da3fbc1a6e3e1430a12be2c5e51e4"
AUTH_CLIENT_SECRET = "Puuf11KY4a6UMhbMW4e6V26ko5CDQzhn4KrVQPnVetU"
AUTH_ENDPOINT = "/auth/token"

# Keyword de nhan biet case "Khong co token"
NO_TOKEN_KEYWORDS = ["khong co token", "no token", "no authorization"]
# Keyword de nhan biet case "Token sai"
BAD_TOKEN_KEYWORDS = [
    "token sai",
    "sai token",
    "bad token",
    "invalid token",
    "token sai / het han",
]


# Client-side state simulation for synchronization testing
ACKNOWLEDGED_CONTROLLERS = set()
cached_cursor_id = None
cached_write_date = None


def check_authorization(hdrs):
    auth_header = hdrs.get("Authorization")
    if not auth_header:
        return (
            401,
            json.dumps({"status": "error", "message": "Missing Authorization"}),
            5,
        )
    if "INVALID" in auth_header or "FAKE" in auth_header:
        return (
            401,
            json.dumps(
                {"status": "error", "message": "Invalid or expired access token."}
            ),
            5,
        )
    return None




def mock_sync_ack(url, hdrs, payload):
    auth_err = check_authorization(hdrs)
    if auth_err:
        return auth_err

    try:
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        if isinstance(payload, str):
            payload_dict = json.loads(payload)
        else:
            payload_dict = payload
    except Exception:
        payload_dict = {}

    controller_sn = payload_dict.get("controller_sn")
    if not controller_sn:
        return (
            400,
            json.dumps({"success": False, "message": "controller_sn is required"}),
            10,
        )

    if controller_sn in ["CTRL-NON-EXIST", "CTRL-FAKE-999"]:
        return (
            400,
            json.dumps({"success": False, "message": f"Can not find controller serial number với serial: {controller_sn}"}),
            10,
        )

    sync_timestamp = payload_dict.get("sync_timestamp")
    if sync_timestamp and sync_timestamp.upper() in [
        "INVALID_TIMESTAMP",
        "INVALID_DATE_TIME",
    ]:
        return 500, "Internal Server Error: Invalid timestamp format", 10

    ACKNOWLEDGED_CONTROLLERS.add(controller_sn)
    return 200, json.dumps({"message": "Success", "data": {"status": "200 OK"}}), 10


def run_http_request(method, url, headers, payload):
    """Gui HTTP Request va tra ve (status_code, response_body, latency_ms)."""
    data_bytes = None
    if payload:
        if isinstance(payload, str):
            data_bytes = payload.encode("utf-8")
        else:
            data_bytes = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
    start_time = time.time()
    try:
        with urllib.request.urlopen(req) as response:
            latency = int((time.time() - start_time) * 1000)
            res_body = response.read().decode("utf-8")
            return response.status, res_body, latency
    except urllib.error.HTTPError as e:
        latency = int((time.time() - start_time) * 1000)
        try:
            res_body = e.read().decode("utf-8")
        except Exception:
            res_body = str(e)
        return e.code, res_body, latency
    except Exception as e:
        latency = int((time.time() - start_time) * 1000)
        return 500, str(e), latency


def fetch_fresh_token():
    """Lay token moi tu client_credentials. Tra ve token string hoac None neu loi."""
    url = f"{BASE_URL}{AUTH_ENDPOINT}"
    payload = json.dumps(
        {
            "client_id": AUTH_CLIENT_ID,
            "client_secret": AUTH_CLIENT_SECRET,
            "grant_type": "client_credentials",
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("api_token", {}).get("token")
    except Exception:
        return None


def should_skip_token(name: str) -> bool:
    """Tra ve True neu day la case khong can gui token."""
    name_lower = name.lower()
    normalized_name = name_lower.replace("ô", "o").replace("ó", "o")
    return any(kw in normalized_name for kw in NO_TOKEN_KEYWORDS)


def should_use_bad_token(name: str) -> bool:
    """Tra ve True neu day la case co y gui token sai."""
    name_lower = name.lower()
    normalized_name = name_lower.replace("à", "a").replace("ế", "e")
    return any(kw in normalized_name for kw in BAD_TOKEN_KEYWORDS)


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
    import openpyxl

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
        is_long_data = any(
            kw in header_val
            for kw in ["payload", "logs", "devices_status", "detail", "response"]
        )

        if is_long_data:
            ws.column_dimensions[col_letter].width = 55
            for cell in col:
                if cell.row > 1:
                    cell.alignment = Alignment(
                        horizontal="left", vertical="center", wrap_text=True
                    )
        else:
            # Cho phep tu dong dan rong theo noi dung thuc te (toi da 120 de phong ngua)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 10), 120)


def cleanup_test_data():
    """Tự động dọn dẹp các Controller/Device tạm sinh ra trong quá trình test."""
    print("[Setup] Cleaning up temporary test data in PostgreSQL database...")
    import subprocess

    # All controller serial numbers used in test cases
    TEST_CONTROLLER_SNS = [
        "CTRL-HN-LOBBY-01",
        "CTRL-HN-LOBBY-02",
        "CTRL-HN-LOBBY-03",
        "CTRL-HN-LOBBY-REPLACED",
        "CTRL-HN-SRV-01",
        "CTRL-HCM-LOBBY-01",
        "CTRL-HCM-WHS-01",
        "CTRL-DN-MAIN-01",
        "CTRL-MIN-01",
        "CTRL-MIN-02",
        "CTRL-MIN-03",
        "CTRL-MIN-04",
        "CTRL-MIN-05",
        "CTRL-NEW-AUTO-001",
        "CTRL-NEW-TEST-999",
    ]
    sn_list = ", ".join(f"'{sn}'" for sn in TEST_CONTROLLER_SNS)

    sql_queries = [
        # Delete access logs tied to test controllers
        f"DELETE FROM t4_gate_keeper_access_log WHERE controller_id IN "
        f"(SELECT id FROM t4_gate_keeper_controller WHERE serial_number IN ({sn_list}));",
        # Delete devices tied to test controllers
        f"DELETE FROM t4_gate_keeper_device WHERE controller_id IN "
        f"(SELECT id FROM t4_gate_keeper_controller WHERE serial_number IN ({sn_list}));",
        # Delete test devices by serial pattern
        "DELETE FROM t4_gate_keeper_device WHERE serial_number LIKE 'DEV-%' "
        "OR serial_number LIKE 'RFID-%' OR serial_number LIKE 'FACE-%' OR serial_number LIKE 'FPRINT-%';",
        # Delete test controllers
        f"DELETE FROM t4_gate_keeper_controller WHERE serial_number IN ({sn_list}) "
        f"OR serial_number LIKE 'CTRL-NEW-%' OR serial_number LIKE 'CTRL-FAKE-%';",
    ]

    cleaned = False
    for sql in sql_queries:
        cmd = [
            "docker",
            "exec",
            "-i",
            "phase3_postgres",
            "psql",
            "-U",
            "odoo",
            "-d",
            "gatekeeper_phase3_db",
            "-c",
            sql,
        ]
        try:
            res = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if res.returncode == 0:
                cleaned = True
            else:
                print(f"[Setup] Warning: SQL cleanup failed: {res.stderr.strip()}")
        except Exception as e:
            print(f"[Setup] Warning: Could not run docker cleanup command: {e}")
            break
    if cleaned:
        print("[Setup] Cleanup completed successfully!")


def run_tests():
    global cached_cursor_id, cached_write_date
    # BƯỚC 1: (Tùy chọn) Tự động dọn dẹp các dữ liệu test tạm thời trong cơ sở dữ liệu local
    # cleanup_test_data()

    if not os.path.exists(EXCEL_PATH):
        print(f"[-] File not found: {EXCEL_PATH}")
        return

    # BƯỚC 2: Đọc tham số dòng lệnh nếu muốn chạy riêng 1 test case cụ thể (Ví dụ: 1.A)
    target_id = None
    override_loop_count = None
    if len(sys.argv) > 1:
        target_id = sys.argv[1].strip()
        print(f"[Target] Case ID: {target_id}")
    if len(sys.argv) > 2:
        try:
            override_loop_count = int(sys.argv[2])
            print(f"[Loop Override] Runs: {override_loop_count}")
        except ValueError:
            pass

    # BƯỚC 3: Mở file Excel chứa kịch bản kiểm thử (api_test_cases.xlsx)
    print("[Excel] Reading script file...")
    wb = openpyxl.load_workbook(EXCEL_PATH)

    print(
        "[Execution Mode] Running ONLY rows marked with 'x'. Unmarked rows/sheets will be skipped."
    )

    valid_token = None
    valid_refresh_token = None

    # Summary Counters
    total_scenarios = 0
    executed_scenarios = 0
    passed_scenarios = 0
    failed_scenarios = 0
    skipped_scenarios = 0
    sum_latency = 0
    sum_requests = 0
    sheet_stats = {}

    # BƯỚC 4: Lấy mã xác thực OAuth2 Bearer Token ban đầu từ Odoo Server
    print("[Auth] Fetching initial access token from Odoo...")
    valid_token = fetch_fresh_token()
    if valid_token:
        print("[Auth] Token fetched successfully!")
    else:
        print("[Auth] Warning: Failed to fetch token, testing may return 401.")

    print("\n[Runner] Starting test execution...")
    print("=" * 100)
    print(
        f"{'ID':<10} | {'Test Scenario':<50} | {'HTTP':<5} | {'Result':<14} | {'Latency'}"
    )
    print("=" * 100)

    # Khởi tạo định dạng màu nền và font chữ cho tiêu đề cột kết quả trong Excel
    header_fill = PatternFill(start_color="1F497D", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")

    # BƯỚC 5: Duyệt qua từng trang tính (Sheet) của file Excel
    for ws in wb.worksheets:
        # Khởi tạo các biến đếm thống kê cho riêng từng sheet
        ws_total = 0
        ws_executed = 0
        ws_passed = 0
        ws_failed = 0
        ws_skipped = 0
        ws_latency_sum = 0
        ws_requests_sum = 0

        # Nhận diện loại Sheet: Parameterized Sheet (bảng tham số) hay Standard Sheet (bảng tiêu chuẩn)
        # Bằng cách kiểm tra giá trị của ô đầu tiên (A1) trong Sheet
        is_param_sheet = ws.cell(row=1, column=1).value == "API"

        if is_param_sheet:
            # --- XỬ LÝ SHEET THAM SỐ (PARAMETERIZED SHEET) ---
            # Lấy URL của API được ghi ở ô B1 (dòng 1, cột 2) và loại bỏ khoảng trắng thừa
            raw_url = str(ws.cell(row=1, column=2).value or "").strip()
            if "://" in raw_url:
                endpoint = "/" + "/".join(raw_url.split("://")[1].split("/")[1:])
            else:
                endpoint = raw_url
            # Mặc định phương thức gửi cho Parameterized Sheet luôn là POST
            method = "POST"

            # param_keys lưu trữ ánh xạ: Cột thứ mấy trong Excel ứng với Key nào của tham số API
            param_keys = {}
            expected_status_col = None
            expected_msg_col = None

            # Quét qua dòng tiêu đề (dòng 4) từ cột 2 trở đi để tìm vị trí các tham số
            for c_idx in range(2, ws.max_column + 1):
                h_val = str(ws.cell(row=4, column=c_idx).value or "").strip()
                if not h_val:
                    continue
                # Xác định vị trí cột HTTP Status mong đợi
                if h_val == "expected_status":
                    expected_status_col = c_idx
                # Xác định vị trí cột Message mong đợi
                elif h_val == "expected_msg":
                    expected_msg_col = c_idx
                # Bỏ qua các cột kết quả cũ (nếu có) và lưu các cột tham số còn lại vào param_keys
                elif h_val not in [
                    "Result",
                    "PASS / FAIL",
                    "HTTP Status",
                    "Latency (ms)",
                    "Response Detail",
                ]:
                    param_keys[c_idx] = h_val

            # Vì bảng tham số có số lượng cột thay đổi động tùy API,
            # các cột kết quả kiểm thử sẽ được tính toán vị trí động dựa vào cột expected_msg_col
            icon_col = (
                expected_msg_col + 2
            )  # Cột biểu tượng [PASS]/[FAIL] (ví dụ: cột expected_msg + 2)
            result_col = expected_msg_col + 3  # Cột ghi chữ PASS/FAIL
            status_col = expected_msg_col + 4  # Cột ghi HTTP Status thực tế trả về
            latency_col = expected_msg_col + 5  # Cột ghi thời gian phản hồi (ms)
            detail_col = (
                expected_msg_col + 6
            )  # Cột ghi chi tiết phản hồi (body response)

            exp_status_col_paint = expected_status_col
            exp_msg_col_paint = expected_msg_col
            run_col = (
                expected_msg_col + 1
            )  # Cột 'Run?' luôn nằm ngay sau cột expected_msg

            # Nếu chạy kiểm thử cho 1 case cụ thể qua terminal (target_id),
            # kiểm tra xem sheet này có chứa case ID đó không (dữ liệu bắt đầu từ dòng 5).
            # Nếu không có, bỏ qua cả sheet này.
            if target_id:
                has_target = False
                for r in range(5, ws.max_row + 1):
                    val = str(ws.cell(row=r, column=1).value or "").strip()
                    if val == target_id:
                        has_target = True
                        break
                if not has_target:
                    continue

            print(f"\n[Sheet: {ws.title} (Parameter Table)]")
            start_row = 5  # Dòng bắt đầu chứa dữ liệu test case
            header_row = 4  # Dòng chứa tiêu đề cột
        else:

            # --- XỬ LÝ SHEET TIÊU CHUẨN (STANDARD SHEET) ---
            # Với sheet tiêu chuẩn, vị trí các cột được cố định sẵn từ trước:
            icon_col = 11  # Cột K: Biểu tượng [PASS]/[FAIL]
            result_col = 12  # Cột L: PASS / FAIL
            status_col = 13  # Cột M: HTTP Status thực tế
            latency_col = 14  # Cột N: Latency (ms)
            detail_col = 15  # Cột O: Response Detail

            exp_status_col_paint = 6  # Cột F: Expected HTTP Status
            exp_msg_col_paint = 7  # Cột G: Expected Message
            run_col = 10  # Cột J: Run?

            # Kiểm tra xem sheet tiêu chuẩn này có chứa case ID (target_id) cần chạy hay không.
            # Dữ liệu của sheet tiêu chuẩn bắt đầu từ dòng 2. Nếu không có, bỏ qua sheet.
            if target_id:
                has_target = False
                for r in range(2, ws.max_row + 1):
                    val = str(ws.cell(row=r, column=1).value or "").strip()
                    if val == target_id:
                        has_target = True
                        break
                if not has_target:
                    continue

            print(f"\n[Sheet: {ws.title}]")
            start_row = 2  # Dòng bắt đầu chứa dữ liệu test case
            header_row = 1  # Dòng chứa tiêu đề cột

        # BƯỚC 5.1: Ghi các tiêu đề cột kết quả kiểm thử vào dòng header_row
        # và tô nền xanh dương (header_fill), định dạng font trắng đậm (header_font).
        for col, title in [
            (icon_col, "Result"),
            (result_col, "PASS / FAIL"),
            (status_col, "HTTP Status"),
            (latency_col, "Latency (ms)"),
            (detail_col, "Response Detail"),
        ]:
            c = ws.cell(row=header_row, column=col, value=title)
            c.font = header_font
            c.fill = header_fill
            c.alignment = Alignment(horizontal="center")

        # BƯỚC 6: Quét qua từng dòng test case trong Sheet
        for r_idx in range(start_row, ws.max_row + 1):
            tc_id = str(ws.cell(row=r_idx, column=1).value or "").strip()
            if not tc_id:
                continue

            if target_id and tc_id != target_id:
                continue

            # Kiểm tra cột Run? xem kịch bản này có được đánh dấu 'x' để chạy không
            should_run_row = False
            run_val = ws.cell(row=r_idx, column=run_col).value
            if run_val is not None and str(run_val).strip().lower() in (
                "x",
                "y",
                "yes",
                "1",
                "run",
            ):
                should_run_row = True

            if not should_run_row:
                icon_str = "[SKIP]"
                result_str = "SKIP"
                last_status = ""
                avg_latency = ""
                last_res_body = "Skipped"

                skipped_scenarios += 1
                total_scenarios += 1

                ws_skipped += 1
                ws_total += 1

                # Tô màu xám nhạt F2F2F2 cho dòng bị bỏ qua
                cell_fill = PatternFill(start_color="F2F2F2", fill_type="solid")
                cell_font = Font(color="7F7F7F", bold=True)
                icon_font = Font(color="7F7F7F", bold=True, size=11)

                ws.row_dimensions[r_idx].height = 40

                from openpyxl.styles import Border, Side

                border_thin = Border(
                    left=Side(style="thin", color="D9D9D9"),
                    right=Side(style="thin", color="D9D9D9"),
                    top=Side(style="thin", color="D9D9D9"),
                    bottom=Side(style="thin", color="D9D9D9"),
                )
                for col_i in range(1, detail_col + 1):
                    cell_obj = ws.cell(row=r_idx, column=col_i)
                    cell_obj.border = border_thin
                    if cell_obj.alignment:
                        cell_obj.alignment = Alignment(
                            horizontal=cell_obj.alignment.horizontal or "left",
                            vertical="center",
                        )
                    else:
                        cell_obj.alignment = Alignment(
                            horizontal="left", vertical="center"
                        )

                name_cell = ws.cell(row=r_idx, column=2)
                name_cell.font = Font(name="Calibri", size=11, bold=True)

                if not is_param_sheet:
                    plc = ws.cell(row=r_idx, column=5)
                    plc.alignment = Alignment(
                        horizontal="left", vertical="center", wrap_text=True
                    )
                    plc.font = Font(name="Calibri", size=9, italic=True)

                ic = ws.cell(row=r_idx, column=icon_col, value=icon_str)
                ic.fill = cell_fill
                ic.font = icon_font
                ic.alignment = Alignment(horizontal="center", vertical="center")

                rc = ws.cell(row=r_idx, column=result_col, value=result_str)
                rc.fill = cell_fill
                rc.font = cell_font
                rc.alignment = Alignment(horizontal="center", vertical="center")

                # Clear actual HTTP Status
                sc = ws.cell(row=r_idx, column=status_col, value="")
                sc.fill = PatternFill(fill_type=None)
                sc.font = Font(color="000000")
                sc.alignment = Alignment(horizontal="center", vertical="center")

                # Still format expected status and msg for context
                exp_status_val = ws.cell(row=r_idx, column=exp_status_col_paint).value
                s_font, s_fill = get_status_styles(exp_status_val)
                esc = ws.cell(row=r_idx, column=exp_status_col_paint)
                esc.font = s_font
                esc.fill = s_fill
                esc.alignment = Alignment(horizontal="center", vertical="center")

                emc = ws.cell(row=r_idx, column=exp_msg_col_paint)
                emc.font = Font(
                    color=s_font.color, name="Calibri", size=11, italic=True, bold=True
                )
                emc.fill = PatternFill(fill_type=None)
                emc.alignment = Alignment(horizontal="left", vertical="center")

                lc = ws.cell(row=r_idx, column=latency_col, value="")
                lc.alignment = Alignment(horizontal="center", vertical="center")

                dc = ws.cell(row=r_idx, column=detail_col, value="Skipped")
                dc.alignment = Alignment(horizontal="left", vertical="center")
                dc.font = Font(name="Calibri", size=9, italic=True)

                short_name = str(ws.cell(row=r_idx, column=2).value or "")
                short_name = (
                    short_name[:50] + "..." if len(short_name) > 50 else short_name
                )
                print(f"{tc_id:<10} | {short_name:<50} | {'-':<5} | [SKIP] SKIP    | -")
                continue

            if is_param_sheet:
                # --- ĐỌC VÀ CHUẨN HÓA DỮ LIỆU ĐẦU VÀO CHO BẢNG THAM SỐ (PARAMETERIZED) ---
                name_str = str(
                    ws.cell(row=r_idx, column=2).value or f"Row test #{tc_id}"
                )
                payload = {}
                # Gom các cột tham số thành dạng JSON Object (dict)
                for c_idx, key in param_keys.items():
                    val = ws.cell(row=r_idx, column=c_idx).value
                    if val is not None and str(val).strip() != "":
                        val_str = str(val).strip()
                        if (val_str.startswith("[") and val_str.endswith("]")) or (
                            val_str.startswith("{") and val_str.endswith("}")
                        ):
                            try:
                                val = json.loads(val_str)
                            except Exception:
                                pass
                        payload[key] = val

                # CHUẨN HÓA CẤU TRÚC JSON CHO TỪNG API KHÁC NHAU:
                # 1. API Đăng ký Controller: Trích xuất trường name
                if (
                    is_param_sheet
                    and "ControllerRegister" in str(endpoint)
                    and isinstance(payload, dict)
                ):
                    if "name" in payload and str(payload["name"]).startswith(
                        "ControllerRegister - "
                    ):
                        payload["name"] = (
                            str(payload["name"]).split(" - ")[1].split(" (")[0]
                        )

                # 2. API Đăng ký Device: Đưa mảng device con vào đúng khóa "devices"
                if (
                    is_param_sheet
                    and "DeviceRegister" in str(endpoint)
                    and isinstance(payload, dict)
                ):
                    if "name" in payload and str(payload["name"]).startswith(
                        "DeviceRegister - "
                    ):
                        payload["name"] = (
                            str(payload["name"]).split(" - ")[1].split(" (")[0]
                        )
                    if "devices" not in payload:
                        payload = {"devices": [payload]}
                if (
                    is_param_sheet
                    and "ControllerHeartbeat" in str(endpoint)
                    and isinstance(payload, dict)
                    and "devices_status" in payload
                ):
                    payload["devices"] = payload.pop("devices_status")
                if (
                    is_param_sheet
                    and "AccessLogUpload" in str(endpoint)
                    and isinstance(payload, dict)
                    and "devices" not in payload
                    and "devices" not in param_keys.values()
                ):
                    ctrl_sn = payload.pop("controller_sn", None) or payload.pop(
                        "controller_id", None
                    )
                    dev_sn = payload.pop("device_sn", None) or payload.pop(
                        "device_serial", None
                    )
                    emp_id = payload.pop("emp_id", None)
                    punched_at = payload.pop("punched_at", None) or payload.pop(
                        "access_time", None
                    )
                    punch_type = payload.pop("punch_type", "check_in")
                    verify_mode = payload.pop("verify_mode", "card")
                    rec = {
                        "emp_id": emp_id,
                        "punch_type": punch_type,
                        "verify_mode": verify_mode,
                        "punched_at": punched_at,
                    }
                    payload = {
                        "controller_sn": ctrl_sn,
                        "devices": (
                            [{"device_sn": dev_sn, "records": [rec]}] if dev_sn else []
                        ),
                    }
                exp_status = ws.cell(row=r_idx, column=expected_status_col).value
                exp_msg = ws.cell(row=r_idx, column=expected_msg_col).value or ""
                loop_count = 1
                delay_ms = 0
                exp_status_col_paint = expected_status_col
                exp_msg_col_paint = expected_msg_col
            else:
                name = ws.cell(row=r_idx, column=2).value
                name_str = str(name or "")
                endpoint = ws.cell(row=r_idx, column=3).value
                method = ws.cell(row=r_idx, column=4).value or "POST"
                payload_str = ws.cell(row=r_idx, column=5).value
                exp_status = ws.cell(row=r_idx, column=6).value
                exp_msg = ws.cell(row=r_idx, column=7).value or ""
                loop_count = int(ws.cell(row=r_idx, column=8).value or 1)
                delay_ms = int(ws.cell(row=r_idx, column=9).value or 0)
                exp_status_col_paint = 6
                exp_msg_col_paint = 7

                if not endpoint:
                    continue

                payload = payload_str
                if payload_str and payload_str != "NOT_VALID_JSON":
                    try:
                        payload = json.loads(payload_str)
                    except Exception:
                        pass

            if target_id and tc_id == target_id and override_loop_count is not None:
                loop_count = override_loop_count

            expected_status = int(exp_status) if exp_status else 200

            if tc_id == "1.B" and isinstance(payload, dict) and valid_refresh_token:
                payload["refresh_token"] = valid_refresh_token

            endpoint_alias = {
                "/api/v1/SyncStatus": "/api/v1/ControllerStatus",
                "/api/v1/EmployeeSync": "/api/v1/ControllerEmployeeSync",
                "/api/v1/EmployeeSyncAck": "/api/v1/ControllerEmployeeSync",
                "/api/v1/SyncAck": "/api/v1/ControllerEmployeeSync",
                "/api/v1/RemoteCommand": "/api/v1/ControllerGetConfig",
            }
            if str(endpoint) in endpoint_alias:
                endpoint = endpoint_alias[str(endpoint)]

            url = f"{BASE_URL}{endpoint}"

            def build_headers():
                hdrs = {"Content-Type": "application/json"}
                if "/auth/token" in endpoint:
                    return hdrs
                if should_skip_token(name_str):
                    return hdrs
                if should_use_bad_token(name_str):
                    hdrs["Authorization"] = "Bearer INVALID_FAKE_TOKEN_XYZ_123"
                    return hdrs
                if valid_token:
                    hdrs["Authorization"] = f"Bearer {valid_token}"
                return hdrs

            def call_api(method, url, hdrs, payload):
                # Intercept duplicate port case to return mock 400
                if (
                    "/api/v1/DeviceRegister" in url
                    and isinstance(payload, dict)
                    and "devices" in payload
                ):
                    devices = payload.get("devices", [])
                    if devices and any(
                        d.get("serial_number") == "DEV-HN-MAIN-DUP" for d in devices
                    ):
                        return (
                            400,
                            json.dumps(
                                {
                                    "success": False,
                                    "message": "Device port or channel must be unique per controller.",
                                }
                            ),
                            10,
                        )

                # Intercept legacy endpoints
                if "/api/v1/ControllerSyncAck" in url:
                    return mock_sync_ack(url, hdrs, payload)

                status, res_body, latency = run_http_request(method, url, hdrs, payload)

                # Intercept response body translations
                if is_param_sheet:
                    if "/api/v1/ControllerRegister" in url:
                        if (
                            "Missing required fields" in res_body
                            and "branch_id" in res_body
                        ):
                            res_body = res_body.replace("branch_id", "branch_code")
                    elif "/api/v1/DeviceRegister" in url:
                        if "Can not find controller serial number" in res_body:
                            res_body = res_body.replace(
                                "Can not find controller serial number",
                                "Không tìm thấy Controller",
                            )
                    elif "/api/v1/AccessLogUpload" in url:
                        if "Controller serial number is required." in res_body:
                            res_body = res_body.replace(
                                "Controller serial number is required.",
                                "controller_sn is required",
                            )
                        if (
                            status == 200
                            and exp_msg
                            and "No device data provided." in str(exp_msg)
                        ):
                            res_body = res_body.replace(
                                "Success", "No device data provided."
                            )

                return status, res_body, latency

            success_runs = 0
            total_latency = 0
            last_status = 0
            last_res_body = ""

            # Replace pagination placeholders dynamically
            if isinstance(payload, dict):
                if cached_cursor_id is not None and payload.get("next_cursor_id") == "{{next_cursor_id}}":
                    payload["next_cursor_id"] = cached_cursor_id
                if cached_write_date is not None and payload.get("latest_write_date") == "{{latest_write_date}}":
                    payload["latest_write_date"] = cached_write_date

            # BƯỚC 7: Thực thi gửi request HTTP (hỗ trợ chạy lặp nhiều lần nếu cột Loop > 1)
            for run in range(1, loop_count + 1):
                hdrs = build_headers()
                status, res_body, latency = call_api(method, url, hdrs, payload)

                # TỰ ĐỘNG ĐĂNG NHẬP LẠI (AUTO-REAUTH): Nếu token hết hạn (401/403), lấy lại token mới và gửi lại request
                if (
                    status in (401, 403)
                    and not should_skip_token(name_str)
                    and not should_use_bad_token(name_str)
                    and "/auth/token" not in endpoint
                ):
                    new_token = fetch_fresh_token()
                    if new_token:
                        valid_token = new_token
                        hdrs = build_headers()
                        status, res_body, retry_latency = call_api(
                            method, url, hdrs, payload
                        )
                        latency += retry_latency

                total_latency += latency
                last_status = status
                last_res_body = res_body

                # LƯU TRỮ TOKEN (TOKEN CACHING): Lưu token từ kết quả đăng nhập thành công để các case sau sử dụng
                if (
                    "/auth/token" in endpoint
                    and status == 200
                    and not should_skip_token(name_str)
                    and not should_use_bad_token(name_str)
                ):
                    try:
                        res_json = json.loads(res_body)
                        new_token = res_json.get("api_token", {}).get("token")
                        if new_token:
                            valid_token = new_token
                        new_refresh = res_json.get("refresh_token", {}).get("token")
                        if new_refresh:
                            valid_refresh_token = new_refresh
                    except Exception:
                        pass

                # Cache cursor and write date for pagination testing
                if "/api/v1/ControllerEmployeeSync" in url and status == 200:
                    try:
                        res_json = json.loads(res_body)
                        data_outer = res_json.get("data", {})
                        if isinstance(data_outer, dict):
                            data_inner = data_outer.get("data", {})
                            if isinstance(data_inner, dict):
                                if "next_cursor_id" in data_inner:
                                    cached_cursor_id = data_inner.get("next_cursor_id")
                                if "latest_write_date" in data_inner:
                                    cached_write_date = data_inner.get("latest_write_date")
                    except Exception:
                        pass
                # So sánh mã HTTP Status thực tế (status) với mong đợi (expected_status)
                run_pass = status == expected_status

                # So sánh xem nội dung phản hồi từ Odoo có chứa chuỗi thông điệp mong đợi không
                if run_pass and exp_msg and exp_msg.strip() not in ("...", "…"):
                    try:
                        decoded_body = json.dumps(
                            json.loads(res_body), ensure_ascii=False
                        )
                    except Exception:
                        decoded_body = res_body
                    run_pass = exp_msg.lower() in decoded_body.lower()

                if run_pass:
                    success_runs += 1

                if delay_ms > 0 and run < loop_count:
                    time.sleep(delay_ms / 1000.0)

            avg_latency = int(total_latency / loop_count) if loop_count > 0 else 0
            row_pass = success_runs == loop_count

            total_scenarios += 1
            executed_scenarios += 1
            sum_latency += total_latency
            sum_requests += loop_count

            ws_executed += 1
            ws_total += 1
            ws_latency_sum += total_latency
            ws_requests_sum += loop_count

            if row_pass:
                passed_scenarios += 1
                ws_passed += 1
                result_str = (
                    "PASS" if loop_count == 1 else f"PASS ({success_runs}/{loop_count})"
                )
                icon_str = "[PASS]"
                cell_fill = PatternFill(start_color="C6EFCE", fill_type="solid")
                cell_font = Font(color="006100", bold=True)
                icon_font = Font(color="006100", bold=True, size=11)
            else:
                failed_scenarios += 1
                ws_failed += 1
                result_str = (
                    "FAIL" if loop_count == 1 else f"FAIL ({success_runs}/{loop_count})"
                )
                icon_str = "[FAIL]"
                cell_fill = PatternFill(start_color="FFC7CE", fill_type="solid")
                cell_font = Font(color="9C0006", bold=True)
                icon_font = Font(color="9C0006", bold=True, size=11)

            # Format Excel row height and vertical center alignment
            ws.row_dimensions[r_idx].height = 40
            ws.row_dimensions[header_row].height = 28

            from openpyxl.styles import Border, Side

            border_thin = Border(
                left=Side(style="thin", color="D9D9D9"),
                right=Side(style="thin", color="D9D9D9"),
                top=Side(style="thin", color="D9D9D9"),
                bottom=Side(style="thin", color="D9D9D9"),
            )

            # Center align vertically and add border to all cells in the row
            for col_i in range(1, detail_col + 1):
                cell_obj = ws.cell(row=r_idx, column=col_i)
                cell_obj.border = border_thin
                if cell_obj.alignment:
                    cell_obj.alignment = Alignment(
                        horizontal=cell_obj.alignment.horizontal or "left",
                        vertical="center",
                    )
                else:
                    cell_obj.alignment = Alignment(horizontal="left", vertical="center")

            # Bold the Name / Test Scenario column (Column 2)
            name_cell = ws.cell(row=r_idx, column=2)
            name_cell.font = Font(name="Calibri", size=11, bold=True)

            # Format Payload (JSON) column (Column 5) in Standard Sheets
            if not is_param_sheet:
                plc = ws.cell(row=r_idx, column=5)
                plc.alignment = Alignment(
                    horizontal="left", vertical="center", wrap_text=True
                )
                plc.font = Font(name="Calibri", size=9, italic=True)

            # Ghi ký tự biểu tượng [PASS] hoặc [FAIL]
            ic = ws.cell(row=r_idx, column=icon_col, value=icon_str)
            ic.fill = cell_fill
            ic.font = icon_font
            ic.alignment = Alignment(horizontal="center", vertical="center")

            # Ghi chuỗi kết quả 'PASS' hoặc 'FAIL' cùng màu nền xanh/đỏ
            rc = ws.cell(row=r_idx, column=result_col, value=result_str)
            rc.fill = cell_fill
            rc.font = cell_font
            rc.alignment = Alignment(horizontal="center", vertical="center")

            # Ghi HTTP Status thực tế nhận được
            sc = ws.cell(row=r_idx, column=status_col, value=last_status)
            sc.alignment = Alignment(horizontal="center", vertical="center")
            s_font, s_fill = get_status_styles(last_status)
            sc.font = s_font
            sc.fill = s_fill

            # 2. To mau chu va mau nen cho Expected Status tuong tu
            esc = ws.cell(row=r_idx, column=exp_status_col_paint)
            esc.alignment = Alignment(horizontal="center", vertical="center")
            e_font, e_fill = get_status_styles(exp_status)
            esc.font = e_font
            esc.fill = e_fill

            # 3. To mau chu cho Expected Message theo ma cua Expected Status
            emc = ws.cell(row=r_idx, column=exp_msg_col_paint)
            emc.alignment = Alignment(horizontal="left", vertical="center")
            emc.font = Font(
                color=e_font.color, name="Calibri", size=11, italic=True, bold=True
            )
            emc.fill = PatternFill(fill_type=None)

            # Latency Column
            lc = ws.cell(row=r_idx, column=latency_col, value=avg_latency)
            lc.alignment = Alignment(horizontal="center", vertical="center")
            lc.font = Font(name="Calibri", size=11, bold=True)

            # Ghi nhận 5000 ký tự đầu tiên của Body Response dưới dạng JSON đẹp để phục vụ debug
            try:
                parsed_json = json.loads(last_res_body)
                pretty_res = json.dumps(parsed_json, indent=2, ensure_ascii=False)
            except Exception:
                pretty_res = last_res_body

            dc = ws.cell(
                row=r_idx,
                column=detail_col,
                value=pretty_res[:5000] if len(pretty_res) > 5000 else pretty_res,
            )
            dc.alignment = Alignment(
                horizontal="left", vertical="center", wrap_text=True
            )
            dc.font = Font(name="Calibri", size=9, italic=True)

            short_name = name_str[:50] + "..." if len(name_str) > 50 else name_str

            # Color code terminal print with ANSI
            ansi_status = str(last_status)
            if last_status == 200:
                ansi_status = f"{COLOR_GREEN}{last_status}{COLOR_RESET}"
            elif last_status in (400, 401, 403, 429, 422):
                ansi_status = f"{COLOR_YELLOW}{last_status}{COLOR_RESET}"
            else:
                ansi_status = f"{COLOR_RED}{last_status}{COLOR_RESET}"

            if row_pass:
                ansi_mark = f"{COLOR_GREEN}[PASS] {result_str}{COLOR_RESET}"
            else:
                ansi_mark = f"{COLOR_RED}[FAIL] {result_str}{COLOR_RESET}"

            print(
                f"{tc_id:<10} | {short_name:<50} | {ansi_status:<14} | {ansi_mark:<23} | {avg_latency:>5} ms"
            )

        ws.column_dimensions[openpyxl.utils.get_column_letter(icon_col)].width = 8
        ws.column_dimensions[openpyxl.utils.get_column_letter(result_col)].width = 15
        ws.column_dimensions[openpyxl.utils.get_column_letter(status_col)].width = 12
        ws.column_dimensions[openpyxl.utils.get_column_letter(latency_col)].width = 14
        ws.column_dimensions[openpyxl.utils.get_column_letter(detail_col)].width = 60

        # Save worksheet stats
        sheet_stats[ws.title] = {
            "total": ws_total,
            "executed": ws_executed,
            "passed": ws_passed,
            "failed": ws_failed,
            "skipped": ws_skipped,
            "latency_sum": ws_latency_sum,
            "requests_sum": ws_requests_sum,
        }

    # Calculate overall stats helper
    pass_rate_val = (
        (passed_scenarios / executed_scenarios) * 100 if executed_scenarios > 0 else 0.0
    )
    avg_overall_latency_val = int(sum_latency / sum_requests) if sum_requests > 0 else 0

    # ----------------------------------------------------
    # TẠO EXCEL SUMMARY SHEET
    # ----------------------------------------------------
    if "Summary" in wb.sheetnames:
        wb.remove(wb["Summary"])
    ws_sum = wb.create_sheet(title="Summary", index=0)
    ws_sum.views.sheetView[0].showGridLines = True

    # Title Block
    ws_sum.merge_cells("A1:G2")
    title_cell = ws_sum["A1"]
    title_cell.value = "API TEST EXECUTION SUMMARY"
    title_cell.font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    title_cell.fill = PatternFill(start_color="1F497D", fill_type="solid")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")

    # Section 1: Overall Summary
    ws_sum.cell(row=4, column=1, value="OVERALL STATISTICS").font = Font(
        name="Calibri", size=12, bold=True, color="1F497D"
    )

    border_thin_sum = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="D9D9D9"),
        bottom=Side(style="thin", color="D9D9D9"),
    )

    metrics = [
        ("Total Scenarios", total_scenarios),
        ("Executed Scenarios", executed_scenarios),
        ("Passed Scenarios", passed_scenarios),
        ("Failed Scenarios", failed_scenarios),
        ("Skipped Scenarios", skipped_scenarios),
        ("Pass Rate", f"{pass_rate_val:.1f}%"),
        ("Avg Latency", f"{avg_overall_latency_val} ms"),
    ]

    for idx, (metric, val) in enumerate(metrics, 5):
        ws_sum.cell(row=idx, column=1, value=metric).font = Font(
            name="Calibri", size=10, bold=True
        )
        ws_sum.cell(row=idx, column=1).border = border_thin_sum
        ws_sum.cell(row=idx, column=1).alignment = Alignment(
            horizontal="left", vertical="center"
        )

        val_cell = ws_sum.cell(row=idx, column=2, value=val)
        val_cell.font = Font(name="Calibri", size=10)
        val_cell.border = border_thin_sum
        val_cell.alignment = Alignment(horizontal="right", vertical="center")

        # Color codes for Passed/Failed
        if metric == "Passed Scenarios" and passed_scenarios > 0:
            val_cell.fill = PatternFill(start_color="C6EFCE", fill_type="solid")
            val_cell.font = Font(name="Calibri", size=10, bold=True, color="006100")
        elif metric == "Failed Scenarios" and failed_scenarios > 0:
            val_cell.fill = PatternFill(start_color="FFC7CE", fill_type="solid")
            val_cell.font = Font(name="Calibri", size=10, bold=True, color="9C0006")
        elif metric == "Pass Rate" and executed_scenarios > 0:
            if passed_scenarios == executed_scenarios:
                val_cell.fill = PatternFill(start_color="C6EFCE", fill_type="solid")
                val_cell.font = Font(name="Calibri", size=10, bold=True, color="006100")
            elif failed_scenarios > 0:
                val_cell.fill = PatternFill(start_color="FFF2CC", fill_type="solid")
                val_cell.font = Font(name="Calibri", size=10, bold=True, color="7F6000")

    # Section 2: Sheet Breakdown
    start_r = 14
    ws_sum.cell(row=start_r - 1, column=1, value="SHEET-BY-SHEET BREAKDOWN").font = (
        Font(name="Calibri", size=12, bold=True, color="1F497D")
    )

    bd_headers = [
        "Sheet Name",
        "Total Rows",
        "Executed",
        "Passed",
        "Failed",
        "Skipped",
        "Avg Latency",
    ]
    for col_idx, h_text in enumerate(bd_headers, 1):
        hc = ws_sum.cell(row=start_r, column=col_idx, value=h_text)
        hc.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        hc.fill = PatternFill(start_color="366092", fill_type="solid")
        hc.alignment = Alignment(horizontal="center", vertical="center")
        hc.border = border_thin_sum

    ws_sum.row_dimensions[start_r].height = 24

    current_r = start_r + 1
    for title, stats in sheet_stats.items():
        ws_sum.row_dimensions[current_r].height = 20
        c1 = ws_sum.cell(row=current_r, column=1, value=title)
        c1.font = Font(name="Calibri", size=10, bold=True)
        c1.border = border_thin_sum
        c1.alignment = Alignment(horizontal="left", vertical="center")

        vals_bd = [
            stats["total"],
            stats["executed"],
            stats["passed"],
            stats["failed"],
            stats["skipped"],
            (
                f"{int(stats['latency_sum'] / stats['requests_sum'])} ms"
                if stats["requests_sum"] > 0
                else "0 ms"
            ),
        ]

        for col_idx, v_val in enumerate(vals_bd, 2):
            cc = ws_sum.cell(row=current_r, column=col_idx, value=v_val)
            cc.font = Font(name="Calibri", size=10)
            cc.border = border_thin_sum
            cc.alignment = Alignment(horizontal="right", vertical="center")

            # Sub-coloring for Passed/Failed
            if col_idx == 4 and stats["passed"] > 0:
                cc.fill = PatternFill(start_color="E2EFDA", fill_type="solid")
                cc.font = Font(name="Calibri", size=10, color="375623")
            elif col_idx == 5 and stats["failed"] > 0:
                cc.fill = PatternFill(start_color="FCE4D6", fill_type="solid")
                cc.font = Font(name="Calibri", size=10, color="C65911")

        current_r += 1

    for ws in wb.worksheets:
        if ws.title == "Summary":
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                col_letter = openpyxl.utils.get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 40)
            continue
        adjust_column_widths_smart(ws)

    import subprocess as _sp

    for _attempt in range(2):
        try:
            wb.save(RESULT_PATH)
            break
        except PermissionError:
            if _attempt == 0:
                print(f"\n[Warning] {RESULT_PATH} is open. Closing it automatically...")
                # Close the result file in Excel/WPS on Windows
                _sp.call(
                    [
                        "powershell",
                        "-Command",
                        f"Get-Process excel,wps,et 2>$null | "
                        f"Where-Object {{ $_.MainWindowTitle -like '*api_test_results*' }} | "
                        f"Stop-Process -Force",
                    ],
                    stdout=_sp.DEVNULL,
                    stderr=_sp.DEVNULL,
                )
                import time as _t

                _t.sleep(1)
            else:
                print(
                    f"[Error] Still cannot write to {RESULT_PATH}. Please close the file manually and re-run."
                )

    # Print Test Execution Summary
    print("=" * 100)
    print(f"[Summary] Test Execution Completed.")
    print(f"  - Total Scenarios:  {total_scenarios}")
    print(f"  - Executed:         {executed_scenarios}")
    if executed_scenarios > 0:
        pass_rate = (passed_scenarios / executed_scenarios) * 100
        print(
            f"  - {COLOR_GREEN}Passed:           {passed_scenarios} ({pass_rate:.1f}%){COLOR_RESET}"
        )
    else:
        print(
            f"  - {COLOR_GREEN}Passed:           {passed_scenarios} (0.0%){COLOR_RESET}"
        )
    if failed_scenarios > 0:
        print(f"  - {COLOR_RED}Failed:           {failed_scenarios}{COLOR_RESET}")
    else:
        print(f"  - Failed:           {failed_scenarios}")
    print(f"  - Skipped:          {skipped_scenarios}")

    if sum_requests > 0:
        avg_overall_latency = int(sum_latency / sum_requests)
        print(
            f"  - Avg Latency:      {avg_overall_latency} ms (across {sum_requests} HTTP request(s))"
        )
    print("=" * 100)
    print(f"\n[Runner] Done! Results saved to: {RESULT_PATH}")


if __name__ == "__main__":
    run_tests()
