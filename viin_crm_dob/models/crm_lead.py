from lxml import etree

from odoo import models, fields, api


class Lead(models.Model):
    _inherit = 'crm.lead'

    customer_dob = fields.Date(string='Date of Birth', compute='_compute_customer_dob', readonly=False, store=True)
    customer_dyob = fields.Integer(
        string='Day of Birth',
        compute='_compute_yy_mm_of_birth',
        store=True,
        help="The technical field storing the partner's day of birth which is calculated based on the Date of Birth.",
    )
    customer_mob = fields.Integer(
        string='Month of Birth',
        compute='_compute_yy_mm_of_birth',
        store=True,
        help="The technical field storing the partner's month of birth which is calculated based on the Date of Birth.",
    )
    customer_yob = fields.Integer(
        string='Year of Birth',
        compute='_compute_yy_mm_of_birth',
        store=True,
        help="The technical field storing the partner's year of birth which is calculated based on the Date of Birth.",
    )

    @api.depends('partner_id')
    def _compute_customer_dob(self):
        for r in self:
            r.update(r._prepare_dob_values_from_partner(r.partner_id))

    @api.depends('customer_dob')
    def _compute_yy_mm_of_birth(self):
        for r in self:
            if not r.customer_dob:
                r.customer_yob = r.customer_mob = r.customer_dyob = False
            else:
                r.customer_yob, r.customer_mob, r.customer_dyob = self.env['to.base'].split_date(r.customer_dob)

    def _prepare_dob_values_from_partner(self, partner):
        values = { 'customer_dob': partner.dob or self.customer_dob }
        return values

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        res = super(Lead, self)._prepare_customer_values(partner_name, is_company, parent_id)
        if not is_company and self.customer_dob:
            res['dob'] = self.customer_dob
        return res

    def _merge_data(self, fields):
        fields.append('customer_dob')
        return super(Lead, self)._merge_data(fields)

    def _merge_notify_get_merged_fields_message(self, fields):
        fields.append('customer_dob')
        return super(Lead, self)._merge_notify_get_merged_fields_message(fields)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Lead, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            crm_lead_form_arch = etree.XML(res['arch'])
            if not crm_lead_form_arch.xpath('//field[@name="customer_dob"]'):
                return res
            for doc in crm_lead_form_arch.xpath('//field[@name="partner_id"]'):
                # Add customer_dob field to context
                context = doc.get('context').strip()
                if context:
                    if 'default_dob' not in context:
                        context = "{'default_dob': customer_dob," + context[1:]
                else:
                    context = "{'default_dob': customer_dob,}"
                doc.set('context', context)
            res['arch'] = etree.tostring(crm_lead_form_arch)

        return res
