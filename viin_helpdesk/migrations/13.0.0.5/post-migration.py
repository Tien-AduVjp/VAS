from odoo import api, SUPERUSER_ID


def _update_end_date_on_ticket(env):
    tickets = env['helpdesk.ticket'].search(['|', ('stage_id.fold', '=', True), ('stage_id.is_final_stage', '=', True), ('resolved_duration', '=', 0)])
    for ticket in tickets:
        tracking_values = ticket.message_ids.tracking_value_ids.filtered(lambda t: 'stage_id' in t.field)
        stage_ids = env['helpdesk.stage'].search([
            ('id', 'in', tracking_values.mapped('new_value_integer')),
            '|',
                ('fold', '=', True),
                ('is_final_stage', '=', True)]
            ).ids
        tracking_values = tracking_values.filtered(lambda t: t.new_value_integer in stage_ids)
        if tracking_values:
            ticket.write({'end_date': tracking_values.sorted(key='write_date')[-1].write_date})


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_end_date_on_ticket(env)

