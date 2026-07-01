# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class LeaveRequest(models.Model):
    """Main transactional model for employee leave requests.

    Inherits mail.thread for chatter integration (messages, followers)
    and mail.activity.mixin for scheduling activities (reminders, to-dos).

    Workflow: Draft → Submitted → Approved / Rejected
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
        help="Auto-generated sequence number (e.g., LR/2026/0001).",
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
        help="Auto-filled from the employee's reporting manager.",
    )
    approver_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Approver",
        tracking=True,
        help="The person responsible for approving this request. "
             "Defaults to the employee's manager but can be changed.",
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
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
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
    # Onchange Methods
    # -------------------------------------------------------------------------
    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        """Auto-fill the approver when the employee changes.

        Sets the approver to the employee's direct manager.
        The user can override this if a different approver is needed.
        """
        if self.employee_id and self.employee_id.parent_id:
            self.approver_id = self.employee_id.parent_id
        else:
            self.approver_id = False

    # -------------------------------------------------------------------------
    # Constraint Methods
    # -------------------------------------------------------------------------
    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        """Validate that end date is not before start date."""
        for record in self:
            if record.date_from and record.date_to:
                if record.date_to < record.date_from:
                    raise ValidationError(
                        _("End date cannot be before start date.")
                    )

    @api.constrains("employee_id", "date_from", "date_to", "state")
    def _check_overlap(self):
        """Prevent overlapping leave requests for the same employee.

        Two leave requests overlap when one starts before the other ends
        AND ends after the other starts. Only checks submitted/approved
        requests — draft and rejected ones are excluded.
        """
        for record in self:
            if record.state in ("submitted", "approved"):
                domain = [
                    ("employee_id", "=", record.employee_id.id),
                    ("id", "!=", record.id),
                    ("state", "in", ("submitted", "approved")),
                    ("date_from", "<=", record.date_to),
                    ("date_to", ">=", record.date_from),
                ]
                overlapping = self.search(domain, limit=1)
                if overlapping:
                    raise ValidationError(
                        _("This employee already has a leave request "
                          "(%s) that overlaps with these dates.")
                        % overlapping.name
                    )

    # -------------------------------------------------------------------------
    # CRUD Overrides
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        """Assign sequence numbers and enforce employee ownership."""
        is_admin = self._is_leave_admin()
        current_employee = self._get_current_employee(required=not is_admin)
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("leave.request")
                    or _("New")
                )
            if not vals.get("employee_id") and current_employee:
                vals["employee_id"] = current_employee.id
            if (
                not is_admin
                and current_employee
                and vals.get("employee_id") != current_employee.id
            ):
                raise UserError(
                    _("You can only create leave requests for yourself.")
                )
            if not vals.get("approver_id") and vals.get("employee_id"):
                employee = self.env["hr.employee"].browse(vals["employee_id"])
                vals["approver_id"] = employee.parent_id.id or False
        return super().create(vals_list)

    def write(self, vals):
        """Prevent unauthorized direct edits outside the workflow methods."""
        if self.env.context.get("leave_workflow_action"):
            return super().write(vals)

        protected_fields = {
            "employee_id",
            "approver_id",
            "leave_type_id",
            "date_from",
            "date_to",
            "reason",
        }
        is_admin = self._is_leave_admin()
        current_employee = self._get_current_employee(required=not is_admin)

        if "state" in vals and not is_admin:
            raise UserError(
                _("Please use the workflow buttons to change the request status.")
            )

        for record in self:
            if not is_admin and record.employee_id != current_employee:
                raise UserError(
                    _("You can only edit your own leave requests.")
                )
            if (
                not is_admin
                and record.state != "draft"
                and protected_fields.intersection(vals)
            ):
                raise UserError(
                    _("Only draft leave requests can be edited.")
                )
            if (
                not is_admin
                and vals.get("employee_id")
                and vals["employee_id"] != current_employee.id
            ):
                raise UserError(
                    _("You cannot transfer a leave request to another employee.")
                )
        return super().write(vals)

    def unlink(self):
        """Prevent deletion of non-draft leave requests."""
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
    def action_submit(self):
        """Submit the leave request for approval.

        Transitions: Draft → Submitted
        Validates that an approver is assigned, then schedules
        a to-do activity for the approver to review the request.
        """
        for record in self:
            if record.state != "draft":
                raise UserError(
                    _("Only draft requests can be submitted.")
                )
            if not record.approver_id:
                raise UserError(
                    _("Please set an approver before submitting. "
                      "The approver is the person who will review "
                      "your leave request.")
                )
            record._check_employee_owner_or_admin()
        self.with_context(leave_workflow_action=True).write({"state": "submitted"})
        # Schedule approval activity for each approver
        for record in self:
            if record.approver_id.user_id:
                record.activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=record.approver_id.user_id.id,
                    summary=_("Leave Request to Approve: %s") % record.name,
                    note=_(
                        "%s has requested %s day(s) of %s from %s to %s. "
                        "Please review and approve or reject."
                    ) % (
                        record.employee_id.name,
                        record.number_of_days,
                        record.leave_type_id.name,
                        record.date_from,
                        record.date_to,
                    ),
                )

    def action_approve(self):
        """Approve the leave request.

        Transitions: Submitted → Approved
        Only the assigned approver (or a Leave Administrator) can approve.
        Marks any pending approval activities as done.
        """
        for record in self:
            if record.state != "submitted":
                raise UserError(
                    _("Only submitted requests can be approved.")
                )
            record._check_approver_rights()
        self.with_context(leave_workflow_action=True).write({"state": "approved"})
        # Mark approval activities as done
        self.activity_feedback(["mail.mail_activity_data_todo"])

    def action_reject(self):
        """Reject the leave request.

        Transitions: Submitted → Rejected
        Only the assigned approver (or a Leave Administrator) can reject.
        Marks any pending approval activities as done.
        """
        for record in self:
            if record.state != "submitted":
                raise UserError(
                    _("Only submitted requests can be rejected.")
                )
            record._check_approver_rights()
        self.with_context(leave_workflow_action=True).write({"state": "rejected"})
        # Mark approval activities as done
        self.activity_feedback(["mail.mail_activity_data_todo"])

    def action_reset_to_draft(self):
        """Reset a rejected request back to draft.

        Transitions: Rejected → Draft
        Allows the employee to modify and resubmit a rejected request.
        """
        for record in self:
            if record.state != "rejected":
                raise UserError(
                    _("Only rejected requests can be reset to draft.")
                )
            record._check_employee_owner_or_admin()
        self.activity_unlink(["mail.mail_activity_data_todo"])
        self.with_context(leave_workflow_action=True).write({"state": "draft"})

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------
    def _check_approver_rights(self):
        """Verify that the current user is the assigned approver
        or has Leave Administrator privileges.

        This enforces the business rule: 'Only the assigned approver
        can finalize approval.'
        """
        self.ensure_one()
        is_admin = self._is_leave_admin()
        if is_admin:
            return
        current_employee = self._get_current_employee()
        is_approver = (
            current_employee and current_employee == self.approver_id
        )
        is_manager = self.env.user.has_group(
            "leave_request.group_leave_manager"
        )
        if not is_manager or not is_approver:
            raise UserError(
                _("Only the assigned approver (%s) or a Leave "
                  "Administrator can approve/reject this request.")
                % (self.approver_id.name or _("not set"))
            )

    def _check_employee_owner_or_admin(self):
        """Allow only the employee owner or a Leave Administrator."""
        self.ensure_one()
        if self._is_leave_admin():
            return
        if self.employee_id != self._get_current_employee():
            raise UserError(
                _("Only the employee who owns this request can perform this action.")
            )

    def _get_current_employee(self, required=True):
        """Return the HR employee linked to the current user."""
        employee = self.env["hr.employee"].search(
            [("user_id", "=", self.env.uid)], limit=1
        )
        if required and not employee:
            raise UserError(
                _("Your user is not linked to an employee record.")
            )
        return employee

    def _is_leave_admin(self):
        """Return whether the current user has Leave Administrator rights."""
        return self.env.user.has_group("leave_request.group_leave_admin")
