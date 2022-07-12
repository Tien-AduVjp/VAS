from odoo import models
import requests

shares = "https://api.linkedin.com/v2/shares"

class SocialPostActionEditPost(models.TransientModel):
    _inherit = 'social.post.action.edit.post'

    def action_confirm_edit(self):
        self.ensure_one()
        Post = self.post_id
        if Post.media_id.social_provider == 'linkedin':
            url = shares + "/%s?oauth2_access_token=%s"%(Post.social_post_id, Post.media_id.linkedin_access_token)
            data ={"patch": {
                        "$set": {
                            "text": {
                                "annotations": [],
                                "text": self.message
                            }
                        }
                    }
                }
            req = requests.post(url, json=data)
            req.raise_for_status()
            Post.write({'message': self.message})
        else:
            return super(SocialPostActionEditPost, self).action_confirm_edit()
