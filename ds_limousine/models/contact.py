# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Limousine Specific Fields
    is_limousine_customer = fields.Boolean(string='Is Limousine Customer', default=False)
    business_type = fields.Selection([
        ('corporate', 'Corporate'),
        ('hotels', 'Hotels'),
        ('government', 'Government'),
        ('individuals', 'Individuals'),
        ('driver', 'Driver'),
        ('rental', 'Rental'),
        ('others', 'Others'),
    ], string='Business Type')

    # Saudi Arabia Specific Fields
    national_id = fields.Char(string='National Identity Number')
    id_type = fields.Selection([
        ('national', 'National'),
        ('resident', 'Resident'),
        ('visitor', 'Visitor'),
        ('gcc', 'Citizens of the GCC'),
    ], string='ID Type Code')

    id_issue_date = fields.Date(string='ID Issue Date')
    id_expiry_date = fields.Date(string='ID Expiry Date')
    id_version_number = fields.Char(string='ID Version Number')

    # Driver License Information
    license_number = fields.Char(string='License Number')
    license_expiry_date = fields.Date(string='License Expiry Date')

    # Commercial Information
    commercial_register = fields.Char(string='Commercial Register')
    governmental_number = fields.Char(string='Governmental Number')
    passport_number = fields.Char(string='Passport Number')

    # Additional Information
    date_of_birth = fields.Date(string='Date of Birth')
    nationality = fields.Many2one('res.country', string='Nationality')

    # Driver Specific
    is_driver = fields.Boolean(string='Is Driver', default=False)
    driver_type = fields.Selection([
        ('internal', 'Internal Driver'),
        ('external', 'External Driver'),
        ('shipping', 'Shipping Company'),
    ], string='Driver Type')

    # Limousine Bookings
    limousine_booking_ids = fields.One2many('limousine.booking', 'customer_id',
                                            string='Limousine Bookings')
    limousine_booking_count = fields.Integer(string='Booking Count',
                                             compute='_compute_limousine_booking_count')

    @api.depends('limousine_booking_ids')
    def _compute_limousine_booking_count(self):
        for partner in self:
            partner.limousine_booking_count = len(partner.limousine_booking_ids)

    def action_view_limousine_bookings(self):
        return {
            'name': 'Limousine Bookings',
            'type': 'ir.actions.act_window',
            'res_model': 'limousine.booking',
            'view_mode': 'list,form',
            'domain': [('customer_id', '=', self.id)],
            'context': {'default_customer_id': self.id},
        }