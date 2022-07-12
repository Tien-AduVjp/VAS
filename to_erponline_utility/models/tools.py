from odoo.tools import config

section = config.misc.get('saaslimits', {})

def get_saas_subscription_type():
    subscription_type = section.get('subscription_type', 'plan')
    return subscription_type

def get_subscription_is_trial():
    return section.get('is_trial', False)
