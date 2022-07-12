# -*- coding: utf-8 -*-

from odoo import exceptions


class InvalidInput(exceptions.UserError):
    """
    Exception object that is intended to be used in case of invalid input/arg found
    """

    def __init__(self, msg):
        super(InvalidInput, self).__init__(msg)

