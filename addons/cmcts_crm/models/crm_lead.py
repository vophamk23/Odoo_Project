# -*- coding: utf-8 -*-
from odoo import models, fields, api

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model_create_multi
    def create(self, vals_list):
        leads = super(CrmLead, self).create(vals_list)
        
        for lead in leads:
            # Kiểm tra nếu Lead đến từ form Website (dựa vào pattern Nhu cầu:)
            if lead.description and 'Nhu cầu:' in lead.description:
                # 1. Tự động lên lịch hoạt động (Activity) Gọi điện cho Sales
                lead.activity_schedule(
                    'mail.mail_activity_data_call',
                    summary=f'Gọi tư vấn giải pháp cho {lead.contact_name or lead.name}',
                    note=f'Khách hàng để lại thông tin trên website.\nSố điện thoại: {lead.phone}\nNội dung: {lead.description}',
                )
                
                # 2. Gửi Email tự động cho khách hàng (nếu có email)
                if lead.email_from:
                    template = self.env.ref('cmcts_crm.email_template_thank_you_consultation', raise_if_not_found=False)
                    if template:
                        template.send_mail(lead.id, force_send=True)
                        
        return leads
