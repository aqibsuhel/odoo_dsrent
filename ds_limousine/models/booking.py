# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LimousineBooking(models.Model):
    _name = 'limousine.booking'
    _description = 'Limousine Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'booking_date desc, id desc'

    name = fields.Char(string='Booking Reference', required=True, copy=False,
                       readonly=True, default='New', tracking=True)

    # Booking Type
    booking_type = fields.Selection([
        ('limousine', 'Car with Driver (Limousine)'),
        ('transfer', 'Transfer Service'),
        ('hourly', 'Hourly Service'),
        ('daily', 'Daily Service'),
    ], string='Type of Booking', default='limousine', required=True, tracking=True)

    # Customer Information
    customer_id = fields.Many2one('res.partner', string='Customer Name', required=True,
                                  tracking=True, domain=[('is_limousine_customer', '=', True)])
    customer_ref_number = fields.Char(string='Customer Ref Number', tracking=True)
    customer_mobile = fields.Char(string='Customer Mobile', related='customer_id.phone',
                                  readonly=True)

    # Business Type
    business_type = fields.Selection([
        ('government', 'Government'),
        ('corporate', 'Corporate'),
        ('hotels', 'Hotels'),
        ('individuals', 'Individuals'),
        ('rentals', 'Rentals'),
        ('others', 'Others'),
    ], string='Business Type', required=True, tracking=True)

    # Location Information
    region_id = fields.Many2one('limousine.region', string='Region', required=True, tracking=True)
    city_id = fields.Many2one('limousine.city', string='City', required=True, tracking=True,
                              domain="[('region_id', '=', region_id)]")
    branch_id = fields.Many2one('limousine.branch', string='Branch', tracking=True,
                                domain="[('city_id', '=', city_id)]")

    # Booking Date
    booking_date = fields.Datetime(string='Date of Booking', required=True,
                                   default=fields.Datetime.now, tracking=True)

    # Payment Terms
    payment_terms = fields.Selection([
        ('cash', 'Cash'),
        ('credit', 'Credit'),
        ('invoice', 'Invoice'),
        ('prepaid', 'Prepaid'),
    ], string='Payment Terms', tracking=True)

    # Contact & Hotel Information
    contact_hotel = fields.Char(string='Contact & Hotel')
    guest_name = fields.Char(string='Guest Name')
    guest_phone = fields.Char(string='Guest Phone')
    hotel_room_number = fields.Char(string='Hotel Room Number')

    # Flight Information
    flight_number = fields.Char(string='Flight Number')
    airport_id = fields.Many2one('limousine.airport', string='Airport',
                                 domain="[('city_id', '=', city_id)]")

    # Service Information
    service_line_ids = fields.One2many('limousine.booking.service.line', 'booking_id',
                                       string='Service Lines')

    # Backward compatibility - computed field from service lines
    service_product_ids = fields.Many2many('product.product', string='Services (Deprecated)',
                                           compute='_compute_service_products', store=False)

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    # Pricing
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount',
                                store=True, tracking=True)

    # Notes
    notes = fields.Text(string='Notes')

    # Attachments (handled by mail.thread)
    attachment_count = fields.Integer(string='Attachments', compute='_compute_attachment_count')

    # Company
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.model
    def create(self, vals_list):
        if not isinstance(vals_list, list):
            vals_list = [vals_list]

        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('limousine.booking') or 'New'

        return super(LimousineBooking, self).create(vals_list)

    @api.depends('service_line_ids', 'service_line_ids.total')
    def _compute_total_amount(self):
        for booking in self:
            booking.total_amount = sum(booking.service_line_ids.mapped('total'))

    def _compute_service_products(self):
        # Backward compatibility - get products from service lines
        for booking in self:
            booking.service_product_ids = booking.service_line_ids.mapped('service_id')

    def _compute_attachment_count(self):
        for booking in self:
            booking.attachment_count = self.env['ir.attachment'].search_count([
                ('res_model', '=', 'limousine.booking'),
                ('res_id', '=', booking.id)
            ])

    @api.onchange('region_id')
    def _onchange_region_id(self):
        if self.region_id:
            self.city_id = False
            self.branch_id = False

    @api.onchange('city_id')
    def _onchange_city_id(self):
        if self.city_id:
            self.branch_id = False
            self.airport_id = False

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_view_attachments(self):
        return {
            'name': 'Attachments',
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'list,form',
            'domain': [('res_model', '=', 'limousine.booking'), ('res_id', '=', self.id)],
            'context': {'default_res_model': 'limousine.booking', 'default_res_id': self.id},
        }