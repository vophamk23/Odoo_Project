import sys, re

file_path = r'c:\Users\ASUS\Desktop\VoPC-cmcts\docs\Architecture.md'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_section = '''### 6.1 Bảng ánh xạ và Thống kê các Model lõi tái sử dụng

Nhằm tuân thủ triết lý "Không phát minh lại bánh xe" (DRY - Don't Repeat Yourself), toàn bộ dự án dựa trên việc tái sử dụng bộ lõi khổng lồ của Odoo. Dưới đây là bảng thống kê và ánh xạ các Model nguyên bản được gọi ra sử dụng:

| Module lõi Odoo | Model nguyên bản | Tên gọi thực tế | Cách dự án sử dụng | Module dự án can thiệp |
| --- | --- | --- | --- | --- |
| `stock` | `stock.picking` | Phiếu Nhập/Xuất kho | **Kế thừa**: Chặn nút Validate nếu thiếu Serial | `cmcts_inventory` |
| `stock` | `stock.lot` | Số Serial / Lô | **Nguyên bản**: Odoo tự sinh dữ liệu khi nhập Serial | Không |
| `stock` | `stock.quant` | Tồn kho thực tế | **Nguyên bản**: Odoo tự trừ tồn kho khi Validate | Không |
| `crm` | `crm.lead` | Cơ hội / Khách hàng tiềm năng | **Kế thừa**: Bắt sự kiện tạo mới để gán Nguồn từ Website | `cmcts_crm`, `cmcts_website` |
| `crm` | `crm.stage` | Trạng thái Pipeline | **Dữ liệu**: Khởi tạo 5 trạng thái tư vấn đặc thù | `cmcts_crm` |
| `product` | `product.template`| Danh mục Sản phẩm | **Kế thừa**: Ép mặc định theo dõi bằng Serial | `cmcts_inventory` |
| `sale` | `sale.order` | Đơn Bán Hàng | **Nguyên bản**: Sinh tự động từ báo giá của CRM | Không |
| `base` | `res.partner` | Khách hàng | **Nguyên bản**: Lưu trữ thông tin liên hệ | Không |
| `mail` | `mail.activity` | Lịch nhắc việc | **Tự động**: Tự sinh khi chuyển stage | `cmcts_crm` |

---

'''

new_lines = []
in_section_6 = False
for line in lines:
    if line.strip() == '## 6. Đặc tả Model triển khai trên Odoo':
        in_section_6 = True
    elif in_section_6 and line.startswith('## '):
        in_section_6 = False

    if in_section_6 and line.startswith('### 6.'):
        m = re.match(r'^### 6\.(\d+)(.*)$', line)
        if m:
            num = int(m.group(1))
            line = f'### 6.{num+1}{m.group(2)}\n'
            
    new_lines.append(line)

    if line.strip() == 'Phần này mô tả chi tiết cách từng Model được triển khai thực tế trong Odoo 18 — bao gồm loại field, ràng buộc, và hành vi đặc biệt.':
        new_lines.append('\n')
        new_lines.append(new_section)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done!')
