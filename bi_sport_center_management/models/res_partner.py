# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_student = fields.Boolean('Student', readonly=True)
    is_coach = fields.Boolean('Coach', readonly=True)
    p_name = fields.Char('Parent Name')
    short_name = fields.Char('Short Name')
    is_disability = fields.Boolean('Disability', default=False)
    disability_description = fields.Text('Disability Description')    
    trainer_id = fields.Many2one(string='Current Coach', comodel_name='res.partner', domain=[('is_coach', '=', True)])
    is_sport = fields.Boolean('Sport Product')
    sport_id = fields.Many2many(
        'product.product', string="Sport Name", domain=[('is_sportname', '=', True)])

    @api.model
    def get_data(self):
        students = self.search([('is_student', '=', True)])
        trainers = self.search([('is_coach', '=', True)])
        inquiries = self.env['student.inquiry'].search([('state', '=', 'new')])
        admissions = self.env['student.admission'].search([])
        enroll_admissions = self.env['student.admission'].search([('state', '=', 'enrolled')])
        bookings = self.env['center.booking'].search([])
        center_spaces = self.env['product.product'].search([('is_space', '=', True)])
        center_event = self.env['event.event'].search([])
        total_sports = self.env['res.partner'].search([('is_sport', '=', True)])
        total_equipment = self.env['product.product'].search([('is_equipment', '=', True)])
        data =  {'total_inquiries': len(inquiries), 'total_center_events': len(center_event), 'total_bookings': len(bookings), 'total_sports': len(total_sports), 'total_equipment': len(total_equipment), 'total_center_spaces': len(center_spaces), 'total_trainers': len(trainers), 'total_students': len(students), 'total_confirm_admissions': len(admissions), 'total_enroll_admissions': len(enroll_admissions)}
        return data

    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        context = self._context
        params = context.get('params')
        
        if context.get('default_is_student') and not params:
            res.update({
                'is_student': True,
            })
        elif context.get('default_is_student'):
            res.update({
                'is_student': True,
            })
        elif context.get('default_name') and not params:
            res.update({
                'is_student': False,
            })
        elif context.get('default_is_sport') and not params:
            res.update({
                'is_student': False,
            })
        elif context.get('default_is_coach') and not params:
            res.update({
                'is_student': False,
            })
        elif (params and params.get('model') == 'student.admission'):
            res.update({
                'is_student': False,
            })

        return res