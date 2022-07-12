from odoo import models, fields, api


class Website(models.Model):
    _inherit = 'website'

    gtm_enable = fields.Boolean(string='Enable Google Tag Manager')
    gtm_container_id = fields.Char(string='Google Tag Manager Container ID', help="Example: GTM-XXXX")
    gtm_script = fields.Text(string='Google Tag Manager Script', compute='_compute_gmt_script')
    gtm_noscript = fields.Text(string='Google Tag Manager NoScript', compute='_compute_gmt_script')

    @api.depends('gtm_container_id')
    def _compute_gmt_script(self):
        for r in self:
            if r.gtm_container_id:
                r.gtm_script = """
                    <!-- Google Tag Manager -->
                    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
                    new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
                    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
                    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
                    })(window,document,'script','dataLayer','%s');</script>
                    <!-- End Google Tag Manager -->
                """ % r.gtm_container_id
                r.gtm_noscript = """
                    <!-- Google Tag Manager (noscript) -->
                    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=%s"
                    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
                    <!-- End Google Tag Manager (noscript) -->
                """ % r.gtm_container_id
            else:
                r.gtm_script = False
                r.gtm_noscript = False
