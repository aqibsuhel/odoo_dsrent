from odoo import models, fields, api
from datetime import datetime


class LimousineBookingServiceLine(models.Model):
    _name = 'limousine.booking.service.line'
    _description = 'Limousine Booking Service Line'
    _order = 'sequence, id'

    # Basic Information
    sequence = fields.Integer(string='Sr. No.', default=10)
    booking_id = fields.Many2one('limousine.booking', string='Booking', required=True, ondelete='cascade')
    service_id = fields.Many2one('product.product', string='Service',
                                 domain=[('is_limousine_service', '=', True)])

    # Vehicle Information - UPDATED: Now a Many2one to ds.vehicle
    vehicle_id = fields.Many2one('ds.vehicle', string='Vehicle',
                                 domain=[('status', '=', 'available')],
                                 help='Select vehicle from Car Rental fleet')

    # Vehicle Details (Computed from selected vehicle)
    vehicle_brand = fields.Char(string='Brand', related='vehicle_id.brand', store=True, readonly=True)
    vehicle_model = fields.Char(string='Model', related='vehicle_id.model', store=True, readonly=True)
    vehicle_year = fields.Integer(string='Year', related='vehicle_id.year', store=True, readonly=True)
    vehicle_registration = fields.Char(string='Registration', related='vehicle_id.registration_number',
                                       store=True, readonly=True)
    vehicle_color = fields.Char(string='Color', related='vehicle_id.color', store=True, readonly=True)
    vehicle_seats = fields.Integer(string='Seats', related='vehicle_id.seats', store=True, readonly=True)

    # Manual car model entry (for cases where vehicle not in system)
    car_model_manual = fields.Char(string='Car Model (Manual)',
                                   help='Use this if vehicle is not in the system')

    # Display field that shows either vehicle or manual entry
    car_model_display = fields.Char(string='Car Model', compute='_compute_car_model_display', store=True)

    # Date and Time
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)

    # Hours Calculation
    total_hours = fields.Float(string='Total Hours', compute='_compute_hours', store=True)
    duration = fields.Float(string='Duration (Hours)', help='Contracted hours')
    extra_hours = fields.Float(string='Extra Hours', compute='_compute_extra_hours', store=True)

    # Pricing - with automatic population from vehicle
    unit_price = fields.Float(string='Rate/Hour', digits='Product Price')
    quantity = fields.Float(string='Quantity', default=1.0)
    misc_charges = fields.Float(string='Misc Charges')

    # Suggested rates from vehicle (for reference)
    suggested_daily_rate = fields.Float(string='Suggested Daily Rate',
                                        related='vehicle_id.daily_rate', readonly=True)
    suggested_hourly_rate = fields.Float(string='Suggested Hourly Rate',
                                         compute='_compute_suggested_hourly_rate', readonly=True)

    # Tax and Discount
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    tax_amount = fields.Float(string='Tax Amount', compute='_compute_amounts', store=True)
    discount_percent = fields.Float(string='Discount (%)')
    discount_amount = fields.Float(string='Discount Amount', compute='_compute_amounts', store=True)

    # Totals
    subtotal = fields.Float(string='Subtotal', compute='_compute_amounts', store=True)
    total = fields.Float(string='Total', compute='_compute_amounts', store=True)

    # Guest Information
    guests_count = fields.Integer(string='No. of Guests', default=1)
    guest_names = fields.Text(string='Guest Names')

    # Driver
    driver_id = fields.Many2one('res.partner', string='Driver',
                                domain=[('is_driver', '=', True)])

    # Status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    # Notes
    notes = fields.Text(string='Notes')

    @api.depends('vehicle_id', 'car_model_manual')
    def _compute_car_model_display(self):
        """Display either the vehicle info or manual entry"""
        for line in self:
            if line.vehicle_id:
                line.car_model_display = f"{line.vehicle_id.brand} {line.vehicle_id.model} ({line.vehicle_id.year})"
            elif line.car_model_manual:
                line.car_model_display = line.car_model_manual
            else:
                line.car_model_display = ''

    @api.depends('vehicle_id', 'vehicle_id.daily_rate')
    def _compute_suggested_hourly_rate(self):
        """Calculate suggested hourly rate from daily rate (daily_rate / 8 hours)"""
        for line in self:
            if line.vehicle_id and line.vehicle_id.daily_rate:
                line.suggested_hourly_rate = line.vehicle_id.daily_rate / 8.0
            else:
                line.suggested_hourly_rate = 0.0

    @api.depends('start_date', 'end_date')
    def _compute_hours(self):
        """Calculate total hours between start and end date"""
        for line in self:
            if line.start_date and line.end_date:
                delta = line.end_date - line.start_date
                line.total_hours = delta.total_seconds() / 3600.0
            else:
                line.total_hours = 0.0

    @api.depends('total_hours', 'duration')
    def _compute_extra_hours(self):
        """Calculate extra hours beyond contracted duration"""
        for line in self:
            if line.total_hours > line.duration:
                line.extra_hours = line.total_hours - line.duration
            else:
                line.extra_hours = 0.0

    @api.depends('unit_price', 'quantity', 'total_hours', 'misc_charges', 'discount_percent', 'tax_ids')
    def _compute_amounts(self):
        """Calculate subtotal, discount, tax, and total amounts"""
        for line in self:
            # Calculate base amount (use total_hours as quantity if applicable)
            base_qty = line.total_hours if line.total_hours > 0 else line.quantity
            base_amount = line.unit_price * base_qty

            # Add miscellaneous charges
            base_amount += line.misc_charges

            # Calculate discount
            discount = 0.0
            if line.discount_percent > 0:
                discount = base_amount * (line.discount_percent / 100.0)

            # Subtotal after discount
            subtotal = base_amount - discount

            # Calculate tax
            tax_amount = 0.0
            if line.tax_ids:
                # Get tax computation
                taxes = line.tax_ids.compute_all(
                    subtotal,
                    currency=line.booking_id.currency_id if line.booking_id else None,
                    quantity=1.0
                )
                tax_amount = taxes['total_included'] - taxes['total_excluded']

            # Update fields
            line.subtotal = base_amount
            line.discount_amount = discount
            line.tax_amount = tax_amount
            line.total = subtotal + tax_amount

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        """Auto-populate pricing when vehicle is selected"""
        if self.vehicle_id:
            # Set the hourly rate based on daily rate
            if self.vehicle_id.daily_rate:
                self.unit_price = self.vehicle_id.daily_rate / 8.0

            # Clear manual entry
            self.car_model_manual = False

    @api.onchange('service_id')
    def _onchange_service_id(self):
        """Auto-populate data from service product"""
        if self.service_id:
            self.unit_price = self.service_id.list_price

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Ensure end date is after start date"""
        for line in self:
            if line.start_date and line.end_date and line.end_date <= line.start_date:
                raise models.ValidationError('End date must be after start date!')

    def action_confirm(self):
        """Confirm service line"""
        self.write({'status': 'confirmed'})

    def action_start(self):
        """Start service"""
        self.write({'status': 'in_progress'})
        # If vehicle is assigned, mark it as rented
        if self.vehicle_id:
            self.vehicle_id.write({'status': 'rented'})

    def action_complete(self):
        """Complete service"""
        self.write({'status': 'completed'})
        # Return vehicle to available status
        if self.vehicle_id:
            self.vehicle_id.write({'status': 'available'})

    def action_cancel(self):
        """Cancel service line"""
        self.write({'status': 'cancelled'})
        # Return vehicle to available status if it was assigned
        if self.vehicle_id and self.vehicle_id.status == 'rented':
            self.vehicle_id.write({'status': 'available'})