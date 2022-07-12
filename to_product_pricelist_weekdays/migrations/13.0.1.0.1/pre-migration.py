from odoo import api, SUPERUSER_ID
from odoo.tools.sql import column_exists, create_column
from psycopg2.extensions import AsIs

COLUMNS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    weekday_column = column_exists(cr, 'product_pricelist_item', 'weekday')
    if weekday_column:
        # Create column
        for column in COLUMNS:
            if not column_exists(cr, 'product_pricelist_item', column):
                create_column(cr, 'product_pricelist_item', column, 'boolean')
        create_column(cr, 'product_pricelist_item', 'days_of_week', 'boolean')
        # Update data
        sql = """
        UPDATE product_pricelist_item
        SET %s = true, days_of_week = true WHERE weekday = %s;
        """
        for number, day in enumerate(COLUMNS):
            cr.execute(sql, (AsIs(day), str(number)))
