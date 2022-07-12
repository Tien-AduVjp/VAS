from odoo import api, SUPERUSER_ID


def _run_document_generate_rule_manual(env):
    rule = env.ref('viin_document_sale.document_auto_generate_rule_sale_document', raise_if_not_found=False)
    if rule:
        rule.run_manual()

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _run_document_generate_rule_manual(env)
