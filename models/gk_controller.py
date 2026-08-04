import logging

# pyrefly: ignore [missing-import]
from odoo import api, _, fields, models
# pyrefly: ignore [missing-import]
from odoo.addons.t4_coreapi.utils import endpoint, get_body
# pyrefly: ignore [missing-import]
from odoo.exceptions import ValidationError


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
    _order = "last_heartbeat_at desc, id desc"

    name = fields.Char(
        string="Controller Name",
        required=True,
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

    last_heartbeat_at = fields.Datetime(
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
    def _find_controller(self, controller_id):
        return self.search([
            ("serial_number", "=", controller_id),
        ], limit=1)
    
    def _find_device(self, controller_id, device_id):
        return self.env["t4.gate_keeper.device"].search([
            ("serial_number", "=", device_id),
            ("controller_id", "=", controller_id),
        ], limit=1)
    

    @endpoint(name="ControllerHeartbeat")
    def controller_heartbeat(self):
        body = get_body(self.env)
        controller_id = body.get("controller_sn", False)

        controller = self._find_controller(controller_id)
        if not controller:
            raise ValidationError(f"Can not find controller with id {controller_id}")
        devices = body.get("devices", [])
        # if not devices:
        #     raise ValidationError("Devices list is required.")
        for device in devices:
            device_id = device.get("device_sn")
            device_status = device.get("status")
            if not device_id:
                raise ValidationError("Device serial number is required.")

            if not device_status:
                raise ValidationError(f"Device status is required for device {device_id}")
            
            allowed_status = dict(self.env["t4.gate_keeper.device"]._fields["status"].selection).keys()
            if device_status not in allowed_status:
                raise ValidationError(f"Invalid device status for device {device_id}")

            if not device_id or not device_status:
               continue
            
            device_record = self._find_device(controller.id, device_id)
            if device_record:
                device_record.write({"status": device_status})



        heartbeat_at = fields.Datetime.now()
        controller.write({
            "last_heartbeat_at": heartbeat_at,
            "status": "online",
        })


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
                                "template": bio.template,
                                "finger_index/slot": bio.finger_index
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
                                "template": bio.template,
                                "finger_index/slot": bio.finger_index
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
                                "template": bio.template,
                                "finger_index/slot": bio.finger_index
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

    #### Register 

    @endpoint("ControllerStatus")
    def _controller_status(self):
        body = get_body()
        serial_number = body.get("serial_number")

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
            raise ValidationError("Missing required fields (serial_number, branch_id)")

        if not userInfo_vals['branch_id']:
            raise ValidationError("Invalid branch_code provided")   

        new_controller = self.env['t4.gate_keeper.controller'].sudo().create(userInfo_vals)

        return {
            "message": "Controller registered successfully",
            "data": {
                "id": new_controller.id
            }
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
                template = biometric.template.decode() if biometric.template else None

                if biometric.biometric_type == "fingerprint":
                    finger_templates.append(template)
                elif biometric.biometric_type == "face":
                    face_templates = template
            

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

        userInfo_vals ={
            "emp_id": emp_id
        }

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
            employee = self.env["t4.gate_keeper.employee"].create(userInfo_vals)

        ###Fingerprint
        fingerprint = body.get("FP", [])
        if fingerprint:
            for fp in fingerprint:
                finger = self.env["t4.gate_keeper.employee.biometric"].search([
                    ("employee_id", "=", employee.id),
                    ("biometric_type", "=", "fingerprint"),
                    ("finger_index", "=", fp["FID"])
                ], limit = 1)
                finger_vals = {
                    "employee_id": employee.id,
                    "biometric_type": "fingerprint",
                    "finger_index": fp["FID"],
                    "template": fp["TMP"]
                }
                if finger:
                    finger.write(finger_vals)
                else:
                    self.env["t4.gate_keeper.employee.biometric"].create(finger_vals)
        ###BIODATA
        biodata = body.get("BIODATA", {})
        if biodata:
            face = self.env["t4.gate_keeper.employee.biometric"].search([
                ("employee_id", "=", employee.id),
                ("biometric_type", "=", "face"),
                ("finger_index", "=", biodata["Index"])
            ], limit = 1)
            biodata_vals = {
                "employee_id": employee.id,
                "biometric_type": "face",
                "finger_index": biodata["Index"],
                "template": biodata["Tmp"]
            }
            if face:
                face.write(biodata_vals)
            else:
                self.env["t4.gate_keeper.employee.biometric"].create(biodata_vals)
        ###PHOTO
        photo = body.get("PHOTO", {})
        if photo and photo.get("Content"):
            employee.write({
                "avatar": photo["Content"]
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


