# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class CMCTSWebsiteEcommerce(http.Controller):
    """
    Controller quản lý các tính năng E-commerce: Danh sách sản phẩm, Giỏ hàng, và Gửi yêu cầu báo giá.
    """

    @http.route(
        ["/shop", "/shop/page/<int:page>"], type="http", auth="public", website=True
    )
    def shop_list(self, page=1, category=None, sort=None, **kw):
        """Hiển thị danh sách sản phẩm (Cửa hàng), hỗ trợ lọc theo danh mục, sắp xếp và phân trang."""
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
        """Hiển thị trang chi tiết của một sản phẩm, lấy thông tin số lượng hiện có trong giỏ hàng."""
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
        """Xử lý thêm sản phẩm vào giỏ hàng (Form submit thông thường), sau đó chuyển hướng lại trang trước đó."""
        import json

        product_id = post.get("product_id")
        qty = int(post.get("qty", 1))
        _logger.info(
            f"===> ADD TO CART CALLED: product_id={product_id}, qty={qty}, SID: {request.session.sid}"
        )
        if product_id:
            cart_str = request.session.get("cmcts_cart_json", "{}")
            _logger.info(f"===> CURRENT CART IN SESSION: {cart_str}")

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
            _logger.info(
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
        """API thêm sản phẩm vào giỏ hàng qua AJAX (JSON), có kiểm tra số lượng tồn kho."""
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
        """Hiển thị trang Giỏ hàng / Báo giá, hiển thị danh sách sản phẩm khách đã chọn."""
        import json

        cart_str = request.session.get("cmcts_cart_json", "{}")
        _logger.info(
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
        """Xử lý cập nhật số lượng sản phẩm trong giỏ hàng (Form submit)."""
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
        """Xử lý xóa một sản phẩm khỏi giỏ hàng (Link chuyển hướng)."""
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
        """API cập nhật số lượng sản phẩm qua AJAX (JSON), có kiểm tra tồn kho."""
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
        """API xóa sản phẩm khỏi giỏ hàng qua AJAX (JSON)."""
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
        """API làm sạch (xóa toàn bộ) giỏ hàng qua AJAX (JSON)."""
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
        "/quote/submit", type="http", auth="public", website=True, methods=["POST"], csrf=False
    )
    def submit_quote_form(self, **post):
        """Xử lý submit form Yêu cầu báo giá: Tạo Sale Order với các sản phẩm trong giỏ hàng và tạo Partner nếu là khách vãng lai."""
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
                    .with_context(import_file=True).sudo()
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
                .with_context(import_file=True).sudo()
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
                    request.env["sale.order.line"].with_context(import_file=True).sudo().create(
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

            # PRG Pattern to avoid POST form resubmission and CSRF 403
            request.session['thank_you_name'] = company_name
            return request.redirect("/thank-you")
        return request.redirect("/")
