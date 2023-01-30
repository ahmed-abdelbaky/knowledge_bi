from odoo import models, fields, api
from datetime import datetime
from dateutil import relativedelta
from odoo.exceptions import ValidationError


class partnerInherit(models.Model):
    _inherit = 'res.partner'

    is_student = fields.Boolean()
    birth_date = fields.Datetime('Birthday')

    @api.constrains('birth_date')
    def _check_date(self):
        for record in self:
            if record.birth_date > datetime.today():
                raise ValidationError('this date not allow to register')
