# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class CMCTSWebsiteCore(http.Controller):
    """
    Controller xử lý các route cơ bản (trang tĩnh, liên hệ, tư vấn) và tiện ích chung của website.
    """

    @http.route("/aboutus", type="http", auth="public", website=True)
    def about_us(self, **kw):
        """Hiển thị trang Giới thiệu (About Us)."""
        return request.render("cmcts_website.cmcts_about_us", {})

    @http.route("/tu-van", type="http", auth="public", website=True)
    def tu_van(self, **kw):
        """Hiển thị trang Tư vấn giải pháp, có thể nhận tham số product_id để hiển thị sản phẩm quan tâm."""
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
        """Chuyển hướng (redirect) từ đường dẫn /contactus cũ sang /tu-van."""
        return request.redirect("/tu-van")

    @http.route(
        "/contactus/submit", type="http", auth="public", website=True, methods=["POST"], csrf=False
    )
    def contactus_submit_redirect(self, **post):
        """Chuyển hướng submit form từ đường dẫn /contactus/submit sang /tu-van/submit."""
        return request.redirect("/tu-van/submit", code=307)

    @http.route(
        "/tu-van/submit", type="http", auth="public", website=True, methods=["POST"], csrf=False
    )
    def submit_tu_van_form(self, **post):
        """Xử lý dữ liệu POST từ form tư vấn: Tạo CRM Lead và gửi email thông báo cho Sales & Khách hàng."""
        try:
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
                # Use with_context(import_file=True) to completely bypass base_automation execution
                request.env["crm.lead"].with_context(import_file=True).sudo().create(
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

                # Force flush to catch ORM AccessError inside the try block
                request.env.flush_all()
                
                # Use Post-Redirect-Get to avoid POST rendering issues
                request.session['thank_you_name'] = name
                return request.redirect("/thank-you")
            return request.redirect("/")
        except Exception as e:
            _logger.error("Exception in submit_tu_van_form: %s", str(e), exc_info=True)
            raise

    @http.route("/thank-you", type="http", auth="public", website=True, methods=["GET"])
    def thank_you_page(self, **kw):
        name = request.session.pop('thank_you_name', '')
        is_event = request.session.pop('thank_you_is_event', False)
        return request.render("cmcts_website.cmcts_thank_you", {"customer_name": name, "is_event": is_event})

    @http.route("/quote/test_submit", type="http", auth="public", website=True)
    def test_submit(self, **kw):
        """Route dùng để test việc tạo Sale Order trực tiếp (chỉ dành cho mục đích debug/test)."""
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

    @http.route("/privacy", type="http", auth="public", website=True)
    def privacy(self, **kw):
        """Hiển thị trang Chính sách bảo mật (Privacy Policy)."""
        return request.render("cmcts_website.cmcts_privacy", {})

    @http.route("/terms", type="http", auth="public", website=True)
    def terms(self, **kw):
        """Hiển thị trang Điều khoản sử dụng (Terms of Service). Hiện tại fallback sang trang Privacy."""
        return request.render(
            "cmcts_website.cmcts_privacy", {}
        )  # Fallback to privacy for now

    @http.route("/search", type="http", auth="public", website=True)
    def search_results(self, **kw):
        """Xử lý tìm kiếm chung trên toàn website (tìm kiếm Sản phẩm và Bài viết Blog)."""
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
