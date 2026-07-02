# AGENTS.md

> [!CAUTION]
> **CRITICAL REMINDER**: You MUST ALWAYS ask the developer for explicit permission/approval before modifying, creating, or deleting ANY files, or changing any architectural logic, models, fields, database structures, or security rules. DO NOT proceed without developer confirmation.

## Project Overview

### Project Name

**T4 Gate Keeper**

### Technical Stack

* Framework: Odoo 19
* Language: Python 3
* Database: PostgreSQL
* Frontend: Odoo XML Views, JavaScript (when required)
* Module Name: `t4_gate_keeper`

### Purpose

T4 Gate Keeper is a backend system responsible for managing physical access control infrastructure.

The system manages:

* Controllers
* Devices
* Company-based ownership and visibility

The project is currently in the MVP phase and focuses on controller and device management.

### Project Structure

```text
t4_gate_keeper/
├── data/
│   └── scheduler_cron.xml
├── i18n/
│   └── vi.po
├── models/
│   ├── __init__.py
│   ├── gk_access_log.py
│   ├── gk_algorithm.py
│   ├── gk_authen_info.py
│   ├── gk_branch.py
│   ├── gk_controller.py
│   ├── gk_device.py
│   ├── gk_device_model.py
│   ├── gk_employee.py
│   ├── gk_employee_biometric.py
│   ├── gk_scheduler.py
│   └── hr_employee.py
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── views/
│   ├── GK_menu.xml
│   ├── gate_keeper_views.xml
│   ├── gk_access_log_views.xml
│   ├── gk_branch_views.xml
│   ├── gk_controller_sync_views.xml
│   ├── gk_device_model_views.xml
│   ├── gk_employee_biometric_views.xml
│   ├── gk_employee_views.xml
│   └── hr_employee_views.xml
├── .gitignore
├── AGENTS.md
├── __init__.py
├── __manifest__.py
└── document.txt
```

---

# Core Business Concepts

## Controller

In this project, a **Controller** is a physical hardware device.

It is **NOT** an Odoo controller and **NOT** an MVC controller.

Responsibilities:

* Acts as an intermediate gateway.
* Communicates with multiple devices.
* Collects data from devices.
* Sends data back to the server.
* Receives commands from the server and forwards them to devices.

Whenever the term **Controller** appears in the codebase, documentation, comments, or generated code, it refers to the physical controller hardware.

---

## Device

A Device is a hardware endpoint managed by a Controller.

Examples:

* Door reader
* RFID reader
* Fingerprint scanner
* Face recognition terminal
* Access sensor

A Device must always belong to a Controller.

---

## Domain Hierarchy & Synchronization

The database entities follow this hierarchy:
* **Branch** (`t4.gate_keeper.branch`) contains multiple **Controllers**.
* **Controller** (`t4.gate_keeper.controller`) manages multiple **Devices**.
* **Device** (`t4.gate_keeper.device`) has a Many2one relationship with a **Device Model** (`t4.gate_keeper.device_model`).
* **Device Model** can support multiple **Algorithms** (`t4.gate_keeper.algorithm`).
* **Employee** (`t4.gate_keeper.employee`) is associated with **Algorithms** via the **Employee Biometric** relationship table (`t4.gate_keeper.employee.biometric`).
  * Each employee has distinct biometric templates/data tailored for specific algorithms.
  * This allows sync templates to devices that utilize the matching biometric algorithm.

---

## Employee Separation & ID Workflow

> [!WARNING]
> **CRITICAL ARCHITECTURAL RULE**: The employee record in Gate Keeper (`t4.gate_keeper.employee`) must remain completely separate from Odoo's standard HR employee record (`hr.employee`).

### Employee Code (emp_id) Policy:
- Always generate a distinct, independent, unique identifier (`emp_id`) specifically for the Gate Keeper employee record.
- **DO NOT** reuse or prioritize the `hr.employee` standard identifier/code.
- **RATIONALE**: Physical biometric devices register templates/fingerprints/faces tied directly to a fixed biometric ID hash. If we used standard HR employee codes, any subsequent change to the HR employee code in Odoo would break the device-side association, as those hardware-bound hashes cannot easily be changed. Using a separate, permanent, independent `emp_id` ensures synchronization stability.

---

# Multi-Company Architecture

The system is company-aware.

Current business rule:

