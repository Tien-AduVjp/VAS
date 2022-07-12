from odoo import api, http, models
import logging
import requests

_logger = logging.getLogger(__name__)


class WebsiteRecaptcha(models.AbstractModel):


    _name = 'website.recaptcha'
    _description = 'Website Recaptcha Validations'
    URL = 'https://www.google.com/recaptcha/api/siteverify'
    RESPONSE_ATTR = 'g-recaptcha-response'
    REQUEST_TOKEN = RESPONSE_ATTR.replace('-', '_')

    def _get_api_credentials(self, version='v2', website=None):
        website = website or http.request.website
        res = {
            'site_key': '',
            'secret_key': ''
        }
        if version == 'v2':
            res.update({
                'site_key': website.recaptcha_site_key,
                'secret_key': website.recaptcha_secret_key
            })
        elif version == 'v3':
            res.update({
                'site_key': website.recaptcha_site_key_v3,
                'secret_key': website.recaptcha_secret_key_v3,
                'score': website.recaptcha_score
            })
        return res

    @api.model
    def validate_response(self, response, remote_ip, recaptcha_version='v2', website=None):
        """ Validate ReCaptcha Response
        Params:
            response: str The value of 'g-recaptcha-response'.
            remote_ip: str The end user's IP address
        Raises:
            ValidationError on failure
        Returns:
            True on success
        """

        # @TODO: Domain validation
        # domain_name = request.httprequest.environ.get(
        #     'HTTP_HOST', ''
        # ).split(':')[0]
        credentials = self._get_api_credentials(recaptcha_version, website=website)
        data = {
            'secret': credentials['secret_key'],
            'response': response,
            'remoteip': remote_ip,
        }
        res = requests.post(self.URL, data=data).json()
        if not res.get('success'):
            return False
        if recaptcha_version == 'v3':
            if 'score' not in credentials or 'score' not in res or credentials['score'] > res['score']:
                return False
        return True

    @api.model
    def validate_request(self, request, values, recaptcha_version='v2'):
        already_validated = getattr(request, self.REQUEST_TOKEN, None)
        if already_validated is not None\
            or not values.get('login', True)\
            or not values.get('password', True):
            # Only check once: if a call to reCAPTCHA's API is made twice with
            # the same token, we get a 'timeout-or-duplicate' error. So we
            # stick to the first response data storing the token after the
            # first invoke in the current request object. This duplicated
            # call can be cause for instance by website_crm_phone_validation.
            return True
        req_value = values.get(self.RESPONSE_ATTR)
        if not req_value:
            return False
        remote_ip = request.httprequest.environ.get('HTTP_X_FORWARDED_FOR')
        if remote_ip:
            remote_ip = remote_ip.split(',')[0]
        else:
            remote_ip = request.httprequest.remote_addr
        # if not validated an exception is raised anyway
        validated = self.validate_response(req_value, remote_ip, recaptcha_version)
        # Store reCAPTCHA's token in the current request object
        setattr(request, self.REQUEST_TOKEN, req_value)
        return validated
