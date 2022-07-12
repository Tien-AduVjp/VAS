from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    severity_level = fields.Selection([
        ('critical', 'Critical'),
        ('major', 'Major'),
        ('minor', 'Minor/Medium'),
        ('low', 'Low')
        ], string='Severity', tracking=True, default='low',
        help="Severity defines the extent to which a particular defect could create an impact on the application or system.\n"
        "* Critical: A defect that completely hampers or blocks testing of the product/ feature is a critical defect. An example would"
        " be in the case of UI testing where after going through a wizard, the UI just hangs in one pane or doesn’t go further"
        " to trigger the function. Or in some other cases, when the feature developed itself is missing from the build.\n"
        "* Major: Any major feature implemented that is not meeting its requirements/use case(s) and behaves differently than expected."
        " A major defect occurs when the functionality is functioning grossly away from the expectations or not doing what it should be doing.\n"
        "* Minor/Medium: Any feature implemented that is not meeting its requirements/use case(s) and behaves differently than expected"
        " but the impact is negligible to some extent or it doesn’t have a major impact on the application. A moderate defect occurs when"
        " the product or application doesn’t meet certain criteria or still exhibits some unnatural behavior, however, the functionality"
        " as a whole is not impacted.\n"
        "* Low: Any cosmetic defects including spelling mistakes or alignment issues or font casing can be classified under Low Severity."
        " A minor low severity bug occurs when there is almost no impact on the functionality but it is still a valid defect that should"
        " be corrected.")

