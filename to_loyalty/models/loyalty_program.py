import math

from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class LoyaltyProgram(models.Model):
    _name = 'loyalty.program'
    _inherit = ['mail.thread']
    _description = 'Loyalty Program'

    name = fields.Char(string='Name', index=True, required=True,
                       help="An internal identification for the loyalty program configuration", tracking=True)
    pp_currency = fields.Float(string='Points per currency',
                               help="How many loyalty points are given to the customer by sold currency.\n"
                               "Note: these points are won only if all of the matched rules is marked as Commulative.",
                               digits='Loyalty', tracking=True)
    pp_product = fields.Float(string='Points per product', tracking=True,
                              digits='Loyalty',
                              help="How many loyalty points are given to the customer by a quantity of product sold.\n"
                              "Note: these points are won only if all of the matched rules is marked as Commulative.")
    pp_order = fields.Float(string='Points per order', digits='Loyalty', tracking=True,
                            help="How many loyalty points are given to the customer for each sale or order")
    rounding = fields.Float(string='Points Rounding', default=0.000001, digits='Loyalty', required=True, tracking=True,
                            help="The loyalty point amounts are rounded to multiples of this value.")
    rule_ids = fields.One2many('loyalty.rule', 'loyalty_program_id', string='Rules', tracking=True)
    reward_ids = fields.One2many('loyalty.reward', 'loyalty_program_id', string='Rewards', tracking=True, help="The rewards to be given to the"
                                 " customer")
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id, required=True)
    team_ids = fields.One2many('crm.team', 'loyalty_id', string='Sales Channels', help="The sales teams / channels that will use this loyalty program")

    _sql_constraints = [
        ('positive_rounding_check',
         'CHECK(rounding > 0)',
         "The Points Rounding must be strictly positive!"),
    ]

    def _calculate_precision(self):
        self.ensure_one()
        return int(math.ceil(math.log10(1 / self.rounding)))

    def calculate_won_points(self, company_id, product_id, product_qty, price_subtotal, product_uom=None, currency_id=None, date=None):
        """
        calculate won points
        @param company_id: the company for which the order is
        @param product_id:
        @param product_qty:  
        @param price_subtotal: 
        @param product_uom: if passed, the passed product quantity is in this UoM. Hence, it will be converted to the default product UoM
        @param currency_id: if passed, it is to indicated that the price_subtotal is in that currency. Otherwise, it will be considered as the company currency. 
        @param date: the date for currency rate conversion. If not passed, the current date will be used
        @return: won points
        @rtype: float
        """

        self.ensure_one()

        product_sold = 0
        total_sold = 0
        total_points = 0
        # prec = self._calculate_precision()

        # prefeching for better perfomance
        self.rule_ids.read(['product_id', 'product_category_id', 'pp_product', 'pp_currency', 'cumulative'])

        rules = self.rule_ids.filtered(lambda r: r.product_id == product_id)
        overriden = False

        if product_uom:
            product_qty = product_uom._compute_quantity(product_qty, product_id.uom_id)

        ordering_currency = currency_id or company_id.currency_id
        loyalty_program_currency = self.currency_id or company_id.currency_id

        # price_subtotal conversion from from_currency to to_currency
        if ordering_currency != loyalty_program_currency:
            price_subtotal = ordering_currency._convert(price_subtotal, loyalty_program_currency, company_id, date or fields.Datetime.now())

        for rule in rules:
            total_points += float_round(product_qty * rule.pp_product, precision_rounding=self.rounding)
            total_points += float_round(price_subtotal * rule.pp_currency, precision_rounding=self.rounding)
            # if affected by a non cumulative rule, skip the others. (non cumulative rules are put
            # at the beginning of the list when they are loaded)
            if not rule.cumulative:
                overriden = True
                break

        # Test the category rules
        if product_id.categ_id:
            category = product_id.categ_id
            while (category and not overriden):
                rules = self.rule_ids.filtered(lambda r: r.product_category_id == category)
                for rule in rules:
                    total_points += float_round(product_qty * rule.pp_product, precision_rounding=self.rounding)
                    total_points += float_round(price_subtotal * rule.pp_currency, precision_rounding=self.rounding)
                    if not rule.cumulative:
                        overriden = True
                        break
                if not category.parent_id:
                    break
                category = category.parent_id

        if not overriden:
            product_sold = product_qty
            total_sold = price_subtotal

        total_points += float_round(total_sold * self.pp_currency, precision_rounding=self.rounding)
        total_points += float_round(product_sold * self.pp_product, precision_rounding=self.rounding)

        return total_points

    def calculate_spent_points(self, company_id, product_id, product_qty, price_subtotal, reward_id, product_uom=None, currency_id=None, date=None):
        self.ensure_one()
        if reward_id.loyalty_program_id and reward_id.loyalty_program_id.id != self.id:
            raise ValidationError(_("Invalid reward '%s'. The reward must either a global reward or belong the the program '%s'")
                                  % (reward_id.name, self.name))
        points = 0.0
        # prec = self._calculate_precision()

        if product_uom:
            product_qty = product_uom._compute_quantity(product_qty, product_id.uom_id)

        # if currency_id is not passed, the from_currency will be the company's currency
        ordering_currency = currency_id or company_id.currency_id
        # the currency to convert to, which is either the loyalty program's currency or the company's currency whichever comes first
        loyalty_program_currency = self.currency_id or company_id.currency_id
        # price_subtotal conversion from from_currency to to_currency
        if ordering_currency != loyalty_program_currency:
            price_subtotal = ordering_currency._convert(price_subtotal, loyalty_program_currency, company_id, date or fields.Datetime.now())

        if reward_id.reward_type == 'gift':
            points += float_round(product_qty * reward_id.point_cost, precision_rounding=self.rounding)
        elif reward_id.reward_type == 'discount':
            points += float_round(-price_subtotal * reward_id.point_cost, precision_rounding=self.rounding)

        return points

    def find_loyalty_program(self, partner_id=None, team_id=None):
        """
        Find loyalty program for the partner and team where the partner is in priority
        """
        loyalty_id = False
        if partner_id and team_id:
            loyalty_id = partner_id.find_loyalty_program() or team_id.find_loyalty_program()
        elif partner_id:
            loyalty_id = partner_id.find_loyalty_program()
        elif team_id:
            loyalty_id = team_id.find_loyalty_program()
        return loyalty_id
