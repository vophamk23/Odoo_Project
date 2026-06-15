# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CMCTSWebsiteEvent(http.Controller):
    """
    Controller quản lý các tính năng Sự kiện (Event) của website.
    """

    @http.route(
        ["/events", "/events/page/<int:page>"], type="http", auth="public", website=True
    )
    def event_list(self, page=1, category=None, search=None, **kw):
        """Hiển thị danh sách sự kiện, hỗ trợ tìm kiếm, phân trang và lọc theo danh mục."""
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
        """Hiển thị nội dung chi tiết của một sự kiện."""
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
        csrf=False,
    )
    def submit_event_register(self, **post):
        """Xử lý form đăng ký tham gia sự kiện và lưu thông tin người đăng ký."""
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

                request.env["event.registration"].with_context(import_file=True).sudo().create(
                    {
                        "event_id": int(event_id),
                        "name": name,
                        "email": email,
                        "phone": phone,
                    }
                )
            except Exception as e:
                pass

            request.session['thank_you_name'] = name
            request.session['thank_you_is_event'] = True
            return request.redirect("/thank-you")
        return request.redirect("/")
