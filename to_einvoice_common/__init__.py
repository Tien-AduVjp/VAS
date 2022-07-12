from . import models
from . import wizard
from . import controllers

def post_init_hook(cr, registry):
    cr.execute("""
        ALTER TABLE account_journal ALTER COLUMN code TYPE character varying(6);
    """)
