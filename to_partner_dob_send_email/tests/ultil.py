from odoo import fields
import datetime,random

def generate_random_birthday():
    yob = random.randint(1945,2021)
    today = datetime.date.today()
    return fields.Date.to_date('%s-%s-%s' % (yob,today.month,today.day))
