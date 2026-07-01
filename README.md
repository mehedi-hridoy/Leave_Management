# Leave Management — Odoo 17 Community Module

A professional Employee Leave Request Management System built for Odoo 17 Community Edition. Features role-based approval workflow, configurable leave types, automatic notifications, and comprehensive reporting.

---

## Live Demo

Watch the live demo video here:

- https://drive.google.com/file/d/1P6N02jTxgpDQMEi0VHyiIMAvVOVC9lRA/view?usp=sharing

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

This project is an Odoo addon, not a standalone Python application. To run it, you need an Odoo 17 Community environment.

You can run it in either of these ways:

- **Recommended for reviewers:** Docker Desktop on Windows, macOS, or Linux
- **Existing Odoo setup:** Odoo 17 Community, PostgreSQL, and Python 3.10+

The module depends on these Odoo apps:

- `base`
- `hr`
- `mail`

Odoo installs these automatically when this module is installed.

---

## Installation

### Option A: Run With Docker

This is the easiest cross-platform setup for Windows, macOS, and Linux.

#### 1. Install Docker

Install Docker Desktop:

- Windows: Docker Desktop with WSL2 enabled
- macOS: Docker Desktop
- Linux: Docker Engine or Docker Desktop

#### 2. Clone the Repository

```bash
git clone https://github.com/mehedi-hridoy/Leave_Management.git
cd Leave_Management
```

#### 3. Create a Docker Network and Database

```bash
docker network create odoo-leave-network
docker volume create odoo-leave-db-data
docker run -d --name odoo-leave-db --network odoo-leave-network -e POSTGRES_DB=postgres -e POSTGRES_USER=odoo -e POSTGRES_PASSWORD=odoo -v odoo-leave-db-data:/var/lib/postgresql/data postgres:15
```

#### 4. Start Odoo 17

Linux/macOS terminal:

```bash
docker run -d --name odoo-leave-app --network odoo-leave-network -p 8069:8069 -e HOST=odoo-leave-db -e USER=odoo -e PASSWORD=odoo -v "$(pwd)/custom_addons:/mnt/extra-addons" odoo:17.0
```

Windows PowerShell:

```powershell
docker run -d --name odoo-leave-app --network odoo-leave-network -p 8069:8069 -e HOST=odoo-leave-db -e USER=odoo -e PASSWORD=odoo -v "${PWD}/custom_addons:/mnt/extra-addons" odoo:17.0
```

#### 5. Open Odoo

Open:

```text
http://localhost:8069
```

Create a new database from the Odoo database screen.

#### 6. Install the Module

1. Log in to Odoo.
2. Go to **Apps**.
3. Click **Update Apps List**.
4. Search for **Leave Management**.
5. Click **Activate**.

### Option B: Install on an Existing Odoo 17 Instance

Use this option if Odoo 17 is already installed on your machine or server.

#### 1. Clone the Repository

```bash
git clone https://github.com/mehedi-hridoy/Leave_Management.git
cd Leave_Management
```

#### 2. Copy the Addon Into Your Custom Addons Directory

Linux example:

```bash
sudo cp -r custom_addons/leave_request /opt/odoo/custom_addons/
sudo chown -R odoo:odoo /opt/odoo/custom_addons/leave_request
```

Windows example:

```powershell
Copy-Item -Recurse .\custom_addons\leave_request C:\odoo\custom_addons\
```

macOS example:

```bash
cp -R custom_addons/leave_request /path/to/odoo/custom_addons/
```

#### 3. Confirm Your Odoo Addons Path

Your Odoo configuration must include the custom addons directory.

Example:

```ini
addons_path = /opt/odoo/odoo/addons,/opt/odoo/custom_addons
```

On Windows, use your actual Odoo paths, for example:

```ini
addons_path = C:\odoo\server\odoo\addons,C:\odoo\custom_addons
```

#### 4. Restart Odoo

Linux service example:

```bash
sudo systemctl restart odoo
```

If you run Odoo manually from source:

```bash
python odoo-bin -c /path/to/odoo.conf
```

#### 5. Update Apps and Install

1. Open Odoo in your browser, usually:

```text
http://localhost:8069
```

2. Go to **Apps**.
3. Click **Update Apps List**.
4. Search for **Leave Management**.
5. Click **Activate**.

### Upgrade After Code Changes

If the module is already installed and you changed the source code, upgrade it.

Linux service/source example:

```bash
sudo -u odoo /usr/bin/odoo -c /etc/odoo/odoo.conf -d YOUR_DATABASE_NAME -u leave_request --stop-after-init
sudo systemctl restart odoo
```

Docker example:

```bash
docker restart odoo-leave-app
```

Then open Odoo, go to **Apps**, search for **Leave Management**, open the module, and click **Upgrade**.

Replace `YOUR_DATABASE_NAME` with the database you created in Odoo when using the Linux/source command.

### Assign User Roles

1. Go to **Settings → Users & Companies → Users**
2. Open each user who should use the module
3. Under **Leave Management**, assign one role:
   - **User** for employees who create and submit their own requests
   - **Manager** for approvers
   - **Administrator** for full configuration and reporting access

If the Leave Management app is not visible after installation, confirm that the logged-in user has one of these Leave Management roles.

### Verify the Installation

After installation, verify these points:

1. The **Leave Management** app appears in the app launcher.
2. **Leave Management → Leave Requests → My Requests** opens correctly.
3. A user with the **User** role can create and submit their own leave request.
4. A user with the **Manager** role can see assigned requests under **Requests to Approve**.
5. Only the assigned approver can approve or reject the request.
6. **Leave Management → Reporting → Leave Analysis** is visible to managers/admins.

### Troubleshooting

- If the app does not appear, update the Apps list and check the `addons_path`.
- If the menu does not appear, assign a Leave Management role to the current user.
- If approval fails, confirm the approver is linked to an `hr.employee` record and has the **Manager** role.
- If Docker cannot start because port `8069` is already used, change `-p 8069:8069` to another port, for example `-p 8070:8069`, then open `http://localhost:8070`.

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
