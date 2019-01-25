# -*- coding: utf-8 -*-
{
    "name": """Timesheet Report""",
    "summary": """get reprot of timesheet""",
    "category": """Project Management""",
    "version": "10.0.1.0.0",
    "application": True,

    "author": "Entigrity",
    "website": "http://entigrity.com",

    "depends": ['indimedi_crm'],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
            'wizard/custom_timesheet_report_view.xml',
            'wizard/periodic_timesheet_report_view.xml',
        ],

    "auto_install": False,
    "installable": True,
}
