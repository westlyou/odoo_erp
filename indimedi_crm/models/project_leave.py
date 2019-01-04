from odoo import models, fields, api


class ProjectLeave(models.Model):
    _name = 'project.leave'
    
    name = fields.Many2one('project.task', string="Client", required=True)
    project_id = fields.Many2one(related='name.project_id', string="Project", copy=False)
    invoicing_type_id = fields.Many2one(related='project_id.invoicing_type_id', string="Invoicing Type")
    hour_selection = fields.Selection(related='project_id.hour_selection', string="Working Hours", copy=False)
    min_hour_per_day = fields.Float(string="Min Hour/Day", copy=False)
    us_name_id = fields.Many2one(related='project_id.jd_us_name_id', string="US Name", copy=False)
    start_date = fields.Date(string="Start Date", required=True, default=fields.Datetime.now)
    end_date = fields.Date(string="End Date", required=True, default=fields.Datetime.now)
    leave_duration = fields.Integer(string="Leave Duration(Hour)", required=True, copy=False)
    reason = fields.Text(string="Reason for Leave", required=True, copy=False)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('sent', 'Sent')], string="State", copy=False)
    