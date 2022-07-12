# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _create_account_invoice_fleet_vehicle_trip_vendor_rel_table(cr):
    query = """CREATE TABLE IF NOT EXISTS "{rel}" (
        fleet_vehicle_trip_id integer NOT NULL,
        account_invoice_id integer NOT NULL,
        UNIQUE(fleet_vehicle_trip_id, account_invoice_id));
        COMMENT ON TABLE "{rel}" IS 'RELATION BETWEEN account_invoice AND fleet_vehicle_trip';
        CREATE INDEX ON "{rel}" (fleet_vehicle_trip_id);
        CREATE INDEX ON "{rel}" (account_invoice_id);""" \
        .format(rel='account_invoice_fleet_vehicle_trip_vendor_rel', id1='fleet_vehicle_trip_id', id2='account_invoice_id')
    cr.execute(query)


def _update_account_invoice_fleet_vehicle_trip_vendor_rel(cr):
    #Update link between vendor invoice and fleet_vehicle_trip
    cr.execute("""
        WITH tmp_fleet_vehicle_cost AS (
            SELECT id, trip_id, invoice_id
            FROM fleet_vehicle_cost
            WHERE invoice_line_id > 0 AND trip_id > 0
            )
        INSERT INTO account_invoice_fleet_vehicle_trip_vendor_rel (fleet_vehicle_trip_id, account_invoice_id)
        SELECT trip_id, invoice_id FROM tmp_fleet_vehicle_cost
        ON CONFLICT (fleet_vehicle_trip_id, account_invoice_id) DO NOTHING;
    """)

    #Update vendor_invoices_count
    cr.execute("""
        WITH tmp_fleet_vehicle_cost AS (
            SELECT id, trip_id, invoice_id
            FROM fleet_vehicle_cost
            WHERE invoice_line_id > 0 AND trip_id > 0
            )
        UPDATE fleet_vehicle_trip
        SET vendor_invoices_count = (SELECT COUNT (trip_id) FROM tmp_fleet_vehicle_cost AS cost WHERE cost.trip_id = fleet_vehicle_trip.id);
    """)


def migrate(cr, version):
    _create_account_invoice_fleet_vehicle_trip_vendor_rel_table(cr)
    _update_account_invoice_fleet_vehicle_trip_vendor_rel(cr)

