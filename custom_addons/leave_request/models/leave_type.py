# -*- coding: utf-8 -*-

from odoo import api, fields, models


class LeaveType(models.Model):
    """Configuration model for leave types.

    This model stores the different types of leaves available
    in the organization (e.g., Casual Leave, Sick Leave, Annual Leave).
    Administrators configure these; employees select them when requesting leave.
    """

    _name = "leave.type"
    _description = "Leave Type"
    _order = "sequence, name"

    name = fields.Char(
        string="Leave Type",
        required=True,
        translate=True,
        help="Name of the leave type displayed to employees.",
    )
    code = fields.Char(
        string="Code",
        required=True,
        help="Short code for internal reference (e.g., CL, SL, AL).",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Determines the display order. Lower values appear first.",
    )
    max_days = fields.Float(
        string="Maximum Days Per Year",
        default=0.0,
        help="Maximum number of leave days allowed per year. "
             "Set to 0 for unlimited.",
    )
    color = fields.Integer(
        string="Color",
        help="Color index for kanban view.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive this leave type without deleting it.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        help="Company this leave type belongs to. "
             "Leave empty for all companies.",
    )

    # -------------------------------------------------------------------------
    # SQL Constraints
    # -------------------------------------------------------------------------
    _sql_constraints = [
        (
            "code_company_uniq",
            "UNIQUE(code, company_id)",
            "The leave type code must be unique per company!",
        ),
    ]
