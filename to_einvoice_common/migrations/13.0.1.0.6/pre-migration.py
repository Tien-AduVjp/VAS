# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


# Create new column -> set data
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    #unlink record in ir.cron
    cron = env.ref('to_accounting_sinvoice.ir_cron_ensure_download_sinvoice_file', raise_if_not_found=False)
    if cron:
        cron.unlink()
    #update fields renamed
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
    AND table_name = 'account_journal' and column_name = 'sinvoice_send_mail_option'
    """)
    if cr.fetchone():
        cr.execute("""
        ALTER TABLE account_journal ADD COLUMN einvoice_send_mail_option character varying;
        """)
        cr.execute("""
        UPDATE account_journal SET einvoice_send_mail_option = sinvoice_send_mail_option
        """)