from . import models


def _default_to_partner_ownership_type(cr):
    """Pre-populate stored computed/related fields to speedup installation"""

    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='res_partner' and column_name='ownership_type_id';
    """)

    if not cr.fetchone():
        cr.execute("""
        ALTER TABLE res_partner ADD COLUMN ownership_type_id integer;
        UPDATE res_partner SET ownership_type_id = NULL;
        """)

def pre_init_hook(cr):
    _default_to_partner_ownership_type(cr)
