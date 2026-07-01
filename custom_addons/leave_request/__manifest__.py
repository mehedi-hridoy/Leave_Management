# -*- coding: utf-8 -*-
{
    "name": "Leave Management",
    "version": "17.0.1.0.0",
    "summary": "Employee Leave Request Management System",
    "description": """
        Employee Leave Management System
        =================================
        - Leave request creation and approval workflow
        - Multi-level approval (Manager)
        - Leave types configuration
        - Automatic sequence numbering
        - Mail integration with chatter
        - Dashboard with kanban, tree, and form views
        - Security groups and record rules
    """,
    "author": "Mehedi Hasan",
    "website": "",
    "category": "Human Resources/Leave Management",
    "license": "LGPL-3",
    "depends": [
        "base",
        "hr",
        "mail",
    ],
    "data": [
        # Security — MUST be loaded first
        "security/leave_security.xml",
        "security/ir.model.access.csv",
        "security/leave_record_rules.xml",
        # Data
        "data/sequence_data.xml",
        "data/leave_type_data.xml",
        # Views
        "views/leave_type_views.xml",
        "views/leave_request_views.xml",
        # Menus — MUST be loaded last (references actions from views)
        "views/leave_menus.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "application": True,
    "installable": True,
    "auto_install": False,
    "sequence": 1,
}
