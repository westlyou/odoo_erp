from odoo import models, fields, api


SEASONAL_HOURS = [('10', '10 Hours'), ('20', '20 Hours'), ('30', '30 Hours'), ('40', '40 Hours'),('80', '80 Hours'), ('90', '90 Hours'), ('100', '100 Hours'), ('160', '160 Hours'), ('180', '180 Hours'), ('200', '200 Hours'), ('40_20', '40-20 Hours'), ('20_10', '20-10 Hours')]

class JobDescription(models.Model):
	_inherit = 'job.description'
	
	seasonal_hour = fields.Char(
		SEASONAL_HOURS,
		string='Season - Non Season',
	)
	seasonal_rate_per_hour = fields.Float(
		string='Seasonal Rate Per Hour',
	)
	perm_season_date_from = fields.Datetime(
		string='Season Date From',
	)
	perm_season_date_to = fields.Datetime(
		string='Season Date To',
	)
	task_to_be_done2 = fields.Char(
		string='task To be Done2'
	)
	task_to_be_done3 = fields.Char(
		string='task To be Done3'
	)
	task_to_be_done4 = fields.Char(
		string='task To be Done4'
	)


class Lead(models.Model):
	_inherit = 'crm.lead'
	
	lead_ext = fields.Char(
		string="Ext",
	)
