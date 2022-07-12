from lxml import etree
from odoo import api, SUPERUSER_ID

def _revert_context_partner_dob(env):
    crm_lead_form = env.ref('crm.crm_lead_view_form')
    crm_lead_form_arch = etree.XML(crm_lead_form.arch)
    for doc in crm_lead_form_arch.xpath('//field[@name="partner_id"]'):
        context = doc.get('context').replace("'default_dob': customer_dob,", "")
        doc.set('context', context)

        doc_parent = doc.getparent()
        for dob_field in doc_parent.findall('.//field[@name="customer_dob"]'):
            doc_parent.remove(dob_field)

    crm_lead_form.write({'arch': etree.tostring(crm_lead_form_arch, encoding='unicode')})

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _revert_context_partner_dob(env)
