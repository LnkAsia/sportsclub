from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    membership = fields.Char('MembersShip Number')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')