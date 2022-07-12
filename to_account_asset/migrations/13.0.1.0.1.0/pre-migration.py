from odoo import api, SUPERUSER_ID
from odoo.addons.to_account_asset.models.account_asset_depreciation_line import AccountAssetDepreciationLine
import odoo


def _prepare_query_remove_old_fields(query=''):
    query += """
    DELETE FROM ir_model_relation WHERE name ILIKE '%asset_disposal%rel%' OR name ILIKE '%account_asset_history%rel';
    DELETE FROM ir_model_fields_selection WHERE field_id IN 
                    (SELECT field.id FROM ir_model_fields AS field 
                    INNER JOIN ir_model AS model 
                    ON field.model_id=model.id AND model.model ILIKE '%asset%' AND field.name ILIKE '%method_period%');
    DELETE FROM ir_model_fields_selection WHERE field_id IN 
                    (SELECT field.id FROM ir_model_fields AS field 
                    INNER JOIN ir_model AS model 
                    ON field.model_id=model.id AND model.model ILIKE '%account_asset_history%');
    """
    return query

def _prepare_query_create_account_asset_depreciation_line_table(query=''):
    query += """
    CREATE TABLE IF NOT EXISTS account_asset_depreciation_line (
        id serial NOT NULL,
        create_uid integer, -- references res_users on delete set null,
        create_date timestamp without time zone,
        write_date timestamp without time zone,
        write_uid integer, -- references res_users on delete set null,
        name character varying(128) NOT NULL,
        sequence integer DEFAULT 100,
        move_check boolean default False,
        disposal boolean default False,
        amount numeric,
        remaining_value numeric,
        depreciated_value numeric,
        depreciation_date timestamp without time zone,
        asset_id integer REFERENCES account_asset_asset ON DELETE SET NULL,
        move_id integer REFERENCES account_move ON DELETE SET NULL
    );
    """
    return query

def _prepare_query_insert_depreciation_line_vals():
    return """
    INSERT INTO account_asset_depreciation_line 
        (create_uid, 
        create_date, 
        write_date, 
        write_uid, 
        name, 
        sequence, 
        move_check, 
        disposal, 
        amount, 
        remaining_value, 
        depreciated_value, 
        depreciation_date, 
        move_id, 
        asset_id)
    SELECT 
        move.create_uid,
        move.create_date,
        move.write_date,
        move.write_uid,
        move.ref,
        move.id,
        true,
        move.asset_disposal,
        move.amount_total,
        move.asset_remaining_value,
        move.asset_depreciated_value,
        move.date,
        move.id,
        move.account_asset_id
    FROM account_move as move 
        INNER JOIN account_asset_asset as asset ON move.account_asset_id=asset.id;"""

def _prepare_query_with_temp_column():
    return """
    ALTER TABLE account_asset_asset ADD temp_method_period character varying(64);
    UPDATE account_asset_asset SET temp_method_period = method_period;
    ALTER TABLE account_asset_category ADD temp_method_period character varying(64);
    UPDATE account_asset_category SET temp_method_period = method_period;
    """

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    #Move data to temp column
    cr.execute(_prepare_query_with_temp_column())
    
    #Remove old fields on Odoo and create new table
    query = _prepare_query_remove_old_fields()
    query = _prepare_query_create_account_asset_depreciation_line_table(query)
    cr.execute(query)
    
    #Move data from account.move to account.asset.depreciation.line 
    cr.execute(_prepare_query_insert_depreciation_line_vals())
    # Remove unused action
    action_asset_disposal = env.ref('to_account_asset.action_asset_disposal', raise_if_not_found=False)
    if action_asset_disposal:
        action_asset_disposal.unlink()
