from odoo import models, fields, api
from datetime import datetime


class studentRegistration(models.Model):
    _name = "student.registration"

    def _default_currency_id(self):
        return self.env.user.company_id.currency_id

    name = fields.Char('Name', readonly=True)
    student_id = fields.Many2one('res.partner', string='Student Id', domain="[('is_student','=',True)]")
    phone = fields.Char(string="Phone", related="student_id.phone")
    age = fields.Integer("Age", compute='_compute_age')
    date = fields.Date('Date', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  default=_default_currency_id)

    amount = fields.Monetary('Amount', required=True)
    state = fields.Selection(
        [
            ('draft', 'draft'),
            ('confirmed', 'Confirmed'),
            ('invoiced', 'Invoiced'),
            ('canceled', 'Canceled')
        ], default='draft'
    )

    @api.depends('student_id')
    def _compute_age(self):
        for record in self:
            record.age = datetime.now - record.birth_date

    @api.model
    def create(self, data_list):
        data_list['name'] = self.env['ir.sequence'].next_by_code('student.registration')
        return super().create(data_list)

    def button_confirmed(self):
        for record in self:
            record.state = 'confirmed'

    def button_cancel(self):
        for record in self:
            record.state = 'canceled'
