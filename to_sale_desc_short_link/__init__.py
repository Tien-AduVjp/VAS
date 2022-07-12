from . import models

from odoo import tools
#adding symbol "&" to TEXT_URL_REGEX
#odoo TEXT_URL_REGEX = r'https?://[a-zA-Z0-9@:%._\+~#=/-]+(?:\?\S+)?'
tools.TEXT_URL_REGEX = r'https?://[a-zA-Z0-9@:%._\+~#=/&-]+(?:\?\S+)?'
