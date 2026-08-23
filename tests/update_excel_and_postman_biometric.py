import json
import openpyxl,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
# Part 1: Update Excel file tests/api_test_cases.xlsx
# ==============================================================================,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
wb = openpyxl.load_workbook("tests/api_test_cases.xlsx"),,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

# Update 7.A (Row 18)
ws.cell(row=18, column=5).value = '{"controller_sn": "CTRL-HN-LOBBY-01","emp_id": "1005"}'

# Update 7.B (Row 19)
ws.cell(row=19, column=2).value = 'BiometricGet - Nhân viên hợp lệ nhưng không có dữ liệu sinh trắc học (200)'
ws.cell(row=19, column=5).value = '{"controller_sn": "CTRL-HN-LOBBY-01","emp_id": "1008"}'
ws.cell(row=19, column=6).value = 200/
ws.cell(row=19, column=7).value = 'success'///

# Insert row at row 20
ws.insert_rows(20, 1)

# Copy style from row 19 (now 19, since insertion is at 20) to row 20
for col in range(1, 11):
    src_cell = ws.cell(row=19, column=col)
    dest_cell = ws.cell(row=20, column=col)/////////////////
    if src_cell.has_style:////
        dest_cell.font = copy.copy(src_cell.font)
        dest_cell.border = copy.copy(src_cell.border)///////
        dest_cell.number_format = copy.copy(src_cell.number_format)
        dest_cell.protection = copy.copy(src_cell.protection)
        dest_cell.alignment = copy.copy(src_cell.alignment)////////////////
# Set values for 7.B2 in row 20
ws.cell(row=20, column=1).value = '7.B2'
ws.cell(row=20, column=2).value = 'BiometricGet - Nhân viên không tồn tại (400)'//////////
ws.cell(row=20, column=3).value = '/api/v1/EmployeeBiometricGet'
ws.cell(row=20, column=4).value = 'POST'
ws.cell(row=20, column=5).value = '{"controller_sn": "CTRL-HN-LOBBY-01","emp_id": "9999"}'////////////////////
ws.cell(row=20, column=6).value = 400
ws.cell(row=20, column=7).value = 'Không tìm thấy Controller hoặc Nhân viên hợp lệ'//////////////
ws.cell(row=20, column=8).value = 1
ws.cell(row=20, column=9).value = 0
ws.cell(row=20, column=10).value = 'x'

# Update 7.C (Row 21)
ws.cell(row=21, column=5).value = '{"emp_id": "1005"}'

# Update 7.E (Row 23)
ws.cell(row=23, column=5).value = '{"controller_sn": "CTRL-FAKE-DOES-NOT-EXIST","emp_id": "1005"}'

# Update 7.G (Row 25)
ws.cell(row=25, column=5).value = '{"controller_sn": "CTRL-HN-LOBBY-01","emp_id": "1005"}'

# Update 7.H (Row 26)
ws.cell(row=26, column=5).value = '{"controller_sn": "CTRL-HN-LOBBY-01","emp_id": "1005"}Lưu Access Token từ phản hồi của server@token = {{login.response.body.api_token.token}}'

wb.save("tests/api_test_cases_temp.xlsx")
wb.close()

if os.path.exists("tests/api_test_cases_temp.xlsx"):
    os.replace("tests/api_test_cases_temp.xlsx", "tests/api_test_cases.xlsx")
    print("Excel template updated successfully.")
else:
    print("Error: temp Excel file not created.")

# ==============================================================================
# Part 2: Update Postman Collection file
# ==============================================================================
postman_file = "tests/0_api_response_tests.postman_collection.json"
with open(postman_file, "r", encoding="utf-8") as f:
    p_data = json.load(f)

def find_folder(items, name):
    for item in items:
        if item.get("name") == name:
            return item
        if "item" in item:
            res = find_folder(item["item"], name)
            if res:
                return res
    return None

folder = find_folder(p_data["item"], "API 7 - Employee Biometric Get")
if folder:
    # 1. Update 7.A (index 0)
    req_7a = folder["item"][0]
    # Update payload
    req_7a["request"]["body"]["raw"] = json.dumps({
        "controller_sn": "CTRL-HN-LOBBY-01",
        "emp_id": "1005"
    }, indent=4)

    # 2. Update 7.B (index 1)
    req_7b = folder["item"][1]
    req_7b["name"] = "7.B 200 - Nhân viên hợp lệ nhưng không có dữ liệu sinh trắc học"
    # Update payload
    req_7b["request"]["body"]["raw"] = json.dumps({
        "controller_sn": "CTRL-HN-LOBBY-01",
        "emp_id": "1008"
    }, indent=4)
    # Update tests if any (expect status 200 instead of 400)
    for event in req_7b.get("event", []):
        if event.get("listen") == "test":
            exec_list = event.get("script", {}).get("exec", [])
            for i, line in enumerate(exec_list):
                if "400" in line:
                    exec_list[i] = line.replace("400", "200")

    # 3. Create 7.B2 by copying 7.B
    req_7b2 = copy.deepcopy(req_7b)
    req_7b2["name"] = "7.B2 400 - Nhân viên không tồn tại"
    req_7b2["request"]["body"]["raw"] = json.dumps({
        "controller_sn": "CTRL-HN-LOBBY-01",
        "emp_id": "9999"
    }, indent=4)
    # Update tests for 7.B2 to expect 400
    for event in req_7b2.get("event", []):
        if event.get("listen") == "test":
            exec_list = event.get("script", {}).get("exec", [])
            for i, line in enumerate(exec_list):
                if "200" in line:
                    exec_list[i] = line.replace("200", "400")

    # Insert 7.B2 at index 2 (after 7.B)
    folder["item"].insert(2, req_7b2)

    # 4. Update emp_id in 7.C, 7.E, 7.G, 7.H (index now shifts by 1)
    # indices: 7.A (0), 7.B (1), 7.B2 (2), 7.C (3), 7.D (4), 7.E (5), 7.F (6), 7.G (7), 7.H (8)
    for idx, r_idx in [("7.C", 3), ("7.E", 5), ("7.G", 7), ("7.H", 8)]:
        req = folder["item"][r_idx]
        try:
            body_dict = json.loads(req["request"]["body"]["raw"])
            if "emp_id" in body_dict:
                body_dict["emp_id"] = "1005"
                req["request"]["body"]["raw"] = json.dumps(body_dict, indent=4)
        except Exception as ex:
            print(f"Skipping JSON update for {idx}: {ex}")

    with open(postman_file, "w", encoding="utf-8") as f:
        json.dump(p_data, f, indent=4, ensure_ascii=False)
    print("Postman collection updated successfully.")
else:
    print("Error: API 7 folder not found in Postman collection.")
