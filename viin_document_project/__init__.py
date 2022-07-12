from odoo import api, SUPERUSER_ID


def _run_document_generate_rule_manual(env):
    project_rule = env.ref('viin_document_project.document_auto_generate_rule_project_project_document', raise_if_not_found=False)
    task_rule = env.ref('viin_document_project.document_auto_generate_rule_project_task_document', raise_if_not_found=False)
    if project_rule:
        project_rule.run_manual()
    if task_rule:
        task_rule.run_manual()

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _run_document_generate_rule_manual(env)
