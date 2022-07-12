from odoo import models
import requests
import html2text
from odoo.exceptions import UserError

host = "https://graph.facebook.com"

class Message(models.Model):
    _inherit = 'mail.message'

    def _send_social_message_facebook(self, social_page, social_particiapant_id):
        page_access_token = social_page.facebook_page_access_token
        message = html2text.html2text(self.body)
        url = host + "/me/messages?access_token=%s"%(page_access_token)
        request_data = {
            "messaging_type": "MESSAGE_TAG",
            "tag": "ACCOUNT_UPDATE",
            "recipient": {
                "id": social_particiapant_id
                },
            "message": {
                "text": message
                }
            }
        try:
            req = requests.post(url,
                json=request_data)
            req.raise_for_status()
            data = req.json()
            if data.get('message_id', False):
                self.write({'social_message_id': data.get('message_id', False)})
        except requests.HTTPError:
            raise UserError("An error occurred")
