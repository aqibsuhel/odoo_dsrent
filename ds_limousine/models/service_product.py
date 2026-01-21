# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Limousine Service Specific
    is_limousine_service = fields.Boolean(string='Is Limousine Service', default=False)
    is_oil = fields.Boolean(string='Is Oil')
    is_expenses = fields.Boolean(string='Expenses?')
    can_be_rented = fields.Boolean(string='Can be Rented')
    is_gps = fields.Boolean(string='Is GPS')
    is_booking_service = fields.Boolean(string='Booking Service')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Inherited from template
    is_limousine_service = fields.Boolean(related='product_tmpl_id.is_limousine_service',
                                          readonly=False, store=True)