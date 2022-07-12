from . import controllers
from . import models
from . import report
from . import wizard


def post_init_hook(cr, registry):
    """
    This method cleans up the name and the default_code to help auto module discovery later
    """
    cr.execute("""
    UPDATE product_template SET default_code = TRIM(default_code), name = TRIM(name);
    UPDATE product_product SET default_code = TRIM(default_code);
    """)
