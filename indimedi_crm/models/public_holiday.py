from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError

import time


class PublicHoliday(models.Model):
    _name = 'public.holiday'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char(string='Holiday Name', track_visibility='onchange')
    public_holiday_date = fields.Date(string='Date', track_visibility='onchange')

    @api.multi
    @api.constrains('public_holiday_date')
    def _identify_same_holiday(self):
        for record in self:
            holiday_obj = self.search([
                ('public_holiday_date', '=ilike', record.public_holiday_date),
                ('id','!=',record.id)])
            if holiday_obj:
                raise ValidationError(_('Holiday is already defined on this Date. (Public Holiday Date: %s)')
                    % record.public_holiday_date)
