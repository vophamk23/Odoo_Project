# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CMCTSWebsiteController(http.Controller):

    @http.route('/tu-van', type='http', auth='public', website=True, methods=['POST', 'GET'])
    def submit_consultation_form(self, **post):
        # Chỉ xử lý khi có dữ liệu POST từ Form
        if request.httprequest.method == 'POST' and post:
            name = post.get('name')
            phone = post.get('phone')
            email = post.get('email')
            description = post.get('description', '')

            # Ráp nội dung nhu cầu để trigger automation bên CRM
            # Theo tài liệu Architecture.md: if vals.get('description', '').startswith('Nhu cầu:')
            full_description = f"Nhu cầu: {description}\nEmail: {email}\nSĐT: {phone}"

            # Gọi ORM tạo Lead mới trong CRM (dùng sudo để public user có thể tạo)
            request.env['crm.lead'].sudo().create({
                'name': f'Tư vấn từ Website - {name}',
                'contact_name': name,
                'phone': phone,
                'email_from': email,
                'description': full_description,
            })

            # Render trang Cảm ơn
            return request.render("cmcts_website.thank_you_page", {
                'customer_name': name
            })
        
        # Nếu vào bằng GET, redirect về trang chủ
        return request.redirect('/')
