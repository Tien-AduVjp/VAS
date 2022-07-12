from odoo import api, SUPERUSER_ID


def update_classes(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    xml_ids_map = {
        'truck_2_4_tons': 'vehicle_type_truck',
        'truck_4_10_tons': 'vehicle_type_truck',
        'truck_10_18_tons': 'vehicle_type_truck',
        'truck_over_18_tons': 'vehicle_type_truck',
        'bus_13_29_seats': 'vehicle_type_bus',
        'sedan_5_seats': 'vehicle_type_car',
        }
    vehicle_class_ids = env['vehicle.class']
    for k, v in xml_ids_map.items():

        vehicle_class_id = env.ref('to_fleet_specs.%s' % k)
        vehicle_type_id = env.ref('to_fleet_specs.%s' % v)
        vehicle_class_id.write({
            'type_id': vehicle_type_id.id
            })
        vehicle_class_ids += vehicle_class_id

    types = ['vehicle_type_truck', 'vehicle_type_bus', 'vehicle_type_car']

    type_id = env.ref('to_fleet_specs.vehicle_type_truck')
    cr.execute("""
    UPDATE vehicle_class SET type_id = %s
    WHERE id NOT IN %s
        AND legacy_type = 'truck'
    """, (type_id.id, tuple(vehicle_class_ids.ids)))

    type_id = env.ref('to_fleet_specs.vehicle_type_bus')
    cr.execute("""
    UPDATE vehicle_class SET type_id = %s
    WHERE id NOT IN %s
        AND legacy_type = 'bus'
    """, (type_id.id, tuple(vehicle_class_ids.ids)))

    type_id = env.ref('to_fleet_specs.vehicle_type_car')
    cr.execute("""
    UPDATE vehicle_class SET type_id = %s
    WHERE id NOT IN %s
        AND legacy_type = 'car'
    """, (type_id.id, tuple(vehicle_class_ids.ids)))

    return vehicle_class_ids


def drop_legacy(cr):
    cr.execute("""
    ALTER TABLE vehicle_class DROP COLUMN legacy_type;
    """)


def migrate(cr, version):

    update_classes(cr)
    drop_legacy(cr)

