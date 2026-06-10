# Tài liệu Đặc tả Kiến trúc và Thiết kế Module (SDD)

**Dự án:** VoPC-CMCTS Phase 1  
**Phiên bản:** 1.0  
**Ngày lập:** 09/06/2026  
**Nhóm thực hiện:** Phase1-team  
**GitHub:** https://github.com/Phase1-team/VoPC-cmcts

---

## Mục lục

1. [Tổng quan tài liệu](#1-tổng-quan-tài-liệu)
2. [Kiến trúc tổng thể hệ thống](#2-kiến-trúc-tổng-thể-hệ-thống)
3. [Kiến trúc triển khai](#3-kiến-trúc-triển-khai)
4. [Cấu trúc thư mục Custom Addons](#4-cấu-trúc-thư-mục-custom-addons)
5. [Đặc tả chi tiết từng Module](#5-đặc-tả-chi-tiết-từng-module)
6. [Đặc tả Model triển khai trên Odoo](#6-đặc-tả-model-triển-khai-trên-odoo)
7. [Quy trình tích hợp giữa các Module](#7-quy-trình-tích-hợp-giữa-các-module)
8. [Phân quyền và Bảo mật](#8-phân-quyền-và-bảo-mật)

---

## 1. Tổng quan tài liệu

Tài liệu này (System Design Document - SDD) đóng vai trò là bản vẽ kỹ thuật dành cho đội ngũ phát triển Odoo. Nó quy định:

- Kiến trúc tổng thể hệ thống
- Cách chia nhỏ và tổ chức các module
- Đặc tả chi tiết về việc kế thừa (inherit) Models và Views trong Odoo 18
- Đặc tả từng Model được triển khai thực tế trên hệ thống

Tài liệu này cần được đọc kết hợp với:

- `SRS.md` — Tài liệu phân tích yêu cầu (System Requirement Specification)
- `ERD.md` — Tài liệu thiết kế dữ liệu (Entity-Relationship Diagram)
- `test-cases.md` — Kịch bản kiểm thử hệ thống

---

## 2. Kiến trúc tổng thể hệ thống

Hệ thống tuân thủ kiến trúc 3 lớp (3-tier architecture) tiêu chuẩn của Odoo.

```
┌──────────────────────────────────────────────────────────┐
│               PRESENTATION TIER (Lớp Hiển thị)           │
│                                                          │
│   Backend: Web Client (Owl Framework) + XML Views        │
│   Frontend: QWeb Template Engine + Bootstrap + HTML/CSS  │
└────────────────────────────┬─────────────────────────────┘
                             │ HTTP/JSON-RPC
┌────────────────────────────┴─────────────────────────────┐
│            LOGIC TIER (Lớp Logic Nghiệp vụ)              │
│                                                          │
│   Odoo Framework (Python 3.10+)                          │
│   Odoo ORM (Object-Relational Mapping)                   │
│   Custom Addons: cmcts_inventory, cmcts_crm,             │
│                  cmcts_website                           │
└────────────────────────────┬─────────────────────────────┘
                             │ ORM / SQL
┌────────────────────────────┴─────────────────────────────┐
│                 DATA TIER (Lớp Dữ liệu)                  │
│                                                          │
│   PostgreSQL 14+                                         │
│   Lưu trữ toàn bộ dữ liệu cấu trúc:                      │
│   Bảng, Quan hệ, Dữ liệu thực tế                         │
└──────────────────────────────────────────────────────────┘
```

### Mô tả chi tiết từng lớp

**1. Lớp Dữ liệu (Data Tier)**

- Chịu trách nhiệm lưu trữ và truy xuất dữ liệu vật lý thông qua hệ quản trị cơ sở dữ liệu **PostgreSQL 14+**.
- Giao tiếp hoàn toàn thông qua **Odoo ORM** (Object-Relational Mapping), giúp ngăn chặn triệt để lỗ hổng SQL Injection và đảm bảo phân quyền truy cập (Record Rules) ở tầng thấp nhất.
- Thực thi các ràng buộc cấp cơ sở dữ liệu (Database Constraints), điển hình như ràng buộc tính duy nhất của Serial Number (`UNIQUE`) để đảm bảo không thất thoát hay trùng lặp kho.

**2. Lớp Logic Nghiệp vụ (Logic Tier / Business Rules)**

Được viết bằng **Python 3.10+** trên lõi Odoo Framework, đóng vai trò là "bộ não" điều phối toàn bộ dự án:

- **Phân hệ Kho (`cmcts_inventory`):** Chứa các logic kiểm duyệt (Validation) nghiêm ngặt, chặn việc xác nhận phiếu kho nếu phát hiện nhân viên chưa gán mã Serial, đồng thời tự động tính toán tồn kho khả dụng.
- **Phân hệ CRM (`cmcts_crm`):** Thực thi các luồng tự động hóa (Automated Actions), tự động phân công tác vụ (Activities) và kích hoạt kịch bản gửi Email mỗi khi một Cơ hội (Lead) thay đổi trạng thái (Stage).
- **Bộ điều khiển (Controllers):** Cung cấp các Endpoint nhận dữ liệu an toàn (POST request) từ Website Form và đẩy trực tiếp vào Pipeline của CRM mà không cần thao tác tay.

**3. Lớp Hiển thị (Presentation Tier / UI)**

Cung cấp trải nghiệm tương tác trực quan, phân tách rạch ròi 2 môi trường phục vụ 2 nhóm đối tượng khác nhau:

- **Môi trường Backend (Cho Nhân viên/Admin):** Xây dựng trên nền tảng **Owl Framework (JavaScript)** kết hợp các file XML định nghĩa Views. Cung cấp giao diện tương tác động như bảng Kanban kéo-thả (cho CRM) và List/Form nhập liệu siêu tốc (cho Kho).
- **Môi trường Frontend (Cho Khách hàng):** Cấu trúc bởi **QWeb Template Engine** kết hợp Bootstrap 5, HTML5 và CSS3. Đảm bảo giao diện Website và Form đăng ký hoàn toàn Responsive, hiển thị mượt mà trên cả Mobile, Tablet và Desktop.

---

## 3. Kiến trúc triển khai

Dự án chạy trên nền tảng Docker với 2 container riêng biệt.

```
┌──────────────────────────────────────────────────────────┐
│                   Docker Host (Ubuntu)                   │
│                                                          │
│       ┌──────────────────┐        ┌──────────────────┐   │
│       │     odoo-web     │        │     odoo-db      │   │
│       │                  │        │                  │   │
│       │   Odoo Server    │        │    PostgreSQL    │   │
│       │   Port: 8069     │        │    Port: 5432    │   │
│       │                  │        │                  │   │
│       │  Volume mount:   │        │   Volume mount:  │   │
│       │  ./addons/       │        │   ./pgdata/      │   │
│       │  ./config/       │        │                  │   │
│       └────────┬─────────┘        └────────┬─────────┘   │
│                │                           │             │
│                └─────────────┬─────────────┘             │
│                    Docker Bridge Network                 │
└──────────────────────────────────────────────────────────┘

Truy cập từ bên ngoài:
- Odoo Web: http://localhost:8069
- Database: localhost:5432 (nội bộ)
```

### Cấu hình docker-compose.yml

```yaml
version: "3.8"
services:
  odoo-web:
    image: odoo:18.0
    ports:
      - "8069:8069"
    volumes:
      - ./addons:/mnt/extra-addons
      - ./config/odoo.conf:/etc/odoo/odoo.conf
    depends_on:
      - odoo-db
    networks:
      - odoo-network

  odoo-db:
    image: postgres:14
    environment:
      POSTGRES_DB: odoo18_vopc
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
    volumes:
      - ./pgdata:/var/lib/postgresql/data
    networks:
      - odoo-network

networks:
  odoo-network:
    driver: bridge
```

### Cấu hình odoo.conf

```ini
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
db_host = odoo-db
db_port = 5432
db_user = odoo
db_password = odoo
db_name = odoo18_vopc
admin_passwd = admin
```

---

## 4. Cấu trúc thư mục Custom Addons

Toàn bộ code lập trình riêng cho dự án nằm trong thư mục `addons/`.

```
addons/
├── cmcts_inventory/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── stock_picking.py        # Override validate phiếu kho
│   │   └── product_template.py     # Force default tracking = serial
│   ├── views/
│   │   └── stock_picking_views.xml # Highlight cột Serial Number
│   └── security/
│       └── ir.model.access.csv
│
├── cmcts_crm/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── crm_lead.py             # Override write() bắt sự kiện
│   └── data/
│       ├── crm_stage_data.xml      # Dữ liệu khởi tạo 6 stage pipeline
│       ├── automation_rules.xml    # Quy tắc tự động tạo Activity
│       └── mail_templates.xml      # Template email theo từng stage
│
└── cmcts_website/
    ├── __init__.py
    ├── __manifest__.py
    ├── controllers/
    │   ├── __init__.py
    │   └── main.py                 # Xử lý form submit → CRM Lead
    ├── views/
    │   ├── homepage_templates.xml  # Hero Banner, dịch vụ, footer
    │   └── contact_form_templates.xml  # Form đăng ký tư vấn
    └── static/                     # Chứa tài nguyên tĩnh (Assets)
        └── src/
            ├── css/
            │   └── style.css       # File CSS tuỳ chỉnh giao diện
            └── img/
                └── hero_banner.jpg # Ảnh minh họa trang chủ
```

---

## 5. Đặc tả chi tiết từng Module

### 5.1 Module `cmcts_inventory`

**Mục tiêu:** Ràng buộc chặt chẽ quy trình nhập, xuất, chuyển kho phải thông qua nhập Serial Number. Ngăn chặn validate phiếu khi thiếu Serial.

**File `__manifest__.py`**

```python
{
    'name': 'CMCTS Inventory',
    'version': '18.0.1.0.0',
    'summary': 'Ràng buộc Serial Number trong quy trình kho',
    'depends': ['stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
```

**File `models/stock_picking.py`**

Kế thừa `stock.picking`, override hàm `button_validate()` để kiểm tra Serial trước khi cho phép hoàn thành phiếu.

```python
from odoo import models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        # Kiểm tra tất cả dòng move_line
        for move_line in self.move_line_ids:
            product = move_line.product_id
            # Chỉ kiểm tra sản phẩm tracking = serial
            if product.tracking == 'serial':
                # Kiểm tra khi nhập kho (lot_name)
                if not move_line.lot_name and not move_line.lot_id:
                    raise UserError(
                        _(
                            'Sản phẩm "%s" yêu cầu nhập Serial Number '
                            'trước khi xác nhận phiếu kho.'
                        ) % product.name
                    )
        # Nếu hợp lệ thì tiếp tục validate bình thường
        return super().button_validate()
```

**File `models/product_template.py`**

Kế thừa `product.template`, đặt giá trị mặc định tracking = serial để nhân viên không quên cấu hình.

```python
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tracking = fields.Selection(
        default='serial',
        help='Mặc định theo dõi theo Serial Number cho thiết bị công nghệ'
    )
```

**File `views/stock_picking_views.xml`**

Kế thừa form phiếu kho, highlight cột Serial Number để nhân viên dễ chú ý.

```xml
<odoo>
    <record id="view_picking_form_cmcts" model="ir.ui.view">
        <field name="name">stock.picking.form.cmcts</field>
        <field name="model">stock.picking</field>
        <field name="inherit_id" ref="stock.view_picking_form"/>
        <field name="arch" type="xml">
            <!-- Thêm decoration màu đỏ cho dòng chưa có serial -->
            <xpath expr="//field[@name='move_line_ids_without_package']"
                   position="attributes">
                <attribute name="decoration-danger">
                    product_id.tracking == 'serial' and not lot_id
                </attribute>
            </xpath>
        </field>
    </record>
</odoo>
```

---

### 5.2 Module `cmcts_website`

**Mục tiêu:** Xây dựng giao diện website chuyên nghiệp và form đăng ký tư vấn tự động tạo Lead trong CRM.

**File `__manifest__.py`**

```python
{
    'name': 'CMCTS Website',
    'version': '18.0.1.0.0',
    'summary': 'Giao diện website và form tư vấn kết nối CRM',
    'depends': ['website', 'crm'],
    'data': [
        'views/homepage_templates.xml',
        'views/contact_form_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
}
```

**File `controllers/main.py`**

Xử lý POST request từ form đăng ký tư vấn, tạo Lead trong CRM.

```python
from odoo import http
from odoo.http import request

class CmctsWebsite(http.Controller):

    @http.route('/tu-van', type='http', auth='public', website=True)
    def tu_van_page(self, **kwargs):
        # Hiển thị trang form đăng ký tư vấn
        return request.render('cmcts_website.contact_form_page', {})

    @http.route('/tu-van/submit', type='http',
                auth='public', website=True, methods=['POST'])
    def tu_van_submit(self, **post):
        # Lấy dữ liệu từ form
        name     = post.get('name', '').strip()
        email    = post.get('email', '').strip()
        phone    = post.get('phone', '').strip()
        need     = post.get('need', '').strip()
        note     = post.get('note', '').strip()

        # Kiểm tra dữ liệu tối thiểu
        if not name or not email:
            return request.render('cmcts_website.contact_form_page', {
                'error': 'Vui lòng điền đầy đủ Họ tên và Email.'
            })

        # Tạo Lead trong CRM, dùng sudo() vì user là public
        request.env['crm.lead'].sudo().create({
            'name'       : f'Tư vấn từ website - {name}',
            'contact_name': name,
            'email_from' : email,
            'phone'      : phone,
            'description': f'Nhu cầu: {need}\nGhi chú: {note}',
            'type'       : 'opportunity',
        })

        # Trả về trang cảm ơn
        return request.render('cmcts_website.thank_you_page', {
            'name': name
        })
```

**File `views/contact_form_templates.xml`**

```xml
<odoo>
    <!-- Trang form đăng ký tư vấn -->
    <template id="contact_form_page" name="Đăng ký tư vấn">
        <t t-call="website.layout">
            <div class="container py-5">
                <h2>Đăng ký tư vấn</h2>
                <t t-if="error">
                    <div class="alert alert-danger">
                        <t t-esc="error"/>
                    </div>
                </t>
                <form action="/tu-van/submit" method="post">
                    <input type="hidden" name="csrf_token"
                           t-att-value="request.csrf_token()"/>
                    <div class="mb-3">
                        <label>Họ và tên *</label>
                        <input type="text" name="name"
                               class="form-control" required="1"/>
                    </div>
                    <div class="mb-3">
                        <label>Email *</label>
                        <input type="email" name="email"
                               class="form-control" required="1"/>
                    </div>
                    <div class="mb-3">
                        <label>Số điện thoại</label>
                        <input type="text" name="phone"
                               class="form-control"/>
                    </div>
                    <div class="mb-3">
                        <label>Nhu cầu tư vấn</label>
                        <select name="need" class="form-select">
                            <option value="Quản lý Kho">Quản lý Kho</option>
                            <option value="CRM">CRM</option>
                            <option value="Website">Website</option>
                            <option value="Khác">Khác</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label>Ghi chú thêm</label>
                        <textarea name="note" class="form-control"
                                  rows="3"></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">
                        Gửi thông tin
                    </button>
                </form>
            </div>
        </t>
    </template>

    <!-- Trang cảm ơn sau khi submit -->
    <template id="thank_you_page" name="Cảm ơn">
        <t t-call="website.layout">
            <div class="container py-5 text-center">
                <h2>Cảm ơn bạn đã liên hệ!</h2>
                <p>Chúng tôi sẽ liên hệ lại với bạn trong thời gian sớm nhất.</p>
                <a href="/" class="btn btn-primary">Về trang chủ</a>
            </div>
        </t>
    </template>
</odoo>
```

---

### 5.3 Module `cmcts_crm`

**Mục tiêu:** Tự động hoá quy trình chăm sóc khách hàng — tạo Activity nhắc việc và gửi email template khi nhân viên chuyển stage pipeline.

**File `__manifest__.py`**

```python
{
    'name': 'CMCTS CRM',
    'version': '18.0.1.0.0',
    'summary': 'Tự động hoá Sales Pipeline và chăm sóc khách hàng',
    'depends': ['crm', 'base_automation', 'mail'],
    'data': [
        'data/crm_stage_data.xml',
        'data/mail_templates.xml',
        'data/automation_rules.xml',
    ],
    'installable': True,
    'auto_install': False,
}
```

**File `models/crm_lead.py`**

Kế thừa `crm.lead`, override hàm `write()` để bắt sự kiện chuyển stage và thực hiện logic bổ sung nếu cần.

```python
from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # Trường tùy chỉnh: lưu nguồn gốc lead
    lead_source = fields.Selection([
        ('website_form', 'Form Website'),
        ('manual'      , 'Tạo thủ công'),
        ('phone'       , 'Gọi điện'),
    ], string='Nguồn Lead', default='manual')

    @api.model_create_multi
    def create(self, vals_list):
        # Tự động đánh dấu lead từ website
        for vals in vals_list:
            if vals.get('description', '').startswith('Nhu cầu:'):
                vals['lead_source'] = 'website_form'
        return super().create(vals_list)
```

**File `data/crm_stage_data.xml`**

Khởi tạo 6 stage cho pipeline CRM theo đúng quy trình tư vấn thiết kế.

```xml
<odoo>
    <data noupdate="1">
        <record id="stage_new" model="crm.stage">
            <field name="name">Tiếp nhận yêu cầu</field>
            <field name="sequence">1</field>
            <field name="probability">10</field>
        </record>
        <record id="stage_consulting" model="crm.stage">
            <field name="name">Đang tư vấn</field>
            <field name="sequence">2</field>
            <field name="probability">30</field>
        </record>
        <record id="stage_quotation" model="crm.stage">
            <field name="name">Gửi báo giá</field>
            <field name="sequence">3</field>
            <field name="probability">50</field>
        </record>
        <record id="stage_negotiation" model="crm.stage">
            <field name="name">Đàm phán</field>
            <field name="sequence">4</field>
            <field name="probability">70</field>
        </record>
        <record id="stage_won" model="crm.stage">
            <field name="name">Chốt hợp đồng</field>
            <field name="sequence">5</field>
            <field name="probability">100</field>
            <field name="is_won">True</field>
        </record>
    </data>
</odoo>
```

**File `data/mail_templates.xml`**

Template email tự động gửi khi lead chuyển sang stage "Gửi báo giá".

```xml
<odoo>
    <record id="email_template_quotation" model="mail.template">
        <field name="name">CRM - Gửi báo giá tư vấn</field>
        <field name="model_id" ref="crm.model_crm_lead"/>
        <field name="subject">Báo giá dịch vụ tư vấn - {{ object.name }}</field>
        <field name="email_to">{{ object.email_from }}</field>
        <field name="body_html"><![CDATA[
            <p>Kính gửi {{ object.partner_id.name or object.contact_name }},</p>
            <p>Cảm ơn bạn đã quan tâm đến dịch vụ của chúng tôi.</p>
            <p>Chúng tôi xin gửi đến bạn báo giá cho nhu cầu
               <strong>{{ object.name }}</strong>.</p>
            <p>Nhân viên phụ trách: {{ object.user_id.name }}</p>
            <p>Liên hệ: {{ object.user_id.email }}</p>
            <br/>
            <p>Trân trọng,<br/>Đội ngũ CMCTS</p>
        ]]></field>
    </record>
</odoo>
```

**File `data/automation_rules.xml`**

Quy tắc tự động tạo Activity khi lead chuyển sang stage "Đang tư vấn".

```xml
<odoo>
    <record id="automation_consulting_activity"
            model="base.automation">
        <field name="name">
            CRM - Tạo Activity khi chuyển sang Đang tư vấn
        </field>
        <field name="model_id" ref="crm.model_crm_lead"/>
        <field name="trigger">on_write</field>
        <field name="filter_domain">
            [('stage_id', '=', ref('cmcts_crm.stage_consulting'))]
        </field>
        <field name="filter_pre_domain">
            [('stage_id', '!=', ref('cmcts_crm.stage_consulting'))]
        </field>
        <field name="action_server_ids" eval="[(4, ref('cmcts_crm.action_create_call_activity'))]"/>
    </record>

    <record id="action_create_call_activity"
            model="ir.actions.server">
        <field name="name">Tạo Activity Gọi điện tư vấn</field>
        <field name="model_id" ref="crm.model_crm_lead"/>
        <field name="state">object_create</field>
        <field name="fields_lines">
            <!-- Tạo mail.activity nhắc gọi điện trong 1 ngày -->
        </field>
    </record>
</odoo>
```

---

## 6. Đặc tả Model triển khai trên Odoo

Phần này mô tả chi tiết cách từng Model được triển khai thực tế trong Odoo 18 — bao gồm loại field, ràng buộc, và hành vi đặc biệt.

### 6.1 Model `stock.picking` (Phiếu kho)

**Loại:** Kế thừa (inherit) từ module `stock`  
**File:** `cmcts_inventory/models/stock_picking.py`

| Field           | Loại Field | Ràng buộc          | Ghi chú                                 |
| --------------- | ---------- | ------------------ | --------------------------------------- |
| name            | Char       | required, readonly | Tự sinh: WH/IN/xxxx, WH/OUT/xxxx        |
| picking_type_id | Many2one   | required           | Liên kết `stock.picking.type`           |
| partner_id      | Many2one   | optional           | Khách hàng hoặc nhà cung cấp            |
| state           | Selection  | readonly           | draft, waiting, confirmed, done, cancel |
| move_line_ids   | One2many   | -                  | Các dòng chi tiết di chuyển             |
| sale_id         | Many2one   | optional           | Đơn bán hàng nguồn                      |
| scheduled_date  | Datetime   | -                  | Ngày dự kiến thực hiện                  |

**Hành vi tùy chỉnh:**

Hàm `button_validate()` được override để thêm bước kiểm tra:

1. Duyệt qua toàn bộ `move_line_ids`
2. Với mỗi sản phẩm có `tracking == 'serial'`, kiểm tra `lot_id` hoặc `lot_name` có giá trị không
3. Nếu trống thì raise `UserError` kèm tên sản phẩm cụ thể để nhân viên biết sản phẩm nào còn thiếu serial
4. Nếu tất cả hợp lệ thì gọi `super().button_validate()` để Odoo xử lý bình thường

---

### 6.2 Model `stock.lot` (Serial Number)

**Loại:** Sử dụng nguyên (không kế thừa thêm) từ module `stock`  
**Bảng DB:** `stock_lot`

| Field       | Loại Field | Ràng buộc | Ghi chú                                     |
| ----------- | ---------- | --------- | ------------------------------------------- |
| name        | Char       | required  | Mã Serial do nhân viên nhập, VD: DELL-SN001 |
| product_id  | Many2one   | required  | Liên kết `product.product`                  |
| company_id  | Many2one   | required  | Tự điền theo công ty đang đăng nhập         |
| create_date | Datetime   | readonly  | Tự sinh khi tạo bản ghi                     |
| note        | Text       | optional  | Ghi chú tình trạng, bảo hành                |

**Ràng buộc SQL:**

```sql
-- Odoo tự tạo ràng buộc này khi cài module stock
UNIQUE (name, product_id, company_id)
```

Nghĩa là: cùng 1 công ty, cùng 1 sản phẩm thì không được có 2 serial trùng tên.

---

### 6.3 Model `stock.quant` (Tồn kho thực tế)

**Loại:** Sử dụng nguyên từ module `stock`  
**Bảng DB:** `stock_quant`

| Field             | Loại Field | Ràng buộc | Ghi chú                                              |
| ----------------- | ---------- | --------- | ---------------------------------------------------- |
| product_id        | Many2one   | required  | Sản phẩm                                             |
| location_id       | Many2one   | required  | Vị trí lưu kho                                       |
| lot_id            | Many2one   | optional  | Serial Number (bắt buộc nếu product tracking=serial) |
| quantity          | Float      | -         | Số lượng đang có (On Hand)                           |
| reserved_quantity | Float      | -         | Số lượng đã giữ chờ xuất                             |

**Lưu ý:** Bảng này không được thao tác trực tiếp. Odoo tự cập nhật khi validate phiếu kho.  
Số lượng khả dụng = `quantity - reserved_quantity`.

---

### 6.4 Model `crm.lead` (Lead / Opportunity)

**Loại:** Kế thừa (inherit) từ module `crm`  
**File:** `cmcts_crm/models/crm_lead.py`

| Field       | Loại Field | Ràng buộc | Ghi chú                                         |
| ----------- | ---------- | --------- | ----------------------------------------------- |
| name        | Char       | required  | Tên cơ hội kinh doanh                           |
| partner_id  | Many2one   | optional  | Khách hàng (`res.partner`)                      |
| stage_id    | Many2one   | required  | Stage hiện tại trong pipeline                   |
| user_id     | Many2one   | -         | Nhân viên Sales phụ trách                       |
| probability | Float      | -         | Xác suất chốt (0-100%), tự cập nhật theo stage  |
| email_from  | Char       | -         | Email khách hàng                                |
| phone       | Char       | -         | Số điện thoại khách hàng                        |
| description | Text       | -         | Nội dung nhu cầu, ghi chú                       |
| lead_source | Selection  | -         | Trường tùy chỉnh: website_form / manual / phone |
| type        | Selection  | -         | lead hoặc opportunity                           |

**Hành vi tùy chỉnh:**

Hàm `create()` được override để:

1. Kiểm tra nếu `description` bắt đầu bằng "Nhu cầu:" (định dạng của form website)
2. Tự động gán `lead_source = 'website_form'`
3. Giúp nhân viên Sales phân biệt nguồn gốc của từng Lead

---

### 6.5 Model `product.template` (Template sản phẩm)

**Loại:** Kế thừa (inherit) từ module `product`  
**File:** `cmcts_inventory/models/product_template.py`

| Field      | Loại Field | Ràng buộc        | Ghi chú                                         |
| ---------- | ---------- | ---------------- | ----------------------------------------------- |
| name       | Char       | required         | Tên sản phẩm                                    |
| list_price | Float      | -                | Giá bán mặc định                                |
| type       | Selection  | required         | Bắt buộc chọn `storable` cho thiết bị lưu kho   |
| tracking   | Selection  | default='serial' | Mặc định theo Serial, tùy chỉnh đặt lại default |
| categ_id   | Many2one   | required         | Danh mục sản phẩm                               |

**Hành vi tùy chỉnh:**

Field `tracking` được ghi đè default value thành `'serial'` để khi nhân viên tạo sản phẩm mới, hệ thống mặc định đã chọn sẵn theo dõi bằng Serial Number, tránh trường hợp quên cấu hình.

---

### 6.6 Model `res.partner` (Khách hàng / Nhà cung cấp)

**Loại:** Sử dụng nguyên từ module `base`  
**Bảng DB:** `res_partner`

| Field         | Loại Field | Ràng buộc | Ghi chú                               |
| ------------- | ---------- | --------- | ------------------------------------- |
| name          | Char       | required  | Tên đối tác                           |
| email         | Char       | -         | Email liên hệ                         |
| phone         | Char       | -         | Số điện thoại                         |
| customer_rank | Integer    | -         | Giá trị > 0 nếu là khách hàng         |
| supplier_rank | Integer    | -         | Giá trị > 0 nếu là nhà cung cấp       |
| category_id   | Many2many  | -         | Tags: VIP, Thân thiết, Tiềm năng, Mới |
| street        | Char       | -         | Địa chỉ                               |

---

### 6.7 Model `sale.order` (Đơn bán hàng)

**Loại:** Sử dụng nguyên từ module `sale`  
**Bảng DB:** `sale_order`

| Field          | Loại Field | Ràng buộc | Ghi chú                      |
| -------------- | ---------- | --------- | ---------------------------- |
| name           | Char       | readonly  | Tự sinh: S00001, S00002...   |
| partner_id     | Many2one   | required  | Khách hàng                   |
| opportunity_id | Many2one   | optional  | CRM Lead nguồn gốc           |
| state          | Selection  | readonly  | draft / sale / done / cancel |
| order_line     | One2many   | -         | Chi tiết các sản phẩm        |
| amount_total   | Float      | computed  | Tổng tiền, tự tính           |

**Hành vi quan trọng:**

Khi nhấn "Confirm" (chuyển state từ draft sang sale), Odoo tự động:

1. Tạo `stock.picking` loại Delivery (xuất kho) liên kết với đơn hàng
2. Tạo `stock.move` cho từng dòng sản phẩm trong đơn
3. Phiếu xuất kho ở trạng thái "Waiting" chờ nhân viên kho xử lý

---

## 7. Quy trình tích hợp giữa các Module

Phần này mô tả luồng dữ liệu xuyên suốt từ khi khách hàng tiếp cận đến khi xuất kho giao hàng.

```
Bước 1 — Khách hàng truy cập website
    cmcts_website controller phục vụ trang /tu-van
    Khách điền form và nhấn Gửi

Bước 2 — Tạo Lead CRM tự động
    Controller /tu-van/submit nhận POST data
    Gọi request.env['crm.lead'].sudo().create(...)
    Lead xuất hiện trong CRM ở stage "Tiếp nhận yêu cầu"
    lead_source = 'website_form'

Bước 3 — Nhân viên Sales xử lý Lead
    Mở CRM, kéo Lead sang "Đang tư vấn"
    Automated Action kích hoạt: tạo Activity "Gọi điện trong 1 ngày"
    Kéo sang "Gửi báo giá"
    Automated Action kích hoạt: gửi email template báo giá

Bước 4 — Tạo đơn bán hàng
    Nhấn "New Quotation" từ Lead
    Thêm sản phẩm, điều chỉnh giá
    Nhấn "Confirm" → Đơn bán hàng được tạo (sale.order)
    Hệ thống tự tạo phiếu xuất kho (stock.picking)

Bước 5 — Nhân viên kho thực hiện xuất kho
    Mở phiếu xuất kho, kiểm tra sản phẩm
    Chọn Serial Number cụ thể cho từng sản phẩm
    Nhấn Validate
    cmcts_inventory kiểm tra: tất cả serial phải có giá trị
    Nếu hợp lệ: phiếu chuyển Done, tồn kho giảm, serial ghi nhận đã xuất
```

---

## 8. Phân quyền và Bảo mật

### 8.1 Nhóm người dùng Odoo

| Nhóm            | XML ID                           | Mô tả                         |
| --------------- | -------------------------------- | ----------------------------- |
| Quản trị viên   | `base.group_system`              | Toàn quyền hệ thống           |
| Nhân viên Kho   | `stock.group_stock_user`         | Làm phiếu kho, xem tồn kho    |
| Quản lý Kho     | `stock.group_stock_manager`      | Cấu hình kho, xem báo cáo     |
| Nhân viên Sales | `sales_team.group_sale_salesman` | Quản lý CRM, lập báo giá      |
| Quản lý Sales   | `sales_team.group_sale_manager`  | Xem toàn bộ pipeline, báo cáo |

### 8.2 Phân quyền theo Model

| Model              | Nhân viên Kho   | Nhân viên Sales | Khách (Public)    |
| ------------------ | --------------- | --------------- | ----------------- |
| `stock.picking`    | Đọc / Ghi / Xóa | Chỉ đọc         | Không có          |
| `stock.lot`        | Đọc / Ghi       | Không có        | Không có          |
| `stock.quant`      | Đọc / Ghi       | Không có        | Không có          |
| `crm.lead`         | Không có        | Đọc / Ghi       | Không có          |
| `sale.order`       | Chỉ đọc         | Đọc / Ghi       | Không có          |
| `res.partner`      | Chỉ đọc         | Đọc / Ghi       | Không có          |
| `product.template` | Đọc / Ghi       | Chỉ đọc         | Chỉ đọc (website) |

### 8.3 File `ir.model.access.csv`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_stock_lot_user,stock.lot.user,stock.model_stock_lot,stock.group_stock_user,1,1,1,0
access_stock_quant_user,stock.quant.user,stock.model_stock_quant,stock.group_stock_user,1,1,1,0
```

---

_Tài liệu này được lưu tại: `/docs/SDD_VoPC_cmcts.md` trên GitHub repo_  
_Cập nhật lần cuối: 09/06/2026_
