from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import ValidationError


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
    customer_invoice_ids = fields.Many2many('account.move')
    count_invoices = fields.Integer("Count Invoices", compute="_compute_count_invoices")

    @api.depends('customer_invoice_ids')
    def _compute_count_invoices(self):
        for request in self:
            request.count_invoices = len(request.customer_invoice_ids)

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

    def view_invoices(self):
        """Action view for invoices of a customer"""
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [('id', 'in', self.customer_invoice_ids.ids),
                       ('move_type', 'in', self.env['account.move'].get_sale_types())],
            "context": {"create": False},
            "name": "Customer Invoices",
            'view_mode': 'tree,form',
        }
        return result

    def prepare_customer_invoice(self):
        """Prepares customer invoices based on lines on request"""
        customer_invoice = self.env['account.move']
        invoice_lines = []
        student_serice = self.env.ref('knowledge_bi.product_student_reg_service')
        invoice_lines.append((0, 0, {
            'name': student_serice.name,
            'display_name': student_serice.name,
            'price_unit': self.amount,
            'quantity': 1,
            'product_id': student_serice.id or False,
        }))

        customer_bill_vals = {
            'invoice_date': datetime.now().date(),
            'move_type': 'out_invoice',
            'state': 'draft',
            'partner_id': self.student_id.id,
            'invoice_line_ids': invoice_lines,
        }
        customer_invoice += self.env['account.move'].create(customer_bill_vals)
        return customer_invoice

    def action_create_invoice(self):
        """Create a new invoice"""
        customer_invoice = self.prepare_customer_invoice()
        if customer_invoice:
            self.customer_invoice_ids = [(6, 0, customer_invoice.ids)]
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount == 0.0:
                raise ValidationError('Please enter amount Value')
