# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class LeaveRequest(models.Model):
    """Main transactional model for employee leave requests.

    Inherits mail.thread for chatter integration (messages, followers)
    and mail.activity.mixin for scheduling activities (reminders, to-dos).

    Workflow: Draft → Confirmed → Approved / Refused
    """

    _name = "leave.request"
    _description = "Leave Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"
    _rec_name = "name"

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------
    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
        help="Auto-generated sequence number for this leave request.",
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
        tracking=True,
        default=lambda self: self.env["hr.employee"].search(
            [("user_id", "=", self.env.uid)], limit=1
        ),
        help="Employee requesting the leave.",
    )
    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        related="employee_id.department_id",
        store=True,
        readonly=True,
        help="Auto-filled from the employee's department.",
    )
    manager_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Manager",
        related="employee_id.parent_id",
        store=True,
        readonly=True,
        help="Auto-filled from the employee's manager.",
    )
    leave_type_id = fields.Many2one(
        comodel_name="leave.type",
        string="Leave Type",
        required=True,
        tracking=True,
        help="Type of leave being requested.",
    )
    date_from = fields.Date(
        string="Start Date",
        required=True,
        tracking=True,
        help="First day of the leave period.",
    )
    date_to = fields.Date(
        string="End Date",
        required=True,
        tracking=True,
        help="Last day of the leave period.",
    )
    number_of_days = fields.Float(
        string="Duration (Days)",
        compute="_compute_number_of_days",
        store=True,
        readonly=True,
        help="Total number of leave days (inclusive of start and end dates).",
    )
    reason = fields.Text(
        string="Reason",
        help="Reason or justification for the leave request.",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("approved", "Approved"),
            ("refused", "Refused"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
        copy=False,
        help="Current status of the leave request.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        related="employee_id.company_id",
        store=True,
        readonly=True,
        help="Company of the employee.",
    )

    # -------------------------------------------------------------------------
    # SQL Constraints
    # -------------------------------------------------------------------------
    _sql_constraints = [
        (
            "date_check",
            "CHECK(date_to >= date_from)",
            "End date must be greater than or equal to start date!",
        ),
    ]

    # -------------------------------------------------------------------------
    # Compute Methods
    # -------------------------------------------------------------------------
    @api.depends("date_from", "date_to")
    def _compute_number_of_days(self):
        """Calculate the number of leave days from the date range.

        Uses inclusive counting: a leave from Monday to Friday = 5 days.
        """
        for record in self:
            if record.date_from and record.date_to:
                delta = record.date_to - record.date_from
                record.number_of_days = delta.days + 1
            else:
                record.number_of_days = 0.0

    # -------------------------------------------------------------------------
    # Constraint Methods
    # -------------------------------------------------------------------------
    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        """Validate that end date is not before start date.

        This is a Python-level constraint that provides a user-friendly
        error message. The SQL constraint above is the database-level safety net.
        """
        for record in self:
            if record.date_from and record.date_to:
                if record.date_to < record.date_from:
                    raise ValidationError(
                        _("End date cannot be before start date.")
                    )

    # -------------------------------------------------------------------------
    # CRUD Overrides
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to assign automatic sequence number.

        When a new leave request is created, the 'name' field is
        populated from the ir.sequence 'leave.request' (e.g., LR/2026/0001).
        """
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("leave.request")
                    or _("New")
                )
        return super().create(vals_list)

    def unlink(self):
        """Prevent deletion of non-draft leave requests.

        Only draft requests can be deleted. Once a request is confirmed,
        approved, or refused, it must be kept for audit trail purposes.
        """
        for record in self:
            if record.state != "draft":
                raise UserError(
                    _("You cannot delete a leave request "
                      "that is not in draft state.")
                )
        return super().unlink()

    # -------------------------------------------------------------------------
    # Workflow Action Methods
    # -------------------------------------------------------------------------
    def action_confirm(self):
        """Submit the leave request for approval.

        Transitions: Draft → Confirmed
        Available to: The employee who created the request
        """
        for record in self:
            if record.state != "draft":
                raise UserError(
                    _("Only draft requests can be submitted for approval.")
                )
        self.write({"state": "confirmed"})

    def action_approve(self):
        """Approve the leave request.

        Transitions: Confirmed → Approved
        Available to: Leave Managers (the employee's manager)
        """
        for record in self:
            if record.state != "confirmed":
                raise UserError(
                    _("Only confirmed requests can be approved.")
                )
        self.write({"state": "approved"})

    def action_refuse(self):
        """Refuse the leave request.

        Transitions: Confirmed → Refused
        Available to: Leave Managers (the employee's manager)
        """
        for record in self:
            if record.state != "confirmed":
                raise UserError(
                    _("Only confirmed requests can be refused.")
                )
        self.write({"state": "refused"})

    def action_reset_to_draft(self):
        """Reset a refused request back to draft.

        Transitions: Refused → Draft
        Allows the employee to modify and resubmit a refused request.
        """
        for record in self:
            if record.state != "refused":
                raise UserError(
                    _("Only refused requests can be reset to draft.")
                )
        self.write({"state": "draft"})
