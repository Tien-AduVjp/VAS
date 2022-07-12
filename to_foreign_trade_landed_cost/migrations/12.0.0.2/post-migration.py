from odoo import api, SUPERUSER_ID
import psycopg2

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    for company_id in env['res.company'].search([('chart_template_id', '!=', False)]):
        company_id.create_landed_cost_journal_if_not_exists()
        
    deprecated_journal = env.ref('to_foreign_trade_landed_cost.account_journal_import_tax_landed_cost')
    if deprecated_journal:
        try:
            deprecated_journal.unlink()
            cr.commit()
        except Exception as e:
            cr.rollback()
    return 

