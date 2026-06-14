# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from odoo.exceptions import AccessDenied


class CMCTSWebsiteController(http.Controller):
    import logging

    _logger = logging.getLogger(__name__)

    # --- Core Routes ---
    @http.route("/aboutus", type="http", auth="public", website=True)
    def about_us(self, **kw):
        return request.render("cmcts_website.cmcts_about_us", {})

    @http.route("/tu-van", type="http", auth="public", website=True)
    def tu_van(self, **kw):
        product_id = kw.get("product_id")
        product = None
        if product_id:
            try:
                product = request.env["product.template"].sudo().browse(int(product_id))
                if not product.exists():
                    product = None
            except Exception:
                product = None
        return request.render("cmcts_website.cmcts_contactus", {"product": product})

    @http.route("/contactus", type="http", auth="public", website=True)
    def contactus_redirect(self, **kw):
        return request.redirect("/tu-van")

    @http.route(
        "/contactus/submit", type="http", auth="public", website=True, methods=["POST"]
    )
    def contactus_submit_redirect(self, **post):
        return request.redirect("/tu-van/submit", code=307)

    @http.route(
        "/tu-van/submit", type="http", auth="public", website=True, methods=["POST"]
    )
    def submit_tu_van_form(self, **post):
        if request.httprequest.method == "POST" and post:
            name = post.get("name")
            phone = post.get("phone")
            email = post.get("email")
            solution = post.get("solution", "N/A")
            requirements = post.get("requirements", "")

            solution_map = {
                "servers": "Hạ Tầng Server & Máy Chủ",
                "storage": "Hạ Tầng Lưu Trữ (Storage)",
                "networking": "Thiết Bị Mạng & Truyền Dẫn",
                "edge": "Nút Mạng Biên & IoT Edge",
            }
            solution_label = solution_map.get(solution, solution)

            full_description = f"Nhu cầu: {requirements}\nSolution Interest: {solution_label}\nEmail: {email}\nPhone: {phone}"

            # 1. Create Lead in CRM
            request.env["crm.lead"].sudo().create(
                {
                    "name": f"Website Lead - {name}",
                    "contact_name": name,
                    "phone": phone,
                    "email_from": email,
                    "description": full_description,
                }
            )

            # 2. Send Email to Sales Team (Admin)
            from datetime import datetime

            now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

            admin_body = f"""
                <div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333333;">
                    <h2 style="color: #a04100; border-bottom: 1px solid #eee; padding-bottom: 10px;">Yêu Cầu Tư Vấn Mới Từ Website</h2>
                    <p>Có một yêu cầu tư vấn mới được gửi từ website <strong>CMCTS</strong>:</p>
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                        <tr>
                            <td style="width: 150px; font-weight: bold; padding: 8px 0; border-bottom: 1px solid #f0f0f0;">Họ và tên:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #f0f0f0;">{name}</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold; padding: 8px 0; border-bottom: 1px solid #f0f0f0;">Số điện thoại:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #f0f0f0;">{phone}</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold; padding: 8px 0; border-bottom: 1px solid #f0f0f0;">Email liên hệ:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #f0f0f0;">{email}</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold; padding: 8px 0; border-bottom: 1px solid #f0f0f0;">Giải pháp quan tâm:</td>
                            <td style="padding: 8px 0; border-bottom: 1px solid #f0f0f0;">{solution_label}</td>
                        </tr>
                        <tr>
                            <td style="font-weight: bold; padding: 8px 0; vertical-align: top;">Nội dung nhu cầu:</td>
                            <td style="padding: 8px 0; white-space: pre-wrap;">{requirements}</td>
                        </tr>
                    </table>
                    <p style="margin-top: 25px; font-size: 12px; color: #777777; border-top: 1px solid #eee; padding-top: 10px;">
                        Hệ thống CRM CMCTS - Tự động ghi nhận lúc {now_str}
                    </p>
                </div>
            """

            try:
                request.env["mail.mail"].sudo().create(
                    {
                        "subject": f"[Yêu cầu Tư vấn] Khách hàng mới: {name}",
                        "body_html": admin_body,
                        "email_from": "website@cmcts.vn",
                        "email_to": "sales@cmcts.com",
                    }
                ).send()
            except Exception as e:
                pass

            # 3. Send Confirmation Email to Client
            client_body = f"""
                <div style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333333; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.02);">
                    <div style="background-color: #0a2540; padding: 25px; text-align: center; color: #ffffff;">
                        <h1 style="margin: 0; font-size: 22px; font-weight: 800; letter-spacing: 2px;">CMCTS</h1>
                        <p style="margin: 5px 0 0 0; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #fe6b00;">Technology &amp; Solution</p>
                    </div>
                    <div style="padding: 30px; background-color: #ffffff;">
                        <p>Kính gửi <strong>{name}</strong>,</p>
                        <p>Cảm ơn ông/bà đã quan tâm đến giải pháp và dịch vụ công nghệ của <strong>CMCTS</strong>. Chúng tôi đã nhận được thông tin đăng ký tư vấn của ông/bà với các nội dung chi tiết sau:</p>
                        
                        <div style="background-color: #f9fafb; padding: 20px; border-radius: 6px; margin: 20px 0; border: 1px solid #f0f0f0;">
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr>
                                    <td style="width: 150px; font-weight: bold; padding: 5px 0;">Họ và tên:</td>
                                    <td>{name}</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: bold; padding: 5px 0;">Số điện thoại:</td>
                                    <td>{phone}</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: bold; padding: 5px 0;">Email:</td>
                                    <td>{email}</td>
                                </tr>
                                <tr>
                                    <td style="font-weight: bold; padding: 5px 0;">Giải pháp quan tâm:</td>
                                    <td>{solution_label}</td>
                                </tr>
                            </table>
                        </div>

                        <p>Đội ngũ chuyên gia kỹ sư hạ tầng của CMCTS sẽ tiến hành nghiên cứu yêu cầu và liên hệ lại với ông/bà trong vòng <strong>24 giờ làm việc</strong> để đưa ra phương án tư vấn tối ưu nhất.</p>
                        
                        <p>Nếu có bất kỳ yêu cầu khẩn cấp nào cần hỗ trợ ngay, xin vui lòng gọi hotline của chúng tôi tại số <strong>1900 2468</strong>.</p>
                        
                        <p style="margin-top: 30px; font-weight: bold; color: #0a2540;">Trân trọng,<br/>Đội ngũ giải pháp CMCTS</p>
                    </div>
                    <div style="background-color: #f3f4f6; padding: 15px; text-align: center; font-size: 11px; color: #777777; border-top: 1px solid #e5e7eb;">
                        <p style="margin: 0 0 5px 0;">Tòa nhà CMC, 11 Duy Tân, Cầu Giấy, Hà Nội | Hotline: 1900 2468</p>
                        <p style="margin: 0;">© 2026 CMCTS. All rights reserved.</p>
                    </div>
                </div>
            """

            try:
                request.env["mail.mail"].sudo().create(
                    {
                        "subject": "CMCTS - Xác nhận yêu cầu tư vấn giải pháp",
                        "body_html": client_body,
                        "email_from": "sales@cmcts.com",
                        "email_to": email,
                    }
                ).send()
            except Exception as e:
                pass

            return request.render(
                "cmcts_website.cmcts_thank_you", {"customer_name": name}
            )
        return request.redirect("/")

    @http.route("/quote/test_submit", type="http", auth="public", website=True)
    def test_submit(self, **kw):
        sale_order = (
            request.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": 3,
                    "note": "Test Note",
                    "client_order_ref": "Website B2B Quote",
                }
            )
        )
        return request.make_response(f"Created SO: {sale_order.id}")

    # --- E-commerce & Cart Routes ---
    @http.route(
        ["/shop", "/shop/page/<int:page>"], type="http", auth="public", website=True
    )
    def shop_list(self, page=1, category=None, sort=None, **kw):
        domain = [("is_published", "=", True)]

        if category:
            try:
                cat_id = int(category)
                domain.append(("public_categ_ids", "in", [cat_id]))
            except ValueError:
                pass

        order = "sequence, id desc"
        if sort == "price_asc":
            order = "list_price asc, id desc"
        elif sort == "price_desc":
            order = "list_price desc, id desc"
        elif sort == "name_asc":
            order = "name asc, id desc"

        ProductTemplate = request.env["product.template"].sudo()
        total_products = ProductTemplate.search_count(domain)
        limit = 12
        import math

        total_pages = math.ceil(total_products / limit) if total_products else 1
        page = max(1, min(page, total_pages))
        offset = (page - 1) * limit

        products = ProductTemplate.search(
            domain, limit=limit, offset=offset, order=order
        )
        categories = request.env["product.public.category"].sudo().search([])

        return request.render(
            "cmcts_website.cmcts_shop_list",
            {
                "products": products,
                "categories": categories,
                "current_category": (
                    int(category) if category and category.isdigit() else None
                ),
                "current_sort": sort,
                "page": page,
                "total_pages": total_pages,
                "limit": limit,
                "total_products": total_products,
                "offset": offset,
            },
        )

    @http.route(
        ['/shop/detail/<model("product.template"):product>'],
        type="http",
        auth="public",
        website=True,
    )
    def shop_detail(self, product, **kw):
        import json
        cart_str = request.session.get("cmcts_cart_json", "{}")
        try:
            cart_data = json.loads(cart_str)
        except Exception:
            cart_data = {}
        
        current_cart_qty = cart_data.get(str(product.id), 0)

        return request.render(
            "cmcts_website.cmcts_shop_detail",
            {
                "product": product,
                "current_cart_qty": current_cart_qty,
            },
        )

    @http.route(
        "/shop/cart/add", type="http", auth="user", website=True, methods=["POST"]
    )
    def add_to_cart(self, **post):
        import json

        product_id = post.get("product_id")
        qty = int(post.get("qty", 1))
        self._logger.info(
            f"===> ADD TO CART CALLED: product_id={product_id}, qty={qty}, SID: {request.session.sid}"
        )
        if product_id:
            cart_str = request.session.get("cmcts_cart_json", "{}")
            self._logger.info(f"===> CURRENT CART IN SESSION: {cart_str}")

            try:
                cart = json.loads(cart_str)
            except Exception:
                cart = {}

            pid_str = str(product_id)
            if pid_str in cart:
                cart[pid_str] += qty
            else:
                cart[pid_str] = qty

            new_cart_str = json.dumps(cart)
            request.session["cmcts_cart_json"] = new_cart_str
            request.session.is_dirty = True
            self._logger.info(
                f"===> NEW CART IN SESSION: {request.session.get('cmcts_cart_json')}"
            )

        referrer = request.httprequest.referrer or "/shop"
        import re

        referrer = re.sub(r"([?&])(added|qty)=[^&]*", r"\1", referrer)
        referrer = referrer.replace("&&", "&").rstrip("?&")
        separator = "&" if "?" in referrer else "?"
        redirect_url = f"{referrer}{separator}added={product_id}&qty={qty}"

        return request.redirect(redirect_url)

    @http.route(
        "/shop/cart/add_json",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def add_to_cart_json(self, **post):
        import json

        product_id = post.get("product_id")
        qty = int(post.get("qty", 1))

        if not product_id:
            return request.make_response(
                json.dumps({"success": False, "error": "Missing product_id"}),
                [("Content-Type", "application/json")],
            )

        cart_str = request.session.get("cmcts_cart_json", "{}")
        try:
            cart = json.loads(cart_str)
        except Exception:
            cart = {}

        pid_str = str(product_id)
        product = request.env["product.template"].sudo().browse(int(product_id))

        is_storable = getattr(product, 'is_storable', False) or getattr(product, 'detailed_type', product.type) == 'product'
        if is_storable:
            current_qty = cart.get(pid_str, 0)
            if (current_qty + qty) > product.sudo().qty_available:
                return request.make_response(
                    json.dumps({"success": False, "error": f"Vượt quá tồn kho! '{product.name}' hiện chỉ còn {int(product.sudo().qty_available)} cái."}),
                    [("Content-Type", "application/json")],
                )

        if pid_str in cart:
            cart[pid_str] += qty
        else:
            cart[pid_str] = qty

        request.session["cmcts_cart_json"] = json.dumps(cart)
        request.session.is_dirty = True

        total_qty = sum(cart.values())
        product = request.env["product.template"].sudo().browse(int(product_id))

        data = {
            "success": True,
            "product_id": product.id,
            "product_name": product.name,
            "product_price_formatted": "{:,.0f}".format(product.list_price).replace(
                ",", "."
            )
            + " đ",
            "added_qty": qty,
            "total_qty": total_qty,
            "remaining_qty": max(0, int(product.sudo().qty_available) - sum([v for k, v in cart.items() if k == str(product.id)])),
            "image_url": (
                f"/web/image/product.template/{product.id}/image_1920"
                if product.image_1920
                else "/web/static/img/placeholder.png"
            ),
        }
        return request.make_response(
            json.dumps(data), [("Content-Type", "application/json")]
        )

    @http.route("/shop/cart", type="http", auth="user", website=True)
    def quote_cart(self, **kw):
        import json

        cart_str = request.session.get("cmcts_cart_json", "{}")
        self._logger.info(
            f"===> LOADING CART VIEW, SID: {request.session.sid}, cart_str={cart_str}"
        )

        try:
            cart_data = json.loads(cart_str)
        except Exception:
            cart_data = {}
            request.session["cmcts_cart_json"] = "{}"

        product_ids = [int(pid) for pid in cart_data.keys() if pid.isdigit()]
        products = (
            request.env["product.template"].sudo().search([("id", "in", product_ids)])
        )
        product_dict = {p.id: p for p in products}

        cart_items = []
        total_price = 0.0

        # Lấy danh sách keys từ dưới lên trên (mới nhất lên đầu)
        for pid_str in reversed(list(cart_data.keys())):
            if not pid_str.isdigit():
                continue
            pid = int(pid_str)
            if pid in product_dict:
                p = product_dict[pid]
                qty = cart_data[pid_str]
                item_total = p.list_price * qty
                total_price += item_total
                cart_items.append({"product": p, "qty": qty, "item_total": item_total})

        return request.render(
            "cmcts_website.cmcts_quote_cart",
            {"cart_items": cart_items, "total_price": total_price},
        )

    @http.route(
        "/shop/cart/update", type="http", auth="public", website=True, methods=["POST"]
    )
    def update_cart(self, **post):
        import json

        product_id = post.get("product_id")
        qty = int(post.get("qty", 0))
        if product_id:
            cart_str = request.session.get("cmcts_cart_json", "{}")
            try:
                cart = json.loads(cart_str)
            except Exception:
                cart = {}

            pid_str = str(product_id)
            if pid_str in cart:
                if qty > 0:
                    cart[pid_str] = qty
                else:
                    del cart[pid_str]

            request.session["cmcts_cart_json"] = json.dumps(cart)
            request.session.is_dirty = True

        return request.redirect("/shop/cart")

    @http.route("/shop/cart/remove", type="http", auth="public", website=True)
    def remove_from_cart(self, product_id, **kw):
        import json

        if product_id:
            cart_str = request.session.get("cmcts_cart_json", "{}")
            try:
                cart = json.loads(cart_str)
            except Exception:
                cart = {}

            pid_str = str(product_id)
            if pid_str in cart:
                del cart[pid_str]

            request.session["cmcts_cart_json"] = json.dumps(cart)
            request.session.is_dirty = True

        return request.redirect("/shop/cart")

    @http.route(
        "/shop/cart/update_json",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def update_cart_json(self, **post):
        import json

        product_id = post.get("product_id")
        qty = int(post.get("qty", 1))

        if not product_id:
            return request.make_response(
                json.dumps({"success": False, "error": "Missing product_id"}),
                [("Content-Type", "application/json")],
            )

        cart_str = request.session.get("cmcts_cart_json", "{}")
        try:
            cart = json.loads(cart_str)
        except Exception:
            cart = {}

        pid_str = str(product_id)
        product = request.env["product.template"].sudo().browse(int(product_id))

        is_storable = getattr(product, 'is_storable', False) or getattr(product, 'detailed_type', product.type) == 'product'
        if is_storable:
            if qty > product.sudo().qty_available:
                return request.make_response(
                    json.dumps({"success": False, "error": f"Vượt quá tồn kho! '{product.name}' hiện chỉ còn {int(product.sudo().qty_available)} cái."}),
                    [("Content-Type", "application/json")],
                )

        if pid_str in cart:
            if qty > 0:
                cart[pid_str] = qty
            else:
                del cart[pid_str]

        request.session["cmcts_cart_json"] = json.dumps(cart)
        request.session.is_dirty = True

        # Calculate new totals
        product_ids = [int(pid) for pid in cart.keys() if pid.isdigit()]
        products = (
            request.env["product.template"].sudo().search([("id", "in", product_ids)])
        )
        product_dict = {p.id: p for p in products}

        total_price = 0.0
        total_qty = 0
        for p_id_str, p_qty in cart.items():
            if not p_id_str.isdigit():
                continue
            p_id = int(p_id_str)
            if p_id in product_dict:
                total_price += product_dict[p_id].list_price * p_qty
                total_qty += p_qty

        item_total = 0.0
        if int(product_id) in product_dict:
            item_total = product_dict[int(product_id)].list_price * qty

        data = {
            "success": True,
            "total_price_formatted": (
                "{:,.0f} đ".format(total_price) if total_price > 0 else "Liên hệ Sales"
            ),
            "total_price": total_price,
            "total_qty": total_qty,
            "item_total_formatted": (
                "{:,.0f} đ".format(item_total) if item_total > 0 else "0 đ"
            ),
            "cart_empty": len(cart) == 0,
        }
        return request.make_response(
            json.dumps(data), [("Content-Type", "application/json")]
        )

    @http.route(
        "/shop/cart/remove_json",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def remove_from_cart_json(self, **post):
        import json

        product_id = post.get("product_id")
        if not product_id:
            return request.make_response(
                json.dumps({"success": False, "error": "Missing product_id"}),
                [("Content-Type", "application/json")],
            )

        cart_str = request.session.get("cmcts_cart_json", "{}")
        try:
            cart = json.loads(cart_str)
        except Exception:
            cart = {}

        pid_str = str(product_id)
        if pid_str in cart:
            del cart[pid_str]

        request.session["cmcts_cart_json"] = json.dumps(cart)
        request.session.is_dirty = True

        # Calculate new totals
        product_ids = [int(pid) for pid in cart.keys() if pid.isdigit()]
        products = (
            request.env["product.template"].sudo().search([("id", "in", product_ids)])
        )
        product_dict = {p.id: p for p in products}

        total_price = 0.0
        total_qty = 0
        for p_id_str, p_qty in cart.items():
            if not p_id_str.isdigit():
                continue
            p_id = int(p_id_str)
            if p_id in product_dict:
                total_price += product_dict[p_id].list_price * p_qty
                total_qty += p_qty

        data = {
            "success": True,
            "total_price_formatted": (
                "{:,.0f} đ".format(total_price) if total_price > 0 else "Liên hệ Sales"
            ),
            "total_price": total_price,
            "total_qty": total_qty,
            "cart_empty": len(cart) == 0,
        }
        return request.make_response(
            json.dumps(data), [("Content-Type", "application/json")]
        )

    @http.route(
        "/shop/cart/clear_json",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
        csrf=True,
    )
    def clear_cart_json(self, **post):
        import json

        request.session["cmcts_cart_json"] = "{}"
        request.session.is_dirty = True
        data = {
            "success": True,
            "total_price_formatted": "Liên hệ Sales",
            "total_price": 0.0,
            "total_qty": 0,
            "cart_empty": True,
        }
        return request.make_response(
            json.dumps(data), [("Content-Type", "application/json")]
        )

    @http.route(
        "/quote/submit", type="http", auth="public", website=True, methods=["POST"]
    )
    def submit_quote_form(self, **post):
        import json

        if request.httprequest.method == "POST" and post:
            company_name = post.get("company_name", "Unknown")
            contact_email = post.get("contact_email", "")
            phone = post.get("phone", "")
            notes = post.get("notes", "")
            urgent = post.get("urgent")

            cart_str = request.session.get("cmcts_cart_json", "{}")
            try:
                cart_data = json.loads(cart_str)
            except Exception:
                cart_data = {}

            product_ids = [int(pid) for pid in cart_data.keys() if pid.isdigit()]
            products = (
                request.env["product.template"]
                .sudo()
                .search([("id", "in", product_ids)])
            )

            # Xử lý Partner (Khách hàng)
            partner_id = (
                request.env.user.partner_id.id
                if not request.env.user._is_public()
                else False
            )

            if not partner_id:
                # Khách vãng lai -> Tạo Contact mới
                new_partner = (
                    request.env["res.partner"]
                    .sudo()
                    .create(
                        {
                            "name": company_name,
                            "email": contact_email,
                            "phone": phone,
                            "is_company": True,
                        }
                    )
                )
                partner_id = new_partner.id

            # Tạo Báo giá (Sale Order)
            note_content = (
                f"Ghi chú: {notes}\nƯu tiên: Khẩn cấp"
                if urgent == "on"
                else f"Ghi chú: {notes}"
            )
            sale_order = (
                request.env["sale.order"]
                .sudo()
                .create(
                    {
                        "partner_id": partner_id,
                        "note": note_content,
                        "client_order_ref": "Website B2B Quote",
                        "state": "sent",  # Set to sent so it appears in portal immediately
                    }
                )
            )

            # Tạo chi tiết Báo giá (Sale Order Lines)
            for p in products:
                qty = cart_data.get(str(p.id), 0)
                # Lấy product.product (variant) vì sale.order.line yêu cầu product_id là product.product
                product_variant = (
                    p.product_variant_ids[0] if p.product_variant_ids else False
                )
                if product_variant:
                    request.env["sale.order.line"].sudo().create(
                        {
                            "order_id": sale_order.id,
                            "product_id": product_variant.id,
                            "product_uom_qty": qty,
                            "price_unit": p.list_price,
                        }
                    )

            # Clear cart
            request.session["cmcts_cart_json"] = "{}"
            request.session.is_dirty = True

            return request.render(
                "cmcts_website.cmcts_thank_you",
                {"customer_name": company_name, "order_name": sale_order.name},
            )
        return request.redirect("/")

    # --- Content Routes ---
    # --- Content Routes ---
    @http.route(
        ["/blog", "/blog/page/<int:page>"], type="http", auth="public", website=True
    )
    def blog_list(self, page=1, category=None, **kw):
        domain = [("is_published", "=", True)]
        posts = (
            request.env["blog.post"]
            .sudo()
            .search(domain, order="post_date desc, id desc")
        )

        if category:
            cat_map = {
                "hardware": [
                    "lưu trữ",
                    "trung tâm",
                    "nvme",
                    "phần cứng",
                    "edge",
                    "trung tâm dữ liệu",
                ],
                "security": ["bảo mật", "an toàn", "security", "zero-trust"],
                "cloud": ["đám mây", "cloud", "lai"],
                "network": ["mạng", "sdn", "network", "kết nối"],
            }
            keywords = cat_map.get(category, [])
            if keywords:
                posts = posts.filtered(
                    lambda p: any(
                        k in (p.name or "").lower() or k in (p.subtitle or "").lower()
                        for k in keywords
                    )
                )

        # Pagination logic
        limit = 10
        total_items = len(posts)
        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
        page = max(1, min(page, total_pages))
        offset = (page - 1) * limit
        paginated_posts = posts[offset : offset + limit]

        return request.render(
            "cmcts_website.cmcts_blog_list",
            {
                "posts": paginated_posts,
                "current_category": category,
                "page": page,
                "total_pages": total_pages,
            },
        )

    @http.route(
        ['/blog/detail/<model("blog.post"):post>'],
        type="http",
        auth="public",
        website=True,
    )
    def blog_detail(self, post, **kw):
        return request.render(
            "cmcts_website.cmcts_blog_detail",
            {
                "post": post,
            },
        )

    @http.route(
        ["/events", "/events/page/<int:page>"], type="http", auth="public", website=True
    )
    def event_list(self, page=1, category=None, search=None, **kw):
        domain = [("is_published", "=", True)]
        events = request.env["event.event"].sudo().search(domain)

        if category:
            cat_map = {
                "conference": ["hội nghị", "hội thảo", "workshop"],
                "webinar": ["trực tuyến", "webinar", "online"],
                "expo": ["triển lãm", "expo"],
            }
            keywords = cat_map.get(category, [])
            if keywords:
                events = events.filtered(
                    lambda e: any(k in (e.name or "").lower() for k in keywords)
                )

        if search:
            search_low = search.lower()
            events = events.filtered(lambda e: search_low in (e.name or "").lower())

        # Pagination logic
        limit = 6
        total_items = len(events)
        total_pages = (total_items + limit - 1) // limit if total_items > 0 else 1
        page = max(1, min(page, total_pages))
        offset = (page - 1) * limit
        paginated_events = events[offset : offset + limit]

        return request.render(
            "cmcts_website.cmcts_event_list",
            {
                "events": paginated_events,
                "current_category": category,
                "search": search,
                "page": page,
                "total_pages": total_pages,
            },
        )

    @http.route(
        ['/events/detail/<model("event.event"):event>'],
        type="http",
        auth="public",
        website=True,
    )
    def event_detail(self, event, **kw):
        return request.render(
            "cmcts_website.cmcts_event_detail",
            {
                "event": event,
            },
        )

    @http.route(
        "/events/register/submit",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def submit_event_register(self, **post):
        if request.env.user._is_public():
            return request.redirect("/web/login")

        event_id = post.get("event_id")
        name = post.get("name")
        email = post.get("email")
        phone = post.get("phone")

        if event_id and name and email:
            try:
                # To prevent wkhtmltopdf network error causing 500 error in demo environment,
                # we remove the automated email scheduler for this event before registering.
                request.env["event.mail"].sudo().search(
                    [("event_id", "=", int(event_id))]
                ).unlink()

                request.env["event.registration"].sudo().create(
                    {
                        "event_id": int(event_id),
                        "name": name,
                        "email": email,
                        "phone": phone,
                    }
                )
            except Exception as e:
                pass

            return request.render(
                "cmcts_website.cmcts_thank_you",
                {
                    "customer_name": name,
                    "is_event": True,
                },
            )
        return request.redirect("/")

    # --- Utility Routes ---
    @http.route("/privacy", type="http", auth="public", website=True)
    def privacy(self, **kw):
        return request.render("cmcts_website.cmcts_privacy", {})

    @http.route("/terms", type="http", auth="public", website=True)
    def terms(self, **kw):
        return request.render(
            "cmcts_website.cmcts_privacy", {}
        )  # Fallback to privacy for now

    @http.route("/search", type="http", auth="public", website=True)
    def search_results(self, **kw):
        q = kw.get("q", "").strip()
        products = []
        blogs = []

        if q:
            products = (
                request.env["product.template"]
                .sudo()
                .search(
                    ["|", ("name", "ilike", q), ("default_code", "ilike", q)], limit=12
                )
            )

            try:
                blogs = (
                    request.env["blog.post"]
                    .sudo()
                    .search(
                        ["|", ("name", "ilike", q), ("subtitle", "ilike", q)], limit=12
                    )
                )
            except Exception:
                blogs = (
                    request.env["blog.post"]
                    .sudo()
                    .search([("name", "ilike", q)], limit=12)
                )

        return request.render(
            "cmcts_website.cmcts_search_results",
            {
                "q": q,
                "products": products,
                "blogs": blogs,
            },
        )


class CMCTSHome(Home):
    @http.route("/web/login", type="http", auth="none")
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == "POST" and kw.get("login_type"):
            login = kw.get("login")
            password = kw.get("password")
            db = request.session.db or kw.get("db")
            
            error_msg = None
            if login and password and db:
                try:
                    auth_info = request.env["res.users"].authenticate(db, {'login': login, 'password': password, 'type': 'password'}, {})
                    uid = auth_info.get('uid') if isinstance(auth_info, dict) else auth_info
                    if uid:
                        user = request.env["res.users"].sudo().browse(uid)
                        is_admin = (user.login == "admin")
                        login_type = kw.get("login_type")
                        if login_type == "user" and is_admin:
                            error_msg = "Tài khoản này là Quản trị. Vui lòng chọn tab 'Quản trị'."
                        elif login_type == "admin" and not is_admin:
                            error_msg = "Tài khoản này là Người dùng. Vui lòng chọn tab 'Người dùng'."
                except AccessDenied:
                    pass
            
            if error_msg:
                orig_password = request.params.get("password")
                request.params["password"] = "THIS_WILL_FAIL_12345"
                if "password" in kw:
                    kw["password"] = "THIS_WILL_FAIL_12345"
                
                response = super(CMCTSHome, self).web_login(redirect=redirect, **kw)
                
                request.params["password"] = orig_password
                if "password" in kw:
                    kw["password"] = orig_password
                
                if hasattr(response, "qcontext"):
                    response.qcontext["error"] = error_msg
                
                return response

        return super(CMCTSHome, self).web_login(redirect=redirect, **kw)
