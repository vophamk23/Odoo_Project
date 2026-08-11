import logging
from tempfile import template
from typing import Any
from datetime import datetime

# pyrefly: ignore [missing-import]
from odoo import api, _, fields, models
# pyrefly: ignore [missing-import]
from odoo.addons.t4_coreapi.utils import endpoint, get_body, set_response
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError
import json


_logger = logging.getLogger(__name__)


CONTROLLER_STATUS = [
    ("online", "Online"),
    ("offline", "Offline"),
    ("maintenance", "Maintenance"),
    ("disabled", "Disabled"),
]


ALLOWED_FIELDS = [  # fields of t4 gatekeeper controller if you add or delete pls change this list
    'name', 
    'serial_number', 
    'branch_id', 
    'hardware_model', 
    'firmware_version', 
    'ip_address', 
    'mac_address', 
    'connection_type', 
    'status', 
    'installed_at'
]

class T4GateKeeperController(models.Model):
    _name = "t4.gate_keeper.controller"
    _description = "Gate Keeper Controller"
    _order = "last_heartbeat desc, id desc"

    name = fields.Char(
        string="Controller Name",
        help="Human-readable name used to identify this controller.",
    )

    serial_number = fields.Char(
        string="Serial Number",
        required=True,
        copy=False,
        index=True,
        help="Physical serial number used for maintenance and hardware replacement checks.",
    )

    branch_id = fields.Many2one(
        "t4.gate_keeper.branch",
        string="Branch",
        required=True,
        index=True,
    )

    timezone = fields.Selection(
        related="branch_id.timezone",
        string="Timezone",
        readonly=True,
        store=True,
    )


    device_ids = fields.One2many(
        "t4.gate_keeper.device",
        "controller_id",
        string="Devices",
    )

    hardware_model = fields.Char(
        string="Hardware Model",
        help="Controller model or product line.",
    )

    firmware_version = fields.Char(
        string="Firmware Version",
        help="Firmware version installed on the controller.",
    )

    ip_address = fields.Char(
        string="IP Address",
        help="Connection address when the controller uses TCP/IP.",
    )

    mac_address = fields.Char(
        string="MAC Address",
        help="Hardware identifier useful when DHCP changes the IP address.",
    )

    connection_type = fields.Selection(
        selection=[
            ("tcp_ip", "TCP/IP"),
            ("rs485", "RS485"),
            ("wiegand", "Wiegand"),
        ],
        string="Connection Type",
        required=True,
        default="tcp_ip",
        help="Communication method used by this controller.",
    )

    status = fields.Selection(
        selection=CONTROLLER_STATUS,
        string="Status",
        default="offline",
        tracking=True,
    )

    last_heartbeat = fields.Datetime(
        string="Last Heartbeat",
        readonly=True,
        help="Last time this controller reported that it was online.",
    )

    last_sync_at = fields.Datetime(
        string="Last Sync",
        readonly=True,
        help="Last successful permission or template synchronization.",
    )

    installed_at = fields.Date(
        string="Installed On",
        help="Installation date used for maintenance planning.",
    )

    employee_sync_status = fields.Selection(
        selection=[
            ("synced", "Synced"),
            ("out_of_sync", "Out of Sync"),
        ],
        string="Employee Sync Status",
        compute="_compute_employee_sync_status",
        help="Indicates whether the controller has synchronized the latest employee updates.",
    )

    def _compute_employee_sync_status(self):
        for controller in self:
            domain = controller._get_employee_sync_domain(controller)
            unsynced_count = self.env["t4.gate_keeper.employee"].search_count(domain)
            if unsynced_count == 0:
                controller.employee_sync_status = "synced"
            else:
                controller.employee_sync_status = "out_of_sync"

    _controller_serial_number_unique = models.Constraint(
        "UNIQUE(serial_number)",
        _("Controller serial number must be unique.")
    )

    ################################## ENDPOINT ###############################################
    # heart beat
    def _find_controller(self, serial_number):
        return self.search([
            ("serial_number", "=", serial_number),
        ], limit=1)

    def _find_devices(self, controller_id, device_sns):
        return self.env['t4.gate_keeper.device'].search([
            ("controller_id", "=", controller_id),
            ("serial_number", "in", device_sns),
        ])

    def _find_device_by_name(self, controller_id, device_name):
        return self.env['t4.gate_keeper.device'].search([
            ("controller_id", "=", controller_id),
            ("name", "=", device_name),
        ], limit=1)

    
    @api.model
    def set_response(self, message: str, status_code: int, **kwargs: Any) -> bool:
        set_response(
            data=kwargs,
            message=message,
            status_code=status_code
        )
        return False

    @endpoint(name="Heartbeat")
    def controller_heartbeat(self):
        body = get_body(self.env)
        controller_sn = body.get("controller_sn", False)

        controller = self._find_controller(controller_sn)
        if not controller:
            return self.set_response(
                message="invalid controller",
                status_code=400,
                is_missing=True,
                missing_controller_sn=controller_sn,
                missing_device_sns=False,
                )

        device_sns = body.get("device_sns", [])
        devices = self._find_devices(controller.id, device_sns)

        found_serials = devices.mapped('serial_number')

        missing_serials = set(device_sns) - set(found_serials)

        if missing_serials:
            return self.set_response(
                message="invalid controller",
                status_code=400,
                is_missing=True,
                missing_controller_sn=False,
                missing_device_sns=list(missing_serials),
            )


        heartbeat_at = fields.Datetime.now()
        vals = {
            "last_heartbeat": heartbeat_at,
            "status": "online",
        }
        controller.write(vals)
        devices.write(vals)

        return self.set_response(
                message="success",
                status_code=200,
                is_missing=False,
                missing_controller_sn=False,
                missing_device_sns=False,
        )

    # Employee Sync
    @endpoint(name="ControllerEmployeeSync")
    def controller_employee_sync(self):
        body = get_body()
        serial_number = body.get("controller_sn", False)

        if not serial_number:
            raise ValidationError(_("Controller ID is required."))

        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(_("Can not find controller with ID %s") % serial_number)
        
              
        last_sync = body.get("last_sync_at", False)
        if last_sync:
            try:
                last_sync = fields.Datetime.to_datetime(last_sync)
            except ValueError:
                raise ValidationError(_("Invalid last sync time format. Expected YYYY-MM-DD HH-MM-SS"))
        
        try:
            page_size = int(body.get("page_size", 15))
        except:
            raise ValidationError(_("Invalid page size"))
        
        if page_size < 1:
            raise ValidationError(_("Invalid page size"))
        
        cursor_id = body.get("next_cursor_id")
        cursor_write_date = body.get("latest_write_date")

        if cursor_write_date:
            try:
                cursor_write_date = fields.Datetime.to_datetime(cursor_write_date)
            except ValueError:
                raise ValidationError(_("Invalid latest_write_date"))


        if cursor_id:
            try:
                cursor_id = int(cursor_id)
            except ValueError:
                raise ValidationError(_("Invalid cursor id"))
        
        if not last_sync:
            domain = self._get_employee_sync_domain(controller)
        else:
            domain = self._get_employee_sync_domain(controller, last_sync_at=last_sync)

        if cursor_id and cursor_write_date:
            domain +=[
                "|",
                    ("write_date", ">", cursor_write_date),
                "&",
                    ("write_date", "=", cursor_write_date),
                    ("id", ">", cursor_id)
            ]

        employee = self._get_employees_to_sync(domain, limit=page_size + 1)
        if employee:
            latest_write_date = max(employee.mapped("write_date"))
        else:
            latest_write_date = fields.Datetime.now()

        has_next_page = len(employee) > page_size

        if has_next_page:
            employee = employee[:page_size]

        next_cursor = None
        if has_next_page and employee:
            last = employee[-1]
            next_cursor = last.id
            
        new = []
        update = []
        deleted = []
        for emp in employee:
            if not emp.active:
                deleted.append(emp)
            elif not last_sync:
                new.append(emp)
            elif emp.create_date > last_sync:
                new.append(emp)
            else:
                update.append(emp)

        data = {
            "data": {
                "next_cursor_id": next_cursor,
                "has_next_page": has_next_page,
                "new": [
                        {
                        "id": emp.emp_id,
                        "name": emp.name,
                        "branch_id": emp.branch_id.id if emp.branch_id else None,
                        "biometrics": [
                            {
                                "type": bio.biometric_type,
                                "template": bio.binary_template.decode() if bio.binary_template else bio.char_template,
                                "index": bio.finger_index,
                                "photo_avatar": emp.avatar,
                            }
                            for bio in emp.biometric_ids
                        ]
                    }
                    for emp in new
                ],
                "update": [
                    {
                        "id": emp.emp_id,
                        "name": emp.name,
                        "branch_id": emp.branch_id.id if emp.branch_id else None,
                        "biometrics": [
                            {
                                "type": bio.biometric_type,
                                "template": bio.binary_template.decode() if bio.binary_template else bio.char_template,
                                "index": bio.finger_index,
                                "photo_avatar": emp.avatar,
                            }
                            for bio in emp.biometric_ids
                        ]
                    }
                    for emp in update
                ],
                "deleted": [
                    {
                        "id": emp.emp_id,
                        "name": emp.name,
                        "branch_id": emp.branch_id.id if emp.branch_id else None,
                        "biometrics": [
                            {
                                "type": bio.biometric_type,
                                "template": bio.binary_template.decode() if bio.binary_template else bio.char_template,
                                "index": bio.finger_index,
                                "photo_avatar": emp.avatar,
                            }
                            for bio in emp.biometric_ids
                        ]
                    }
                    for emp in deleted
                ],
                "latest_write_date": latest_write_date.strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        return{
            "message": _("Employee sync completed"),
            "data": data
        }
    

    def write(self, userInfo_vals):
        res = super(T4GateKeeperController, self).write(userInfo_vals)
        if 'status' in userInfo_vals:
            for controller in self:
                if controller.status == 'online':
                    devices_to_update = controller.device_ids.filtered(lambda d: d.status == 'controller_offline')
                    if devices_to_update:
                        devices_to_update.write({'status': 'online'})
                else:
                    devices_to_update = controller.device_ids.filtered(lambda d: d.status != 'controller_offline')
                    if devices_to_update:
                        devices_to_update.write({'status': 'controller_offline'})
        return res

    def _get_employee_sync_domain(self, controller, last_sync_at=None):
        domain = [
            '|', 
            ('branch_id', '=', False), 
            ('branch_id', '=', controller.branch_id.id)
        ]

        if last_sync_at:
            domain.append(('write_date', '>', last_sync_at))
            
        return domain

    def _get_employees_to_sync(self, domain, offset=0, limit=None):
        return self.env["t4.gate_keeper.employee"].search(domain,
                                                          order="write_date, id",
                                                          offset=offset,
                                                          limit=limit)

    def _get_employee_biometric_algorithms(self, algorithm, employee, device_model, index):

        algorithm_type = self.env["t4.gate_keeper.algorithm"].search([("name", "=", algorithm)], limit=1)
        if not algorithm_type:
            raise ValidationError(_("Algorithm type %s not found") % algorithm)

        biometric_domain = [
            ("employee_id", "=", employee.emp_id),
            ("algorithm_id", "=", algorithm_type.id),
            ("device_model_id", "=", device_model.id)
        ]

        if index is not None:
            biometric_domain.append((
                "finger_index", "=", index
            ))

        return self.env["t4.gate_keeper.employee.biometric"].search(biometric_domain, limit = 1)

    #### Register 
    @endpoint("ControllerStatus")
    def _controller_status(self):
        body = get_body()
        serial_number = body.get("controller_sn")

        if not serial_number:
            raise ValidationError(_("Serial number is required."))

        controller = self.sudo().search_read(
            [("serial_number", "=", serial_number)],
            ["id", "serial_number"],
            limit=1
        )

        if not controller:
            return {
                "message": "Controller not found.",
                "data": {
                    "is_registered": False,
                }
            }

        controller_id = controller[0]["id"]
        
        devices = self.env["t4.gate_keeper.device"].sudo().search_read(
            [("controller_id", "=", controller_id)],
            ["serial_number"]
        )

        return {
            "message": "Success.",
            "data": {
                "is_registered": True,
                "controller_sn": controller[0]["serial_number"],
                "devices": [d["serial_number"] for d in devices if d.get("serial_number")]
            }
        }

    def _find_branch_by_code(self, branch_code):
        return self.env['t4.gate_keeper.branch'].sudo().search([
            ("code", "=", branch_code)
        ], limit=1)

    @endpoint("ControllerRegister")
    def _controller_register(self):
        body = get_body()

        if "branch_code" in body:
            branch_code = body.pop("branch_code")
            body["branch_id"] = self._find_branch_by_code(branch_code).id

        userInfo_vals = {key: body[key] for key in ALLOWED_FIELDS if key in body}    

        if 'serial_number' not in userInfo_vals or 'branch_id' not in userInfo_vals:
            raise ValidationError("Missing required fields (serial_number, branch_id, name)")

        if not userInfo_vals['branch_id']:
            raise ValidationError("Invalid branch_code provided")   

        new_controller = self.env['t4.gate_keeper.controller'].sudo().create(userInfo_vals)

        return {
            "message": "Controller registered successfully"
        }

    @endpoint('DeviceRegister')
    def _device_register(self):
        body = get_body()
        userInfo_vals_list = body['devices']

        self.env['t4.gate_keeper.device']._device_register(userInfo_vals_list)

        return {
            "message": "Devices register successfully"
        }

    ##### Biometric
    @endpoint(name="EmployeeBiometricGet")
    def employee_biometric_get(self):
        body = get_body()
        serial_number = body.get("controller_sn", False)

        if not serial_number:
            raise ValidationError(_("Controller ID is required."))

        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(_("Can not find controller with ID %s") % serial_number)
        
        employee_id = body.get("emp_id", False)
        if not employee_id:
            raise ValidationError(_("Employee ID is required."))

        employee = self.env["t4.gate_keeper.employee"].search([
            ("emp_id", "=", employee_id),
            "|", 
            ("branch_id", "=", False), 
            ("branch_id", "=", controller.branch_id.id)
        ], limit=1)

        finger_templates = []
        face_templates = None
        if employee:
            for biometric in employee.biometric_ids:
                template = biometric.binary_template if biometric.binary_template else biometric.char_template
                if biometric.algorithm_id.name == "fingerprint":
                    finger_templates.append({
                        "index": biometric.finger_index,
                        "template": template if template else None
                    })
                elif biometric.algorithm_id.name == "face":
                    face_templates = template if template else None
        if employee:
            _logger.info("========== EMPLOYEE BIOMETRIC DEBUG ==========")
            _logger.info("Employee ID: %s", employee.id)
            _logger.info("Employee emp_id: %s", employee.emp_id)
            _logger.info("Biometric count: %s", len(employee.biometric_ids))

            for biometric in employee.biometric_ids:
                template = (
                    biometric.binary_template
                    if biometric.binary_template
                    else biometric.char_template
                )

                _logger.info("----------------------------------------")
                _logger.info("Biometric ID       : %s", biometric.id)
                _logger.info("Biometric type     : %r", biometric.biometric_type)
                _logger.info(
                    "Algorithm ID       : %s",
                    biometric.algorithm_id.id if biometric.algorithm_id else None
                )
                _logger.info(
                    "Algorithm name     : %r",
                    biometric.algorithm_id.name if biometric.algorithm_id else None
                )
                _logger.info("Finger index       : %r", biometric.finger_index)
                _logger.info(
                    "Binary template    : %s",
                    "EXISTS" if biometric.binary_template else "EMPTY"
                )
                _logger.info(
                    "Char template      : %s",
                    "EXISTS" if biometric.char_template else "EMPTY"
                )
                _logger.info("Template type      : %s", type(template))
                _logger.info(
                    "Template length    : %s",
                    len(template) if template else 0
                )
                _logger.info(
                    "Template preview   : %s",
                    template[:100] if template else None
                )

                if biometric.algorithm_id.name == "fingerprint":
                    _logger.info(">>> MATCH FINGERPRINT")

                elif biometric.algorithm_id.name == "face":
                    _logger.info(">>> MATCH FACE")

                else:
                    _logger.warning(
                        ">>> NO MATCH: algorithm_name=%r",
                        biometric.algorithm_id.name if biometric.algorithm_id else None
                    )

            _logger.info("==============================================")


        return {
            "message": _("Success"),
            "data": {
                "emp_id": employee.emp_id,
                "finger_templates": finger_templates,
                "face_template": face_templates,
                "photo_avatar": employee.avatar.decode() if employee.avatar else None,
            }
        }
    
    @endpoint(name="EmployeeBiometricUpdate")
    def employee_biometric_update(self):
        body = get_body()
        serial_number = body.get("controller_sn", False)

        if not serial_number:
            raise ValidationError(_("Controller ID is required."))

        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(_("Can not find controller with ID %s") % serial_number)
        device_sn = body.get("device_sn", False)
        if not device_sn:
            raise ValidationError(_("Device serial number is required."))
        device = self._find_devices(controller.id, device_sn)
        if not device:
            raise ValidationError(_("Can not find device with serial number %s") % device_sn)
        device_model = device.device_model_id
        if not device_model:
            raise ValidationError(_("Device %s does not have a model assigned") % device_sn)
        ###User
        userInfo = body.get("USER", {})
        if not userInfo:
            raise ValidationError(_("User information is required"))
        emp_id = userInfo.get("PIN", False)
        if not emp_id:
            raise ValidationError(_("Missing employee id"))
        employee = self.env["t4.gate_keeper.employee"].search([
            ("emp_id", "=", emp_id),
            "|",
            ("branch_id", "=", False),
            ("branch_id", "=", controller.branch_id.id),
        ], limit=1)

        userInfo_vals ={}

        if controller.branch_id:
            userInfo_vals["branch_id"] = controller.branch_id.id
        
        if userInfo.get("Name"):
            userInfo_vals["name"] = userInfo["Name"]

        if userInfo.get("Passwd"):
            userInfo_vals["password"] = userInfo["Passwd"]
        
        if userInfo.get("Card"):
            userInfo_vals["card_id"] = userInfo["Card"]

        if userInfo.get("Pri"):
            userInfo_vals["privilege"] = userInfo["Pri"]

        if employee:
            employee.write(userInfo_vals)
        else:
            userInfo_vals["emp_id"] = emp_id
            employee = self.env["t4.gate_keeper.employee"].create(userInfo_vals)
        #(cần gửi thêm device sn để xác định device_model_id)
        ###Fingerprint 
        fingerprint = body.get("FP", [])
        if fingerprint:
            for fp in fingerprint:
                finger_index = fp.get("FID")
                if finger_index is None:
                    raise ValidationError(_("Missing finger index for fingerprint template"))

                finger_biometric = self._get_employee_biometric_algorithms(
                    algorithm="fingerprint",
                    employee=employee,
                    device_model=device_model,
                    index=finger_index
                )
                if not finger_biometric:
                    raise ValidationError(_("No matching fingerprint biometric found for employee %s with finger index %s") % (employee.emp_id, finger_index))

                biometric_vals = {
                    "algorithm_id": finger_biometric.algorithm_id.id,
                    "employee_id": employee.id,
                    "biometric_type": "base64",
                    "finger_index": finger_index,
                    "binary_template": fp.get("TMP")
                }

                if finger_biometric:
                    finger_biometric.write(biometric_vals)
                else:
                    self.env["t4.gate_keeper.employee.biometric"].create(biometric_vals)
        ###BIODATA
        biodata = body.get("BIODATA", {})
        if biodata:
            biodata_slot = biodata.get("Index")
            face_biometric = self._get_employee_biometric_algorithms(
                algorithm="face",
                employee=employee,
                device_model=device_model,
                index=biodata_slot
            )
            if not face_biometric:
                raise ValidationError(_("No matching face biometric found for employee %s with slot index %s") % (employee.emp_id, biodata_slot))
            biometrics_vals = {
                "algorithm_id": face_biometric.algorithm_id.id,
                "employee_id": employee.id,
                "biometric_type": "base64",
                "finger_index": 0,
                "binary_template": biodata.get("Tmp")
            }
            if face_biometric:
                face_biometric.write(biometrics_vals)
            else:
                self.env["t4.gate_keeper.employee.biometric"].create(biometrics_vals)
        ###PHOTO
        photo = body.get("PHOTO", {})
        if photo and photo.get("Content"):
            employee.avatar = photo["Content"]
            attachment = self.env["ir.attachment"].search([
                ("res_model", "=", "t4.gate_keeper.employee"),
                ("res_field", "=", "avatar"),
                ("res_id", "=", employee.id)
            ], limit = 1)
            if attachment:
                attachment.write({
                    "name": photo["FileName"],
                    "photo_type": photo["Type"],
                })

        return {
            "message": _("Success")
        }
                


    
    #### Config
    @endpoint(name="ControllerGetConfig")
    def controller_get_config(self):
        body = get_body()
        serial_number = body.get("controller_sn", False)

        if not serial_number:
            raise ValidationError(_("Controller ID is required."))

        controller = self._find_controller(serial_number)
        if not controller:
            raise ValidationError(_("Can not find controller with ID %s") % serial_number)
        
        device_list = controller.device_ids
        device_data = []

        for device in device_list:
            device_data.append({
                "device_sn": device.serial_number,
                "device_model": device.device_model_id.name if device.device_model_id else "N/A",
                "assigned_area": device.area_id.name if device.area_id else "N/A",
                "status": device.status,
                "connection_type": device.connection_type,
                "port/channel": device.port_or_channel,
                "supported_biometric_types": [biometric.name for biometric in device.algorithm_ids],
            })

        return {
            "message": _("Success"),
            "timezone": controller.timezone,
            "data": {
                "devices": device_data
            }
        }


    #### Access Log
    @endpoint(name="AccessLogUpload")
    def controller_log(self):
        """
        Receive access log records from a controller.

        Expected body:
        {
            "controller_sn": "CTRL-001",
            "devices": [
                {
                    "device_sn": "DEV-001",
                    "records": [
                        {
                            "emp_id": 1,
                            "punch_type": "check_in",
                            "verify_mode": "face",
                            "punched_at": "2026-08-05T07:30:00+07:00"
                        }
                    ]
                }
            ]
        }
        """
        body = get_body()
        controller_sn = body.get("controller_sn")

        if not controller_sn:
            raise ValidationError(_("Controller serial number is required."))

        controller = self._find_controller(controller_sn)
        if not controller:
            raise ValidationError(
                _("Controller with serial number '%s' is not registered.") % controller_sn
            )

        devices_data = body.get("devices") or []
        if not devices_data:
            return {"message": _("No device data provided.")}

        DeviceObj = self.env["t4.gate_keeper.device"]
        EmployeeObj = self.env["t4.gate_keeper.employee"]
        AccessLogObj = self.env["t4.gate_keeper.access_log"]

        # Direction mapping
        DIRECTION_MAP = {
            "check_in": "in",
            "check_out": "out",
        }

        # Allowed verification types from the model
        ALLOWED_VERIFY_TYPES = {"face", "fingerprint", "card", "password", "other"}

        created_count = 0
        errors = []

        for device_data in devices_data:
            device_sn = device_data.get("device_sn")
            if not device_sn:
                errors.append(_("Skipped device entry with missing serial number."))
                continue

            device = DeviceObj.search([
                ("serial_number", "=", device_sn),
                ("controller_id", "=", controller.id),
            ], limit=1)

            if not device:
                errors.append(
                    _("Device '%s' is not registered under controller '%s'.") % (device_sn, controller_sn)
                )
                continue

            records = device_data.get("records") or []
            log_vals_list = []

            for rec in records:
                emp_id = rec.get("emp_id")
                if emp_id is None:
                    errors.append(_("Skipped record with missing emp_id on device '%s'.") % device_sn)
                    continue

                # emp_id is Integer in the system
                try:
                    emp_id_int = int(emp_id)
                except (ValueError, TypeError):
                    errors.append(_("Invalid emp_id '%s' on device '%s'.") % (emp_id, device_sn))
                    continue

                employee = EmployeeObj.search([("emp_id", "=", emp_id_int)], limit=1)
                if not employee:
                    errors.append(
                        _("Employee with ID '%s' not found. Skipped record on device '%s'.") % (emp_id, device_sn)
                    )
                    continue

                # Direction
                punch_type = rec.get("punch_type", "")
                direction = DIRECTION_MAP.get(punch_type, "unk")

                # Verification type
                verify_mode = rec.get("verify_mode", "")
                verification_type = verify_mode if verify_mode in ALLOWED_VERIFY_TYPES else "other"

                # Parse access time
                access_time = self._parse_access_time(rec.get("punched_at"))

                log_vals_list.append({
                    "controller_id": controller.id,
                    "device_id": device.id,
                    "employee_id": employee.id,
                    "access_time": access_time,
                    "direction": direction,
                    "verification_type": verification_type,
                    "sync_status": "success",
                })

            if log_vals_list:
                AccessLogObj.create(log_vals_list)
                created_count += len(log_vals_list)

        result = {
            "message": _("%d access log(s) created successfully.") % created_count,
            "data": {
                "created_count": created_count,
            },
        }

        if errors:
            result["data"]["warnings"] = errors

        _logger.info(
            "Access log upload from controller %s: %d records created, %d warnings",
            controller_sn, created_count, len(errors),
        )

        return result

    def _parse_access_time(self, raw_value):
        """
        Parse access time from various formats.
        Returns a naive UTC datetime string or falls back to now().
        """
        if not raw_value:
            return fields.Datetime.now()

        try:
            raw_str = str(raw_value)
            if "T" in raw_str:
                # ISO format: 2026-08-05T07:30:00+07:00
                dt = datetime.fromisoformat(raw_str.replace("Z", "+00:00"))
                if dt.utcoffset() is not None:
                    # Convert to naive UTC for Odoo storage
                    dt = (dt - dt.utcoffset()).replace(tzinfo=None)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Assume already in correct format
                return raw_value
        except Exception:
            _logger.warning("Failed to parse access time '%s', using current time.", raw_value)
            return fields.Datetime.now()
