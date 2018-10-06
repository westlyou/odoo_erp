# -*- coding: utf-8 -*-
{
    "name": """Project Task Extension""",
    "summary": """Use checklist to be ensure that all your tasks are 
    performed and to make easy control over them""",
    "category": """Project Management""",
    "version": "10.0.1.0.0",
    "application": True,

    "author": "Entigrity",
    "website": "http://entigrity.com",

    "depends": ['base', 'project', 'hr_timesheet_sheet'],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
            'data/subscription_template.xml',
            'views/project_task_subtask.xml',
            'security/ir.model.access.csv',
        ],

    "auto_install": False,
    "installable": True,
}
