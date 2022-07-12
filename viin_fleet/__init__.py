from . import models
from . import reports


def post_init_hook(cr, registry):
    cr.execute("""
        UPDATE fleet_vehicle_log_services SET price_unit = amount;
    """)
