from psycopg2 import sql
from odoo import fields, models, tools


class FleetReport(models.Model):
    _inherit = 'fleet.vehicle.cost.report'

    cost_type_id = fields.Many2one('fleet.service.type', string='Service Type', readonly=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', readonly=True)
    quantity = fields.Float('Quantity', readonly=True)
    price_unit = fields.Float('Unit Price', readonly=True, group_operator='avg')
    
    def _service_select(self):
        return """
        ve.id AS vehicle_id,
        ve.company_id AS company_id,
        ve.name AS name,
        ve.driver_id AS driver_id,
        se.vendor_id as vendor_id,
        ve.fuel_type AS fuel_type,
        date(date_trunc('month', d)) AS date_start,
        COALESCE(sum(se.quantity), 0) AS quantity,
        COALESCE(avg(se.price_unit), 0) AS price_unit,
        COALESCE(sum(se.amount), 0) AS cost,
        'service' AS cost_type,
        se.service_type_id as cost_type_id"""
        
    def _service_from(self):
        return """
        fleet_vehicle ve
    CROSS JOIN generate_series((
            SELECT
                min(date)
                FROM fleet_vehicle_log_services), CURRENT_DATE + '1 month'::interval, '1 month') d
    LEFT JOIN fleet_vehicle_log_services se ON se.vehicle_id = ve.id
        AND date_trunc('month', se.date) = date_trunc('month', d)"""
            
    def _service_where(self):
        return """
        ve.active AND se.active AND se.state != 'cancelled'"""
        
    def _service_groupby(self):
        return """
        ve.id,
        ve.company_id,
        ve.name,
        date_start,
        d,
        se.vendor_id,
        se.service_type_id"""
        
    def _service_orderby(self):
        return """
        ve.id,
        date_start"""
    
    def _service_query(self):
        query = """
    SELECT %s
    FROM %s
    WHERE %s
    GROUP BY %s
    ORDER BY %s""" % (
            self._service_select(),
            self._service_from(),
            self._service_where(),
            self._service_groupby(),
            self._service_orderby()
        )
        return query
    
    def _contract_select(self):
        return """
        ve.id AS vehicle_id,
        ve.company_id AS company_id,
        ve.name AS name,
        ve.driver_id AS driver_id,
        COALESCE (co.insurer_id, cod.insurer_id, com.insurer_id, coy.insurer_id) as vendor_id,
        ve.fuel_type AS fuel_type,
        date(date_trunc('month', d)) AS date_start,
        count(co.vehicle_id) + count(cod.vehicle_id) + count(com.vehicle_id) + count(coy.vehicle_id) AS quantity,
        avg(COALESCE(co.cost_generated, cod.cost_generated, com.cost_generated, coy.cost_generated, 0)) AS price_unit,
        (COALESCE(sum(co.amount), 0) + COALESCE(sum(cod.cost_generated * extract(day FROM least (date_trunc('month', d) + interval '1 month', cod.expiration_date) - greatest (date_trunc('month', d), cod.start_date))), 0) + COALESCE(sum(com.cost_generated), 0) + COALESCE(sum(coy.cost_generated), 0)) AS cost,
        'contract' AS cost_type,
        COALESCE (co.cost_subtype_id, cod.cost_subtype_id, com.cost_subtype_id, coy.cost_subtype_id) as cost_type_id"""
        
    def _contract_from(self):
        return """
        fleet_vehicle ve
    CROSS JOIN generate_series((
            SELECT
                min(acquisition_date)
                FROM fleet_vehicle), CURRENT_DATE + '1 month'::interval, '1 month') d
    LEFT JOIN fleet_vehicle_log_contract co ON co.vehicle_id = ve.id
        AND date_trunc('month', co.date) = date_trunc('month', d)
    LEFT JOIN fleet_vehicle_log_contract cod ON cod.vehicle_id = ve.id
        AND date_trunc('month', cod.start_date) <= date_trunc('month', d)
        AND date_trunc('month', cod.expiration_date) >= date_trunc('month', d)
        AND cod.cost_frequency = 'daily'
    LEFT JOIN fleet_vehicle_log_contract com ON com.vehicle_id = ve.id
        AND date_trunc('month', com.start_date) <= date_trunc('month', d)
        AND date_trunc('month', com.expiration_date) >= date_trunc('month', d)
        AND com.cost_frequency = 'monthly'
    LEFT JOIN fleet_vehicle_log_contract coy ON coy.vehicle_id = ve.id
        AND date_trunc('month', coy.date) = date_trunc('month', d)
        AND date_trunc('month', coy.start_date) <= date_trunc('month', d)
        AND date_trunc('month', coy.expiration_date) >= date_trunc('month', d)
        AND coy.cost_frequency = 'yearly'"""
        
    def _contract_where(self):
        return """
        ve.active"""
        
    def _contract_groupby(self):
        return """
        ve.id,
        ve.company_id,
        ve.name,
        date_start,
        d,
        co.insurer_id,
        cod.insurer_id,
        com.insurer_id,
        coy.insurer_id,
        co.cost_subtype_id,
        cod.cost_subtype_id,
        com.cost_subtype_id,
        coy.cost_subtype_id"""
        
    def _contract_orderby(self):
        return """
        ve.id,
        date_start"""
    
    def _contract_query(self):
        query = """
    SELECT %s
    FROM %s
    WHERE %s
    GROUP BY %s
    ORDER BY %s""" % (
            self._contract_select(),
            self._contract_from(),
            self._contract_where(),
            self._contract_groupby(),
            self._contract_orderby()
       )
        return query
    
    def _service_costs_select(self):
        return """
    vehicle_id AS id,
    company_id,
    vehicle_id,
    name,
    driver_id,
    vendor_id,
    fuel_type,
    date_start,
    quantity,
    price_unit,
    cost,
    'service' as cost_type,
    cost_type_id"""
    
    def _contract_costs_select(self):
        return """
    vehicle_id AS id,
    company_id,
    vehicle_id,
    name,
    driver_id,
    vendor_id,
    fuel_type,
    date_start,
    quantity,
    price_unit,
    cost,
    'contract' as cost_type,
    cost_type_id"""
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
WITH
service_costs AS (%s),
contract_costs AS (%s)
SELECT %s
FROM service_costs
WHERE quantity <> 0
UNION ALL
SELECT %s
FROM contract_costs
WHERE quantity <> 0
        """ % (self._service_query(), self._contract_query(), self._service_costs_select(), self._contract_costs_select())
        self.env.cr.execute(
            sql.SQL("""CREATE or REPLACE VIEW {} as ({})""").format(
                sql.Identifier(self._table),
                sql.SQL(query)
            ))
