# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


# Create new column -> set data
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
    AND table_name = 'account_journal' AND column_name = 'sinvoice_item_name';
    """)
    if cr.fetchone():
        cr.execute("""
        ALTER TABLE account_journal
        ADD COLUMN einvoice_item_name character varying,
        ADD COLUMN send_mail_einvoice_disabled boolean,
        ADD COLUMN einvoice_item_name_new_line_replacement character varying,
        ADD COLUMN einvoice_item_name_truncation boolean,
        ADD COLUMN einvoice_item_name_limit integer;
        """)
        cr.execute("""
        UPDATE account_journal
        SET einvoice_item_name = sinvoice_item_name,
            send_mail_einvoice_disabled = send_mail_sinvoice_disabled,
            einvoice_item_name_new_line_replacement = sinvoice_item_name_new_line_replacement,
            einvoice_item_name_truncation = sinvoice_item_name_truncation,
            einvoice_item_name_limit = sinvoice_item_name_limit;
        """)

































