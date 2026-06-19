# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home
from odoo.exceptions import AccessDenied

class CMCTSHome(Home):
    """
    Ghi đè (override) Controller Home mặc định để tùy chỉnh logic đăng nhập của hệ thống.
    """
    @http.route("/web/login", type="http", auth="none")
    def web_login(self, redirect=None, **kw):
        """Xử lý đăng nhập, bổ sung kiểm tra phân quyền (Quản trị vs Người dùng) dựa trên loại tài khoản được chọn trên giao diện."""
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
