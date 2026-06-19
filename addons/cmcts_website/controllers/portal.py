from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo import http
from odoo.http import request

class CMCTSCustomerPortal(CustomerPortal):
    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        response = super(CMCTSCustomerPortal, self).portal_order_page(order_id, report_type, access_token, message, download, **kw)
        if hasattr(response, 'qcontext') and 'sale_order' in response.qcontext:
            order = response.qcontext['sale_order']
            # Set is_read_by_customer to True when customer views it
            if not order.is_read_by_customer:
                # Do not mark as read if viewed by an internal user (staff)
                if not request.env.user.has_group('base.group_user'):
                    order.sudo().write({'is_read_by_customer': True})
        return response

    def _prepare_quotations_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['draft', 'sent', 'cancel'])
        ]
