from odoo import api, SUPERUSER_ID

from . import models

def pre_init_hook(cr):

    cr.execute(
        """
        ALTER TABLE maintenance_equipment
        ADD COLUMN IF NOT EXISTS preventive_maintenance_mode CHARACTER VARYING;
        """
    )

    cr.execute(
        """
        UPDATE maintenance_equipment
        SET preventive_maintenance_mode = 'default';
        """
    )
