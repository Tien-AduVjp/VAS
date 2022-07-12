import random
from odoo import tools
 
# Setup test data compute total working amount.
DELTA_DAY = random.randint(1, 10)
UOM_UNIT_RATIO = random.uniform(1.0, 4.0)
START_AMOUNT = random.uniform(1.0, 1000.0)
WORKING_AMOUNT = random.uniform(10000.0, 14000.0)
PERIOD_TIME = random.randint(1, 7)
UOM_ROUNDING_DEFAULT = 0.01
UOM_ROUNDING_METHOD = "UP"
TOTAL_WORKING_AMOUNT = START_AMOUNT + DELTA_DAY * (WORKING_AMOUNT / tools.float_round(PERIOD_TIME / UOM_UNIT_RATIO, precision_rounding=UOM_ROUNDING_DEFAULT, rounding_method=UOM_ROUNDING_METHOD))

# Setup data test inverse total working amount.
PRE_TOTAL_WORKING_AMOUNT = random.uniform(10000.0, 14000.0)
INV_WORKING_AMOUNT = ((PRE_TOTAL_WORKING_AMOUNT - START_AMOUNT) / DELTA_DAY) * tools.float_round(PERIOD_TIME / UOM_UNIT_RATIO, precision_rounding=UOM_ROUNDING_DEFAULT, rounding_method=UOM_ROUNDING_METHOD)
