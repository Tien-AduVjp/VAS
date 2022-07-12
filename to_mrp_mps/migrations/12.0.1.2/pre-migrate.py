from odoo import api, fields, SUPERUSER_ID
from odoo.tools.sql import column_exists, create_column, add_foreign_key

COLUMNS_DICT = {
    'mps_forecasted': 'double precision',
    'mps_min_supply': 'double precision',
    'mps_max_supply': 'double precision',
    'mps_apply': 'timestamp',
    'apply_active': 'boolean',
}
COLUMNS = list(COLUMNS_DICT.keys())


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    migrate_columns_from_product_product(cr, env)
    set_default_warehouse_id_columns(cr, env)

def migrate_columns_from_product_product(cr, env):
    """ Create missing columns and move data from 'product_product' to 'mrp_mps_report' """
    # Clear old transient data
    cr.execute("delete from mrp_mps_report where 1 = 1")

    # Create columns to pre-fill data
    for column, type in COLUMNS_DICT.items():
        if not column_exists(cr, 'mrp_mps_report', column):
            create_column(cr, 'mrp_mps_report', column, type, 'MPS Report')
    create_column(cr, 'mrp_mps_report', 'warehouse_id', 'integer', 'MPS Report')
    add_foreign_key(cr, 'mrp_mps_report', 'warehouse_id', 'stock_warehouse', 'id', 'cascade')

    # Prepare data to migrate
    cr.execute("""select pp.id as product_id, pt.company_id, %s
                  from product_product pp
                  join product_template pt on pp.product_tmpl_id = pt.id
                  where pp.mps_active = true;""" % ', '.join(COLUMNS))
    mps_data = cr.dictfetchall()
    warehouse_company_data = _get_warehouses_and_companies_data(cr)

    for data in mps_data:
        if data['company_id']:
            warehouse_id = warehouse_company_data.get(data['company_id'], False)
            _add_record_mrp_mps_report(cr, data['company_id'], warehouse_id, data)
        else:  # If product is multi-companies, we should add a record for each company
            for company_id in env['res.company'].search([]).ids:
                warehouse_id = warehouse_company_data.get(company_id, False)
                _add_record_mrp_mps_report(cr, company_id, warehouse_id, data)

def set_default_warehouse_id_columns(cr, env):
    """ Set default value for 'warehouse_id' columns if value is missing
        at 'mrp_mps_report', 'sale_forecast' and 'sale_forecast_indirect' tables
    """
    product_company_data = _get_products_and_companies_data(cr)
    warehouse_company_data = _get_warehouses_and_companies_data(cr)
    for company_id, product_ids in product_company_data.items():
        # For multi-companies products, assign corresponding
        # forecasts and indirect forecasts to the main company only
        if not company_id:
            company_id = env.ref('base.main_company').id
        warehouse_id = warehouse_company_data.get(company_id, False)
        if warehouse_id:
            cr.execute("""update sale_forecast
                          set warehouse_id = %s
                          where warehouse_id is null and product_id in %s;""", (warehouse_id, tuple(product_ids)))
            cr.execute("""update sale_forecast_indirect
                          set warehouse_id = %s
                          where warehouse_id is null and product_id in %s;""", (warehouse_id, tuple(product_ids)))

def _add_record_mrp_mps_report(cr, company_id, warehouse_id, data):
    if not company_id or not warehouse_id:
        return
    missing_columns = [
        'company_id',
        'period',
        'product_id',
        'create_uid',
        'create_date',
        'write_uid',
        'write_date',
        'warehouse_id'
    ]
    columns = missing_columns + COLUMNS

    now = fields.Datetime.now()
    company_period_data = _get_companies_period_data(cr)
    missing_params = [
        company_id,
        company_period_data.get(company_id) or 'month',
        data['product_id'],
        SUPERUSER_ID,
        now,
        SUPERUSER_ID,
        now,
        warehouse_id
    ]
    params = missing_params + [data[column] for column in COLUMNS]

    query = "insert into mrp_mps_report(%s) values (%s);" % (', '.join(columns), ', '.join(['%s'] * len(params)))
    cr.execute(query, params)

def _get_companies_period_data(cr):
    cr.execute("select id, manufacturing_period from res_company;")
    data = cr.fetchall()
    return dict(data)

def _get_products_and_companies_data(cr):
    cr.execute("""select pt.company_id, array_agg(pp.id)
                  from product_product pp
                  join product_template pt on pp.product_tmpl_id = pt.id
                  group by pt.company_id;""")
    data = cr.fetchall()
    return dict(data)

def _get_warehouses_and_companies_data(cr):
    cr.execute("select company_id, min(id) from stock_warehouse group by company_id;")
    data = cr.fetchall()
    return dict(data)
