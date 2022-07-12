from . import models

def _default_crm_business_type(cr):
    """Pre-populate stored computed/related fields to speedup installation"""

    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='crm_lead' and column_name='business_type_id';
    """)
    if not cr.fetchone():
        cr.execute("""
        ALTER TABLE crm_lead ADD COLUMN business_type_id integer;
        UPDATE crm_lead AS l
        SET business_type_id = p.business_type_id
        FROM res_partner AS p
        WHERE p.id = l.partner_id;
        """)

def pre_init_hook(cr):
    _default_crm_business_type(cr)

