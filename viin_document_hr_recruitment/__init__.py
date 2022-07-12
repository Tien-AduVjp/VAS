from odoo import api, SUPERUSER_ID


def _run_document_generate_rule_manual(env):
    rule = env.ref('viin_document_hr_recruitment.document_auto_generate_rule_hr_applicant', raise_if_not_found=False)
    if rule:
        rule.run_manual()

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _run_document_generate_rule_manual(env)
