from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    cr.execute("""
    DROP TABLE IF EXISTS account_analytic_tag_account_asset_history_rel;
    DROP TABLE IF EXISTS account_asset_asset_asset_disposal_rel;
    UPDATE account_asset_asset SET method_period = CASE WHEN temp_method_period = '1' THEN 1 ELSE 12 END;
    UPDATE account_asset_category SET method_period = CASE WHEN temp_method_period = '1' THEN 1 ELSE 12 END;
    UPDATE mail_tracking_value SET new_value_integer = CASE WHEN new_value_char = 'Months' THEN 1 ELSE
    (CASE WHEN new_value_char = 'Years' THEN 12 END) END
    WHERE field = 'method_period' AND field_type = 'selection' AND field_desc = 'Number of Months in a Period';
    ALTER TABLE account_asset_asset DROP COLUMN temp_method_period;
    ALTER TABLE account_asset_category DROP COLUMN temp_method_period;
    """)