* Each company can only view its own Controllers.
* Each Controller belongs to exactly one company.
* Devices inherit visibility from their Controller.
* Users should only access records associated with their company.

Expected navigation flow:

Company
→ Controllers
→ Devices

When opening a Controller record, users should be able to view Devices managed by that Controller.

---

# Naming Conventions

## Model Names

All business models MUST start with:

```python
t4.gate_keeper
```

Examples:

```python
t4.gate_keeper.controller
t4.gate_keeper.device
t4.gate_keeper.access_log
t4.gate_keeper.command
```

Do NOT create models outside this namespace unless explicitly approved.

---

## Python Classes

Use descriptive class names.

Examples:

```python
class GateKeeperController(models.Model):
    ...
```

```python
class GateKeeperDevice(models.Model):
    ...
```

---

## XML IDs

Use module-prefixed XML IDs.

Examples:

```xml
t4_gate_keeper.view_controller_tree
t4_gate_keeper.view_controller_form
t4_gate_keeper.action_controller
t4_gate_keeper.menu_controller
```

---

## Files

Use snake_case naming.

Examples:

```text
gk_controller.py
gk_device.py
gk_controller_sync_views.xml
gk_device_model_views.xml
security.xml
ir.model.access.csv
```

---

# Development Rules

## Approval Required

The AI assistant MUST NOT:

* Modify existing architecture.
* Rename models.
* Rename fields.
* Modify security rules.
* Modify record rules.
* Modify access rights.
* Create new dependencies.
* Change manifest configuration.
* Change database structure.

without explicit approval from the developer.

When a modification affects architecture or existing behavior, the assistant must first explain:

1. What will change.
2. Why it is needed.
3. Potential side effects.

Implementation should only proceed after approval.

**CRITICAL RULE:** The AI assistant MUST ALWAYS ask for the developer's explicit agreement before modifying ANY files. Do not proceed with any file modifications until the developer confirms.

---

## Backward Compatibility

All generated code must preserve existing functionality unless the developer explicitly requests breaking changes.

Avoid introducing changes that require data migration unless approved.

---

## Minimal Changes Principle

When fixing bugs:

* Prefer the smallest possible change.
* Avoid refactoring unrelated code.
* Avoid changing coding style in untouched areas.
* Avoid moving files unless necessary.

---

# Language Rules

## Source Code

All generated code must be written in English.

Including:

* Variable names
* Class names
* Method names
* Comments
* Docstrings
* Error messages
* Log messages

Example:

```python
raise ValidationError(_("Controller is offline"))
```

---

## Translation

Every user-facing string must be translatable.

Use:

```python
from odoo import _
```

Example:

```python
_("Controller is offline")
```

An equivalent Vietnamese translation must be provided through i18n files.

Expected:

```text
i18n/
└── vi.po
```

No hardcoded Vietnamese text inside Python source code.

---

# Odoo Development Standards

## ORM First

Always use the Odoo ORM.

Preferred:

```python
self.env['t4.gate_keeper.device'].search(...)
```

Avoid direct SQL unless:

* Performance issue is proven.
* ORM cannot solve the problem.

---

## Security

Never use:

```python
sudo()
```

unless explicitly justified.

When using `sudo()`, document the reason.

---

## Record Rules

Multi-company rules must be respected.

Generated code should not bypass company restrictions.

---

## Logging

Use logging for important operations.

Example:

```python
import logging

_logger = logging.getLogger(__name__)
```

Avoid excessive logging.

Do not log sensitive information.

---

# View Standards

## Tree Views

List views should display:

* Name
* Company
* Status
* Create Date

when applicable.

---

## Form Views

Group fields logically.

Example:

* General Information
* Connection Information
* Hardware Information
* Audit Information

---

# Data Integrity

Use:

* required=True
* SQL constraints
* Python constraints

where appropriate.

Avoid storing duplicated information.

Use relations whenever possible.

---

# Testing Expectations

New features should include:

* Security validation
* Multi-company validation
* Business rule validation

Generated code should not assume administrator access.

---

# Documentation

Every new model should contain:

```python
_name
_description
```

Example:

```python
_name = "t4.gate_keeper.controller"
_description = "Gate Keeper Controller"
```

Complex business logic should include concise comments.

---

# MVP Scope

Current MVP includes:

