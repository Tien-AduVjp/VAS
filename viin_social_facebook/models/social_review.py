from odoo import models, fields
import requests
import datetime
from dateutil.parser import parse

HOST = "https://graph.facebook.com"

class SocialReview(models.Model):
    _name = 'social.review'
    _description = 'Social Review'
    _order = 'review_date desc'
    
    review_date = fields.Datetime(string='Review Date')
    message = fields.Text(string='Message')
    page_id = fields.Many2one('social.page', string='Page')

    def _get_all_reivews(self, page_id, social_page_id, access_token):
        url = HOST + '/%s?fields=ratings{open_graph_story,recommendation_type,has_review} &access_token=%s'%(social_page_id, access_token)
        req = requests.get(url)
        data = req.json()
        ratings = data.get('ratings', False)
        review_list = []
        if ratings:
            reviews = ratings.get('data', [])
            for review in reviews:
                open_graph_story = review.get('open_graph_story', False)
                if open_graph_story:
                    start_time = parse(open_graph_story['start_time'])
                    review_date = datetime.datetime.combine(start_time.date(), start_time.time())
                    review_list.append({'review_date': review_date,
                                        'message': open_graph_story['message'],
                                        'page_id': page_id
                                        })
        self._synchronize_all_reviews(review_list, page_id)

    def _synchronize_all_reviews(self, review_list, page_id):
        self.search([('page_id', '=', page_id)]).unlink()
        self.create(review_list)
