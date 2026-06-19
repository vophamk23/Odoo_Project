# -*- coding: utf-8 -*-
# File: __manifest__.py
# Chức năng: File cấu hình module Quản lý Bảo Hành (Warranty Management).
# Module này tự build từ đầu,phục vụ bổ sung cho hệ thống Phase 1.
{
    "name": "Quản lý Bảo Hành",
    "version": "1.1",
    "summary": "Quản lý phiếu bảo hành thiết bị công nghệ cho CMCTS - Phase 2",
    "sequence": 15,
    "description": """
Quản lý Bảo Hành Thiết Bị (Warranty Management)
================================================
Module tự build (custom) phục vụ CMCTS Tech Company.

Chức năng chính:
- Tạo và quản lý Phiếu Bảo Hành thiết bị (Laptop, Server, Mạng...)
- Tiếp nhận và xử lý Phiếu Yêu cầu Bảo Hành từ khách hàng
- Tự động tính ngày hết hạn bảo hành
- Phân quyền 3 cấp: Không có quyền / Chỉ đọc / Toàn quyền
- Ghi log lịch sử thay đổi với Chatter
- Quản lý theo trạng thái: Tiếp nhận → Đang xử lý → Hoàn thành
    """,
    "category": "Services/Warranty",
    "author": "VoPC05",
    "website": "https://github.com/Phase2-team/VoPC-cmcts_warranty",
    # Chỉ phụ thuộc base + mail, KHÔNG dùng module CRM có sẵn của Odoo
    # Phụ thuộc thêm 'stock' để dùng:
    #   - product.product (Sản phẩm) → tên thiết bị, nhóm sản phẩm
    #   - stock.lot (Lô/Sê-ri) → số serial thiết bị đã bán
    # Phụ thuộc 'sale' để dùng sale.order (Đơn hàng)
    "depends": ["base", "mail", "account", "stock", "sale", "website_sale"],
    "data": [
        # THỨ TỰ NẠP RẤT QUAN TRỌNG: Security trước, Data sau, Views cuối
        "security/warranty_groups.xml",
        "security/warranty_rules.xml",
        "security/ir.model.access.csv",
        "data/warranty_sequence.xml",
        "data/warranty_cron.xml",
        "views/warranty_views.xml",
        "views/warranty_menus.xml",
    ],
    # Demo data: chỉ nạp khi Odoo chạy ở chế độ demo (--load-demo-data)
    "demo": [
        "demo/demo.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "cmcts_warranty/static/src/css/warranty_style.css",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
