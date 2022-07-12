# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


    # pre: Create temp column -> set data
    # post: Get data from temp column to create `ir.property` and delete temp column
def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
    AND table_name = 'product_category' AND column_name = 'temp_default_equipment_category_id';""")
    if cr.fetchone():
        Property = env['ir.property']
        # GET fields_id
        cr.execute("""
            SELECT id, name, model
            FROM ir_model_fields
            WHERE model IN ('product.template','product.category') AND name IN ('property_default_equipment_category_id','property_maintenance_team_id');
            """)
        rows_ir_model_fields = cr.fetchall()
        fields_id = {}
        for r in rows_ir_model_fields:
            id, name, model = r
            fields_id['%s,%s'%(name,model)] = id

        # GET data of model `product.category`
        cr.execute("""
            SELECT pc.id, pc.temp_default_equipment_category_id, pc.temp_maintenance_team_id, mec.id, mec.company_id, mt.id, mt.company_id
            FROM product_category as pc
            LEFT JOIN  maintenance_equipment_category as mec ON pc.temp_default_equipment_category_id = mec.id
            LEFT JOIN  maintenance_team as mt ON pc.temp_maintenance_team_id = mt.id;
            """)
        rows_product_category = cr.fetchall()

    #     GET data of model `product.template`
        cr.execute("""
            SELECT pt.id, pt.temp_default_equipment_category_id, pt.temp_maintenance_team_id, mec.id, mec.company_id, mt.id, mt.company_id
            FROM product_template as pt
            LEFT JOIN  maintenance_equipment_category as mec ON pt.temp_default_equipment_category_id = mec.id
            LEFT JOIN  maintenance_team as mt ON pt.temp_maintenance_team_id = mt.id;
            """)
        rows_product_template = cr.fetchall()

    #     CREATE ir.property (`product.category`)
        for row in rows_product_category:
            #SET sequential
            id, default_equipment_category_id, maintenance_team_id, ref_mec_id, ref_mec_company_id, ref_mt_id, ref_mt_company_id = row

            if default_equipment_category_id:
                default_equipment_category_values = {
                    'name': 'property_default_equipment_category_id',
                    'res_id':'product.category,%s' %id,                                 #char : product.category,11
                    'fields_id': fields_id.get('property_default_equipment_category_id,product.category'),          #int
                    'value_reference': 'maintenance.equipment.category,%s' %ref_mec_id,   #char : maintenance.equipment.category,1
                    'type': 'many2one',
                    'company_id': ref_mec_company_id,                                   #int
                    }
                Property.create(default_equipment_category_values)
            if maintenance_team_id:
                maintenance_team_values = {
                    'name': 'property_maintenance_team_id',
                    'res_id':'product.category,%s' %id,
                    'fields_id': fields_id.get('property_maintenance_team_id,product.category'),
                    'value_reference': 'maintenance.team,%s' %ref_mt_id,
                    'type': 'many2one',
                    'company_id': ref_mt_company_id,
                    }
                Property.create(maintenance_team_values)

    #     CREATE ir.property (`product.template`)
        for row in rows_product_template:
            #SET sequential
            id, default_equipment_category_id, maintenance_team_id, ref_mec_id, ref_mec_company_id, ref_mt_id, ref_mt_company_id = row

            if default_equipment_category_id:
                default_equipment_category_values = {
                    'name': 'property_default_equipment_category_id',
                    'res_id':'product.template,%s' %id,
                    'fields_id': fields_id.get('property_default_equipment_category_id,product.template'),
                    'value_reference': 'maintenance.equipment.category,%s' %ref_mec_id,
                    'type': 'many2one',
                    'company_id': ref_mec_company_id,
                    }
                Property.create(default_equipment_category_values)
            if maintenance_team_id:
                maintenance_team_values = {
                    'name': 'property_maintenance_team_id',
                    'res_id':'product.template,%s' %id,
                    'fields_id': fields_id.get('property_maintenance_team_id,product.template'),
                    'value_reference': 'maintenance.team,%s' %ref_mt_id,
                    'type': 'many2one',
                    'company_id': ref_mt_company_id,
                    }
                Property.create(maintenance_team_values)

    #     DROP temp column
        cr.execute("""
            ALTER TABLE product_category
            DROP COLUMN temp_default_equipment_category_id,
            DROP COLUMN temp_maintenance_team_id;""")
        cr.execute("""
            ALTER TABLE product_template
            DROP COLUMN temp_default_equipment_category_id,
            DROP COLUMN temp_maintenance_team_id;""")
