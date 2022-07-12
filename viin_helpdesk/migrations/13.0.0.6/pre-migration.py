from odoo import api, SUPERUSER_ID, tools


def _update_priority_level_on_ticket():
    return """
    ALTER TABLE helpdesk_ticket ADD temp_priority_level character varying(64);
    UPDATE helpdesk_ticket SET temp_priority_level = priority_level;
    UPDATE helpdesk_ticket SET priority_level =
        CASE WHEN temp_priority_level = 'low' THEN '1'
            ELSE
                CASE WHEN temp_priority_level = 'high' THEN '2'
            ELSE
                CASE WHEN temp_priority_level = 'urgent' THEN '3' ELSE '0'
                END
            END
        END;
    ALTER TABLE helpdesk_ticket DROP COLUMN temp_priority_level;
    """

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    env['ir.model.fields'].search([('model', '=', 'report.helpdesk.ticket'),
                                   ('name', '=', 'priority_level')], limit=1) \
                          .with_context(_force_unlink=True).unlink()
    cr.execute(_update_priority_level_on_ticket())
