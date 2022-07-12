# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _create_account_invoice_fleet_vehicle_trip_customer_rel_table(cr):
    query = """CREATE TABLE IF NOT EXISTS "{rel}" (
        fleet_vehicle_trip_id integer NOT NULL,
        account_invoice_id integer NOT NULL,
        UNIQUE(fleet_vehicle_trip_id, account_invoice_id));
        COMMENT ON TABLE "{rel}" IS 'RELATION BETWEEN account_invoice AND fleet_vehicle_trip';
        CREATE INDEX ON "{rel}" (fleet_vehicle_trip_id);
        CREATE INDEX ON "{rel}" (account_invoice_id);""" \
        .format(rel='account_invoice_fleet_vehicle_trip_customer_rel', id1='fleet_vehicle_trip_id', id2='account_invoice_id')
    cr.execute(query)


def account_invoice_fleet_vehicle_trip_customer_rel(cr):
    #Update link between customer invoice and fleet_vehicle_trip
    cr.execute("""
        WITH tmp_fleet_vehicle_revenue AS (
            SELECT id, trip_id, invoice_id
            FROM fleet_vehicle_revenue
            WHERE invoice_line_id > 0 AND trip_id > 0
            )
        INSERT INTO account_invoice_fleet_vehicle_trip_customer_rel (fleet_vehicle_trip_id, account_invoice_id) 
        SELECT trip_id, invoice_id FROM tmp_fleet_vehicle_revenue 
        ON CONFLICT (fleet_vehicle_trip_id, account_invoice_id) DO NOTHING;
    """)
    
    #Update customer_invoices_count
    cr.execute("""
        WITH tmp_fleet_vehicle_revenue AS (
            SELECT id, trip_id, invoice_id
            FROM fleet_vehicle_revenue
            WHERE invoice_line_id > 0 AND trip_id > 0
            )
        UPDATE fleet_vehicle_trip 
        SET customer_invoices_count = (SELECT COUNT (trip_id) FROM tmp_fleet_vehicle_revenue AS revenue WHERE revenue.trip_id = fleet_vehicle_trip.id);
        DROP TABLE IF EXISTS account_invoice_fleet_vehicle_trip_rel;
    """)


def migrate(cr, version):
    _create_account_invoice_fleet_vehicle_trip_customer_rel_table(cr)
    account_invoice_fleet_vehicle_trip_customer_rel(cr)

