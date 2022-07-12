from odoo import api, SUPERUSER_ID


def _change_no_update_scheduler_sync_sinvoice_status(env):
    ir_cron_scheduler_sync_sinvoice_status = env.ref('viin_l10n_vn_accounting_sinvoice.ir_cron_sinvoice_invoice_status_sync', raise_if_not_found=False)
    if ir_cron_scheduler_sync_sinvoice_status:
        domain = [('model', '=', 'ir.cron'), ('res_id', '=', ir_cron_scheduler_sync_sinvoice_status.id)]
        env['ir.model.data'].search(domain).write({'noupdate': False})

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _change_no_update_scheduler_sync_sinvoice_status(env)

