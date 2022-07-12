# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


    # pre: Create temp column -> set data
    # post: Get data from temp column to create `ir.property` and delete temp column
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
    AND table_name = 'product_category' AND column_name = 'default_equipment_category_id';""")
    if cr.fetchone():
        # FOR : 'product.category'  
        cr.execute("""
            ALTER TABLE product_category
            ADD COLUMN  temp_default_equipment_category_id Integer,
            ADD COLUMN  temp_maintenance_team_id Integer;""")
        cr.execute("""
            UPDATE product_category
            SET temp_default_equipment_category_id = default_equipment_category_id,
                temp_maintenance_team_id = maintenance_team_id;""")     
           
        # FOR : 'product.template'  
        cr.execute("""
            ALTER TABLE product_template
            ADD COLUMN  temp_default_equipment_category_id Integer,
            ADD COLUMN  temp_maintenance_team_id Integer;""")
        cr.execute("""
            UPDATE product_template
            SET temp_default_equipment_category_id = default_equipment_category_id,
                temp_maintenance_team_id = maintenance_team_id;""")    
     