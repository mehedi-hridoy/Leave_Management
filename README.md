# Leave Management — Odoo 17 Community Module

A professional Employee Leave Request Management System built for Odoo 17 Community Edition. Features role-based approval workflow, configurable leave types, automatic notifications, and comprehensive reporting.

---

## Features

### Core
- **Leave Request Management** — Create, submit, track, and manage employee leave requests
- **Configurable Leave Types** — Casual, Sick, Annual, Unpaid (customizable by admin)
- **Auto-Generated References** — Sequential numbering (LR/2026/0001)
- **Computed Duration** — Automatic day count from start/end dates
- **Date Validation** — SQL + Python constraints prevent invalid date ranges
- **Overlap Detection** — Prevents duplicate leave bookings for the same employee

### Approval Workflow
```
Draft → Submitted → Approved
                  → Rejected → Draft (re-submit)
```
- **Submit** — Employee submits request; an activity is created for the approver
- **Approve/Reject** — Only the assigned approver or a Leave Administrator can act
- **Reset to Draft** — Rejected requests can be modified and resubmitted

### Security & Access Control
| Role | Permissions |
|------|------------|
| **Leave User** | Create/edit own requests, read leave types |
| **Leave Manager** | Approve/reject team requests, view team data |
| **Leave Administrator** | Full access to all data and configuration |

**Record Rules:**
- Users see only their own requests
- Managers see their own + their team's + requests assigned to them
- Administrators see all requests
- Multi-company isolation applied

### Views
- **Tree View** — Color-coded rows, status badges, employee avatars, day totals
- **Form View** — Workflow header with Submit/Approve/Reject buttons, statusbar, rejection ribbon, chatter
- **Kanban View** — Cards grouped by status with employee avatars
- **Calendar View** — Visual timeline of leaves colored by type
- **Search View** — Quick filters (My Requests, To Approve), group-by options
- **Pivot View** — Leave analysis by employee × leave type
- **Graph View** — Bar chart of leave days by department

### Notifications
- **Chatter Integration** — All state changes are tracked and logged
- **Activity Scheduling** — Approver receives a to-do activity when a request is submitted
- **Activity Feedback** — Activities are marked done when request is approved/rejected

---

## Prerequisites

- Odoo 17 Community Edition
- Python 3.10+
- PostgreSQL 14+
- Required Odoo modules: `base`, `hr`, `mail` (auto-installed as dependencies)

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/mehedi-hridoy/Leave_Management.git
cd Leave_Management
```

### 2. Copy to Odoo Custom Addons
```bash
sudo cp -r custom_addons/leave_request /opt/odoo/custom_addons/
sudo chown -R odoo:odoo /opt/odoo/custom_addons/leave_request
```

### 3. Restart Odoo
```bash
sudo systemctl restart odoo
```

### 4. Install the Module
1. Log in to Odoo → **Apps**
2. Click **Update Apps List**
3. Search for **"Leave Management"**
4. Click **Activate**

### 5. Assign User Roles
1. Go to **Settings → Users & Companies → Users**
2. Open each user who should use the module
3. Under **Leave Management**, assign one role:
   - **User** for employees who create and submit their own requests
   - **Manager** for approvers
   - **Administrator** for full configuration and reporting access

If the Leave Management app is not visible after installation, confirm that the logged-in user has one of these Leave Management roles.

---

## Usage

### As an Employee
1. Navigate to **Leave Management → Leave Requests → My Requests**
2. Click **New** to create a leave request
3. Fill in the leave type, dates, and reason
4. The approver auto-fills from your manager (editable)
5. Click **Submit** — your approver receives a notification

### As a Manager / Approver
1. Navigate to **Leave Management → Leave Requests → Requests to Approve**
2. Review the submitted request
3. Click **Approve** or **Reject**
4. The employee is notified via chatter

### As an Administrator
1. **All Requests** — View every leave request in the system
2. **Leave Analysis** — Pivot and graph reports under Reporting menu
3. **Configuration → Leave Types** — Add/modify leave types

---

## Workflow & Security Design

### State Machine
The leave request follows a linear workflow with a rejection loop:

```
┌───────┐     ┌───────────┐     ┌──────────┐
│ Draft │ ──→ │ Submitted │ ──→ │ Approved │
└───────┘     └─────┬─────┘     └──────────┘
     ↑              │
     │              ↓
     │        ┌──────────┐
     └─────── │ Rejected │
              └──────────┘
```

**Business Rules:**
- Only the request creator can submit (Draft → Submitted)
- Only the assigned approver or admin can approve/reject
- Only rejected requests can be reset to draft
- Non-draft requests cannot be deleted (audit trail)

### Security Architecture
The module implements three-layer security:

1. **Security Groups** — Define roles (User/Manager/Admin) with implied hierarchy
2. **Access Rights (CSV)** — Control CRUD operations per model per group
3. **Record Rules (XML)** — Filter which records each role can see

This layered approach ensures that even if a user manipulates the URL, they cannot access unauthorized data.

---

## Module Structure

```
leave_request/
├── __init__.py                     # Root Python package
├── __manifest__.py                 # Module metadata and dependencies
├── controllers/
│   └── __init__.py                 # Reserved for future portal controllers
├── data/
│   ├── leave_type_data.xml         # Default leave types (CL, SL, AL, UL)
│   └── sequence_data.xml           # Auto-numbering sequence
├── demo/
│   └── demo_data.xml               # Sample employees and leave requests
├── models/
│   ├── __init__.py                 # Model imports
│   ├── leave_request.py            # Main leave request model
│   └── leave_type.py               # Leave type configuration model
├── security/
│   ├── ir.model.access.csv         # Access control list
│   ├── leave_record_rules.xml      # Record-level security rules
│   └── leave_security.xml          # Security groups definition
└── views/
    ├── leave_menus.xml             # Menu hierarchy
    ├── leave_request_views.xml     # All leave request views + actions
    └── leave_type_views.xml        # Leave type views + action
```

---

## Technical Notes

- **Odoo Version:** 17.0 Community
- **Python:** 3.10+
- **License:** LGPL-3
- **Dependencies:** `base`, `hr`, `mail`
- **Model:** `leave.request` (inherits `mail.thread`, `mail.activity.mixin`)
- **Sequence:** `LR/%(year)s/NNNN` with padding 4

---


## Author

**Mehedi Hasan Hridoy**
