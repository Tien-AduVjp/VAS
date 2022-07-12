from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    pos_session_id = fields.Many2one('pos.session', string='PoS Session', readonly=True)
    pos_config_id = fields.Many2one('pos.config', string='PoS', readonly=True)
    pos_session_user_id = fields.Many2one('res.users', string='PoS Session Responsible', readonly=True)
    

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
                       
        fields = {""" pos_session_id,NULL AS pos_config_id,NULL AS pos_session_user_id""":""",
                    s.pos_session_id AS pos_session_id,
                    pconf.id AS pos_config_id,
                    pos_u.id AS pos_session_user_id
        """}
                     
        groupby = """,
                    s.pos_session_id,
                    pconf.id,
                    pos_u.id
        """
        
        from_clause = """
            LEFT JOIN pos_session AS psess ON psess.id = s.pos_session_id
            LEFT JOIN pos_config AS pconf ON pconf.id = psess.config_id
            LEFT JOIN res_users AS pos_u ON pos_u.id = psess.user_id
        """

        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)