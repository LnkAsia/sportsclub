# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StudentAdmission(models.Model):
    _name = "student.admission"
    _description = "Student Admission"

    name = fields.Char('Name', required=True,
                       readonly=True, default=lambda self: _('New'))
    student_id = fields.Many2one('res.partner', string='Student Name', required=True,
                                 domain=[('is_student', '=', True)])
    mobile = fields.Char('Mobile', related='student_id.mobile', store=True, readonly=False)
    p_name = fields.Char('Parent Name', related='student_id.p_name',  readonly=False)
    parent_mobile = fields.Char('Parent Mobile', related='student_id.phone',  readonly=False)
    p1_name = fields.Char('Parent Name ', related='inquiry_id.p_name',  readonly=False)
    parent1_mobile = fields.Char('Parent Mobile ', related='inquiry_id.parent_mobile',  readonly=False)
    email = fields.Char('Email', related='student_id.email', store=True, readonly=False)
    is_disability = fields.Boolean('Description', related='student_id.is_disability', store=True, readonly=False)
    disability_description = fields.Text('Disability Description', related='student_id.disability_description', store=True, readonly=False)
    sport_id = fields.Many2one(
        'product.product', string="Sport Name", domain=[('is_sportname', '=', True)])
    level_id = fields.Many2one('res.partner', string="Sport Center", domain=[
                               ('is_sport', '=', True)])
    trainer_id = fields.Many2one(comodel_name='res.partner', domain=[('is_coach', '=', True)], string='Coach')
    duration = fields.Float("Duration(Days)")
    state = fields.Selection([
        ('new', 'New'),
        ('enrolled', 'Enrolled'),
        ('student', 'Student'),
        ('cancel', 'Cancelled')], string='State',
        copy=False, default="new",store=True)
    is_invoiced = fields.Boolean()
    inquiry_id = fields.Many2one('student.inquiry', string='Inquiry')
    check_parent = fields.Boolean('Check Parent', related='inquiry_id.check_parent')
    check_register = fields.Boolean('Check Register')

    @api.onchange('trainer_id')
    def _onchange_trainer_id(self):
        if self.trainer_id and self.student_id:
            self.student_id.trainer_id = self.trainer_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'student.admission') or _('New')
        res = super(StudentAdmission, self).create(vals_list)
        portal_wizard_obj = self.env['portal.wizard']
        created_portal_wizard =  portal_wizard_obj.create({})
        if created_portal_wizard and res.email:
            portal_wizard_user_obj = self.env['portal.wizard.user']
            wiz_user_vals = {
                        'wizard_id': created_portal_wizard.id,
                        'partner_id': res.student_id.id,
                        'email' : res.student_id.email,
            }
            created_portal_wizard_user = portal_wizard_user_obj.create(wiz_user_vals)
            if created_portal_wizard_user:
                created_portal_wizard_user.action_grant_access()
        return res
    
    def action_enroll(self):
        self.state = 'enrolled'
        self.student_id.update({'is_student' : False})
        template = self.env.ref(
            'bi_sport_center_management.student_admission_enroll_email_template')
        if template:
            template.send_mail(self.id, force_send=True) 
        return {
            'name': 'Create Invoice',
            'view_mode': 'form',
            'res_model': 'create.invoice',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
        }

    def action_make_student(self):
        if not self.is_invoiced:
            return {
            'name': 'Create Invoice',
            'view_mode': 'form',
            'res_model': 'create.invoice',
            'type': 'ir.actions.act_window',
            'context': self._context,
            'target': 'new',
        }
        if self.is_invoiced:
            self.state = 'student'
            self.student_id.update({'is_student' : True})

    def action_cancel(self):
        self.state = 'cancel'

    def action_view_invoice(self):
        self.ensure_one()
        invoice_ids = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        if invoice_ids:
            action = {
                'name': _("Admission Invoices"),
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'target': 'current',
            }
            if len(invoice_ids.ids) == 1:
                invoice = invoice_ids.ids[0]
                action['res_id'] = invoice
                action['view_mode'] = 'form'
                action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            else:
                action['view_mode'] = 'list,form'
                action['domain'] = [('id', 'in', invoice_ids.ids)]
            return action