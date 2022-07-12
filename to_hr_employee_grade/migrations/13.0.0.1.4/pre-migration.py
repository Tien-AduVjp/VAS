from odoo import api, SUPERUSER_ID


def _rename_xml_ids(env):
    leader = env['ir.model.data'].search([
        ('module', '=', 'to_hr_employee_grade'),
        ('name', '=', 'leader_grade'),
        ])
    if leader:
        leader.write({'name': 'expert_grade'})
        env.cr.execute("""
        UPDATE hr_employee_grade
        SET parent_id = NULL,
            name = 'Expert'
        WHERE id = %s
        """, (leader.res_id,))


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _rename_xml_ids(env)
