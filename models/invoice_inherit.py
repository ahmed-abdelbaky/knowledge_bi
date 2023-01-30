from odoo import models, fields, api


class invoiceInherit(models.Model):
    _inherit = 'account.move'

    registration_id = fields.Many2one('student.registration')