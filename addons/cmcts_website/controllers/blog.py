# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CMCTSWebsiteBlog(http.Controller):
    """
    Controller quản lý các tính năng Blog / Tin tức của website.
    """

    @http.route(
        ["/blog", "/blog/page/<int:page>"], type="http", auth="public", website=True
    )
    def blog_list(self, page=1, category=None, **kw):
        """Hiển thị danh sách bài viết blog, hỗ trợ phân trang và lọc theo danh mục từ khóa."""
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
        """Hiển thị nội dung chi tiết của một bài viết blog."""
        return request.render(
            "cmcts_website.cmcts_blog_detail",
            {
                "post": post,
            },
        )