* Controller Management
* Device Management
* Company Ownership
* Controller → Device Relationship

Features outside MVP should not be implemented unless requested.

Examples:

* Attendance
* Visitor Management
* Access Scheduling
* Facial Recognition
* Mobile Applications
* Real-time Monitoring Dashboards

These features may be introduced later and should not influence current design decisions.

---

# AI Assistant Behavior

Before generating code:

1. Understand the existing architecture.
2. Reuse existing patterns.
3. Preserve backward compatibility.
4. Respect multi-company rules.
5. Ask for approval before structural changes.

When uncertain, prefer asking questions rather than making architectural assumptions.

The AI assistant acts as a contributor, not an architect. Final architectural decisions belong to the developer.


# API Development Standards

## API Framework

This project is built on top of the internal framework:

```python
odoo.addons.t4_coreapi
```

The `t4_coreapi` module is responsible for:

* Endpoint registration
* Request routing
* Request parsing
* Response handling
* API lifecycle management

Developers must follow the conventions defined by this framework.

Do not create custom HTTP controllers unless explicitly approved.

Preferred approach is always to use the API abstraction provided by `t4_coreapi`.

---

## Endpoint Declaration

Endpoints must be declared using the decorator:

```python
from odoo.addons.t4_coreapi.utils import endpoint
```

Example:

```python
@endpoint(name="Testing")
def test(self):
    pass
```

Do not manually expose routes when the endpoint decorator can be used.

---

## Request Data Access

Request data must be obtained through helper functions provided by `t4_coreapi`.

```python
from odoo.addons.t4_coreapi.utils import (
    get_body,
    get_params,
)
```

### Request Body

```python
body = get_body()
```

Used for:

* POST payload
* JSON payload
* Request body content

Example:

```python
controller_id = get_body().get("controller_id")
```

---

### Query Parameters

```python
params = get_params()
```

Used for:

* URL parameters
* Query string values

Example:

```python
device_id = get_params().get("device_id")
```

---

## Standard Endpoint Example

```python
from odoo import models
from odoo.addons.t4_coreapi.utils import (
    endpoint,
    get_body,
)

import logging

_logger = logging.getLogger(__name__)


class GateKeeperController(models.Model):
    _name = "t4.gate_keeper.controller"
    _description = "Gate Keeper Controller"

    @endpoint(name="Testing")
    def test(self):
        controller_name = get_body().get(
            "controller_id"
        )

        _logger.warning(
            "CONTROLLER: %s",
            controller_name
        )

        if controller_name:
            self.create({
                "controller_name": controller_name
            })
```

---

## Endpoint Naming Convention

Endpoint names should:

* Be descriptive.
* Use English.
* Represent business actions.
* Remain stable after deployment.

Good examples:

```text
ControllerHeartbeat
ControllerRegister
DeviceSync
DeviceStatus
DeviceEvent
AccessLogUpload
```

Avoid:

```text
Test
Test1
ABC
DemoEndpoint
```

unless used temporarily during development.

---

## API Business Logic

Business logic should remain inside models.

Avoid:

* Direct SQL
* Controller-style procedural code
* Massive endpoint methods

Endpoint methods should:

1. Read request data.
2. Validate request data.
3. Call business methods.
4. Return response.

Example:

```python
@endpoint(name="ControllerHeartbeat")
def controller_heartbeat(self):
    body = get_body()

    return self._process_heartbeat(body)
```

---

## Endpoint Response Structure

The endpoint registration and decoration layer automatically handles response formatting:

### 1. Non-dictionary Return Values
If the endpoint method returns a value that is NOT a dictionary (e.g., a List, String, Boolean, etc.), the framework wraps it into a standard success response where the returned value is assigned to the `data` field:
```json
{
    "success": true,
    "message": "Successful",
    "data": <returned_value>
}
```

### 2. Dictionary Return Values
If the endpoint method returns a dictionary:
- The framework attempts to extract `"data"` and `"message"` keys using `.get()`.
- If **neither** key is found in the dictionary, the entire returned dictionary is treated as the `"data"` payload.
- If **at least one** of `"data"` or `"message"` is found, the framework uses the provided values for the JSON response keys.

---

## Validation Rules

All endpoint inputs should be validated.

Required fields:

```python
controller_id
device_id
company_id
```

must be checked before processing.

