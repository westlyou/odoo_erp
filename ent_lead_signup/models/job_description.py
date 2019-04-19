from odoo import models, fields, api


class JobDescription(models.Model):
	_inherit = 'job.description'
	
	#season_non_season = fields.Char(
	#	string='Season - Non Season',
	#)
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
