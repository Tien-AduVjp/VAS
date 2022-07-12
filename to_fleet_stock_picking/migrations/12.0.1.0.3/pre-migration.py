# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _adding_new_trip_fields(cr):
    sql = ""

    # Adding trip_id
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_move' and column_name='trip_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE stock_move ADD COLUMN trip_id integer;
        """

    # adding vehicle_id
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_move' and column_name='vehicle_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE stock_move ADD COLUMN vehicle_id integer;
        """

    # adding driver_id
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_move' and column_name='driver_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE stock_move ADD COLUMN driver_id integer;
        """

    if sql:
        cr.execute(sql)


def _set_new_trip_fields_vals(cr):
    cr.execute("""
    UPDATE stock_move AS sm
    SET trip_id = sp.trip_id,
        vehicle_id = fvt.vehicle_id,
        driver_id = fvt.driver_id
    FROM stock_picking AS sp
        JOIN fleet_vehicle_trip AS fvt ON fvt.id = sp.trip_id
        WHERE sp.id = sm.picking_id;
    """)


def migrate(cr, version):
    _adding_new_trip_fields(cr)
    _set_new_trip_fields_vals(cr)