Do not assume external hardware sends valid data.

---

## Logging Rules

Incoming requests may be logged for troubleshooting.

Never log:

* Passwords
* Access tokens
* Authentication secrets
* Sensitive biometric data

Allowed:

```python
_logger.info(
    "Heartbeat received from controller %s",
    controller_id
)
```

---

## Error Handling

Never expose Python tracebacks to API consumers.

Use business-friendly error messages.

Bad:

```python
KeyError: controller_id
```

Good:

```python
{
    "success": false,
    "message": "Controller identifier is required."
}
```

---

## Gate Keeper API Philosophy

The T4 Gate Keeper module should not be responsible for:

* HTTP routing
* Request parsing
* Generic API infrastructure

Those responsibilities belong to `t4_coreapi`.

The responsibility of `t4_gate_keeper` is only:

* Controller management
* Device management
* Access-control business logic
* Hardware communication workflows
* Company-based data ownership

```
```


# ADDONS

## Area Warnings Management

To allow users to monitor security events at a high logical level (Area level) rather than inspecting raw access logs, the system includes a dedicated warnings mechanism:

### 1. Area Warning Model (`t4.gate_keeper.area_warning`)
Tracks lifecycle-bound, actionable warnings at the Area level.
* **Fields**:
  * `area_id`: Linked Area (Many2one, required).
  * `device_id`: Source device (Many2one).
  * `employee_id`: Violated employee (Many2one).
  * `access_log_id`: Related raw Access Log (Many2one).
  * `warning_type_id`: Type of warning configuration record (Many2one, required, linked to `t4.gate_keeper.area_warning_type`).
  * `description`: Auto-generated violation detail text.
  * `state`: Status of warning (`active` or `resolved`).
  * `resolved_by_id`: User who cleared the warning (Many2one).
  * `resolved_at`: Datetime of resolution.
  * `resolution_notes`: Reviewer's notes.
* **Methods**:
  * `action_resolve()`: Marks specific warning records as resolved.

### 2. Area Warning Type Model (`t4.gate_keeper.area_warning_type`)
Database-driven category configuration for warnings. The system bootstraps exactly two standard types:
* `invalid_access`: Unauthorized access or access outside standard branch working hours.
* `device_issue`: Connection issues (device offline, controller offline).

### 3. Area Status Compute (`t4.gate_keeper.area`)
* `status` is a stored compute field that depends on `warning_ids.state`.
* If any warning in the area is `warning` (active), `status` evaluates to `warning` (represented as a yellow/orange badge).
* Resolving warnings resets the Area status back to `normal`.

### 4. Access Log Hook & Rule Engine (`t4.gate_keeper.access_log`)
* `area_id` is a related stored field.
* On record creation (`create()`), a timezone-aware hook checks if the `access_time` falls outside standard working hours (08:00 - 17:00) or on weekends using the branch's local timezone.
* If a violation is detected, an active `t4.gate_keeper.area_warning` of type `invalid_access` is generated.

### 5. Automated Device & Controller status triggers
* When a Device (`t4.gate_keeper.device`) status changes to `offline` or `controller_offline`: if it is in an Area, an active warning of type `device_issue` is automatically created (unless one already exists).
* When a Device status changes to `online`: all active `device_issue` warnings for the device are resolved.
* When a Controller (`t4.gate_keeper.controller`) status changes to `online`: it cascades `online` status to all parented devices that were in `controller_offline` state.
* When a Controller status changes to anything other than `online`: it cascades `controller_offline` status to all parented devices that were not already in `controller_offline` state.

## Branch Timezone Synchronization

To ensure physical locations correctly evaluate time checks, the system is timezone-aware at the Branch level:

### 1. Branch Timezone Field (`t4.gate_keeper.branch`)
* Added `timezone` field to configure the geographical timezone of each Branch using standard `pytz.common_timezones` (e.g. `Asia/Ho_Chi_Minh`, `Asia/Tokyo`).

### 2. Controller & Device Synchronization
* Both Controllers (`t4.gate_keeper.controller`) and Devices (`t4.gate_keeper.device`) synchronize timezone configuration from their parent Branch:
  * `timezone` is a stored, related Selection field (`related="branch_id.timezone", store=True`).
  * When a Branch's timezone is updated, Odoo's dependency engine automatically updates the timezone for all child Controllers and Devices.
