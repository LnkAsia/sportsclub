from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CarRental(models.Model):
    _name = 'car.rental'
    _description = 'Car Rental'

    name = fields.Char(string='Rental Reference', required=True, default='New', copy=False)
    car_id = fields.Many2one('fleet.vehicle', string='Car', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    start_date = fields.Datetime(string='Start Date', required=True)
    end_date = fields.Datetime(string='End Date', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft')

    @api.constrains('car_id', 'start_date', 'end_date')
    def _check_car_availability(self):
        for rental in self:
            if rental.start_date >= rental.end_date:
                raise ValidationError("End date must be after start date.")

            overlapping = self.env['car.rental'].search([
                ('id', '!=', rental.id),
                ('car_id', '=', rental.car_id.id),
                ('start_date', '<', rental.end_date),
                ('end_date', '>', rental.start_date),
            ])
            if overlapping:
                raise ValidationError(
                    f"The car '{rental.car_id.name}' is already rented between "
                    f"{overlapping[0].start_date} and {overlapping[0].end_date}."
                )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('car.rental') or 'New'
        return super().create(vals)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
    
