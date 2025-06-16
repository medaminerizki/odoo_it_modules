# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ITDeviceModelBrand(models.Model):
    _name = 'it_device.brand'
    _description = 'IT device brand'
    _order = 'name asc'

    name = fields.Char(string='Brand name', required=True)
    image = fields.Binary("Logo", attachment=True,
                          help="This field holds the image used as logo for the brand, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized image", attachment=True,
                                 help="Medium-sized logo of the brand. It is automatically "
                                      "resized as a 128x128px image, with aspect ratio preserved. "
                                      "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
                                help="Small-sized logo of the brand. It is automatically "
                                     "resized as a 64x64px image, with aspect ratio preserved. "
                                     "Use this field anywhere a small image is required.")

class Category(models.Model):
    _name = 'category'
    _description = 'Device category'
    _order = 'name asc'

    name = fields.Char(string='Device category', required=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]

class PCDevice(models.Model):
    _name = 'pc_device.model'
    _description = 'Model of PC'
    _order = 'brand_id asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(compute="_compute_device_name", string='Name', store=True)
    model_name = fields.Many2one('pc_model.model', string='Model', domain="[('brand', '=', brand_id)]", required=True)
    brand_id = fields.Many2one('it_device.brand', 'Brand', required=True)
    category_ids = fields.Many2many('category', string='Tags')
    pc_sn = fields.Char(string="Serial No.", required=True)
    pc_os = fields.Many2one("pc_os.model", string="System")
    pc_os_licence = fields.Char(string="OS License")
    pc_password = fields.Char(string="PC Password")
    pc_cpu = fields.Many2one('pc_cpu.model', string="Processor")
    pc_memory = fields.Integer(string="Memory RAM (GB)")
    pc_hdd = fields.Boolean(string='HDD')
    pc_ssd = fields.Boolean(string='SSD')
    pc_hdd_capacity = fields.Integer(string='Capacity (GB)')
    pc_ssd_capacity = fields.Integer(string='Capacity (GB)')
    pc_hard_drive = fields.Integer(string="Hard Drive (GB)")
    pc_mac_addr = fields.Char(string="MAC Address")
    pc_curr_user = fields.Many2one('hr.employee', string="Current user")
    pc_prv_user = fields.Many2one('hr.employee', string="Previous user")
    pc_transfer_date = fields.Date(string="Date of transfer", default=fields.Date.today)
    pc_return_date = fields.Date(string="Date of return")
    pc_other = fields.Text(string="Other")
    pc_provider = fields.Many2one('res.partner', string="Provider")
    pc_provider_code = fields.Char(string='Provider code')
    pc_producer_code = fields.Char(string='Producer code')
    license_line = fields.One2many('license.model', 'pc_id', string='License Model', store=True, copy=True)
    accessories_line = fields.One2many('pc_add_accessories', 'pc_id', string='Additional accessories')
    device_id = fields.Many2one('it_devices.model', string='Device')
    image = fields.Binary(related='brand_id.image', string="Logo", readonly=False)
    image_medium = fields.Binary(related='brand_id.image_medium', string="Logo (medium)", readonly=False)
    image_small = fields.Binary(related='brand_id.image_small', string="Logo (small)", readonly=False)

    @api.depends('brand_id.name', 'model_name.name')
    def _compute_device_name(self):
        for record in self:
            record.name = f"{record.brand_id.name or ''} / {record.model_name.name or ''}"

    def name_get(self):
        res = []
        for record in self:
            name = record.model_name.name or ''
            if record.brand_id.name:
                name = f"{record.brand_id.name} / {name}"
            res.append((record.id, name))
        return res

    @api.onchange('brand_id')
    def _onchange_brand(self):
        if self.brand_id:
            self.image_medium = self.brand_id.image
        else:
            self.image_medium = False

    @api.onchange('pc_hdd', 'pc_ssd')
    def _default_value(self):
        if not self.pc_hdd:
            self.pc_hdd_capacity = False
        if not self.pc_ssd:
            self.pc_ssd_capacity = False

    @api.onchange('pc_curr_user')
    def auto_check_accessories(self):
        lines = [(5, 0, 0)]
        if self.device_id and self.pc_curr_user:
            for line in self.device_id.search([('curr_user', '=', self.pc_curr_user.name)]):
                val = {'device_id': line.id}
                lines.append((0, 0, val))
        self.accessories_line = lines

class PCAddAccessories(models.Model):
    _name = 'pc_add_accessories'
    _description = 'Additional PC Accessories'

    device_id = fields.Many2one('it_devices.model', string='Device')
    pc_id = fields.Many2one('pc_device.model', string='PC ID')

class PCOSModel(models.Model):
    _name = 'pc_os.model'
    _description = 'Model for devices operating systems.'
    _order = 'system asc'

    name = fields.Char(compute="_get_name", string="Name", readonly=True)
    system = fields.Char(string="System", required=True)
    distribution = fields.Char(string="Distribution", help="OS distribution: XP, 7, iOS 14, Ubuntu, Kali..")
    edition = fields.Char(string="Edition", help="OS edition: Home, Professional, Ultimate, Enterprise..")
    arch = fields.Selection([('32-bit', '32 bit'), ('64-bit', '64 bit')], string="Architecture")
    pc_id = fields.Many2one('pc_device.model', string='PC ID')

    @api.depends('system', 'distribution', 'edition', 'arch')
    def _get_name(self):
        for rec in self:
            parts = [rec.system, rec.distribution, rec.edition, rec.arch]
            rec.name = " ".join([str(x) for x in parts if x])

class PCCpuModel(models.Model):
    _name = "pc_cpu.model"
    _description = "Model of CPU for PC"
    _order = 'model asc'

    name = fields.Char(compute="_get_name", string="Name", readonly=True)
    model = fields.Char(string='CPU model', required=True)
    frequency = fields.Float(string='Frequency (GHz)', help='Enter value in floating-point')
    pc_id = fields.Many2one('pc_device.model', string='PC ID')

    @api.depends('model', 'frequency')
    def _get_name(self):
        for rec in self:
            parts = [rec.model, rec.frequency]
            name = " ".join([str(x) for x in parts if x])
            if rec.frequency:
                name += " GHz"
            rec.name = name

class PCModelModel(models.Model):
    _name = "pc_model.model"
    _description = "Model of PC devices."
    _order = "name asc"

    name = fields.Char(string="Model name", required=True)
    brand = fields.Many2one('it_device.brand', string='Brand name', required=True)
    pc_id = fields.Many2one('pc_device.model', string='PC ID')

class LicenseModel(models.Model):
    _name = 'license.model'
    _description = 'Model of license information'
    _order = 'software asc'

    name = fields.Char(compute='_get_name', string="Name", readonly=True)
    software = fields.Many2one('license.software', string='Software name')
    version = fields.Char(string='Version')
    serial = fields.Char(string='Serial number')
    pc_id = fields.Many2one('pc_device.model', string='PC ID')

    @api.depends('software', 'version')
    def _get_name(self):
        for rec in self:
            parts = [rec.software.name if rec.software else '', rec.version]
            rec.name = " ".join([str(x) for x in parts if x])

class LicenseSoftware(models.Model):
    _name = 'license.software'

    name = fields.Char(string='Software name')
    license_id = fields.Many2one('license.model', string='License ID')

class MobileDeviceModel(models.Model):
    _name = 'mobile_device.model'
    _description = 'Model of a Mobile Device'
    _order = 'brand_id asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(compute="_compute_mobile_name", store=True)
    model_name = fields.Many2one('mobile_model.model', string='Model name', domain="[('brand', '=', brand_id)]", required=True)
    brand_id = fields.Many2one('it_device.brand', required=True)
    category_ids = fields.Many2many('category', string='Tags')
    mobile_screen_diagonal = fields.Float(string='Screen diagonal (")')
    mobile_internal_memory = fields.Integer(string='Internal memory', help="This is the storage used to hold all your photos, videos, apps, and documents. The higher the value, the more files you can have in your device's memory.")
    mobile_processor = fields.Many2one('mobile_processor.model', string="Processor")
    mobile_os = fields.Many2one('mobile_os.model', string='Operation system')
    mobile_dual_sim = fields.Boolean(string='Dual SIM')
    mobile_battery = fields.Integer(string='Battery capacity (mAh)')
    mobile_imei = fields.Char(string='IMEI', required=True)
    mobile_memory = fields.Integer(string='RAM memory (GB)')
    mobile_network = fields.Many2one('mobile_network.model', string='Network')
    mobile_num = fields.Char(string='Phone number')
    mobile_pin = fields.Char(string='PIN')
    mobile_puk = fields.Char(string='PUK')
    mobile_cloud_login = fields.Char(string='Login')
    mobile_cloud_pass = fields.Char(string='Password')
    mobile_code = fields.Char(string='Restriction code')
    mobile_cur_user = fields.Many2one('hr.employee', string='Current user')
    mobile_prv_user = fields.Many2one('hr.employee', string='Previous user')
    mobile_transfer_date = fields.Date(string="Date of transfer", default=fields.Date.today)
    mobile_return_date = fields.Date(string="Date of return")
    mobile_other = fields.Text(string="Other")
    mobile_provider = fields.Many2one('res.partner', string='Provider')
    mobile_provider_code = fields.Char(string="Provider code")
    mobile_producer_code = fields.Char(string="Producer code")
    image = fields.Binary(related='brand_id.image', string="Logo", readonly=False)
    image_medium = fields.Binary(related='brand_id.image_medium', string="Logo (medium)", readonly=False)
    image_small = fields.Binary(related='brand_id.image_small', string="Logo (small)", readonly=False)

    @api.depends('brand_id.name', 'model_name.name')
    def _compute_mobile_name(self):
        for rec in self:
            rec.name = f"{rec.brand_id.name or ''} / {rec.model_name.name or ''}"

    def name_get(self):
        res = []
        for record in self:
            name = record.model_name.name or ''
            if record.brand_id.name:
                name = f"{record.brand_id.name} / {name}"
            res.append((record.id, name))
        return res

    @api.onchange('brand_id')
    def _onchange_brand(self):
        if self.brand_id:
            self.image_medium = self.brand_id.image
        else:
            self.image_medium = False

class MobileProcessorModel(models.Model):
    _name = "mobile_processor.model"
    _description = "Model of mobile processor"
    _order = "name asc"

    name = fields.Char(string="Processor model name", required=True)
    mobile_id = fields.Many2one('mobile_device.model', string='Mobile ID')

class MobileOSModel(models.Model):
    _name = "mobile_os.model"
    _description = "Mobile OS"
    _order = "name asc"

    name = fields.Char(string="OS name", required=True)
    mobile_id = fields.Many2one('mobile_device.model', string='Mobile ID')

class MobileModelModel(models.Model):
    _name = "mobile_model.model"
    _description = "Model of mobile devices."
    _order = "name asc"

    name = fields.Char(string="Model name", required=True)
    brand = fields.Many2one('it_device.brand', string='Brand name', required=True)
    mobile_id = fields.Many2one('mobile_device.model', string='Mobile ID')

class MobileNetworkModel(models.Model):
    _name = 'mobile_network.model'
    _description = 'Mobile Network Model'
    _order = "name asc"

    name = fields.Char(string='Network name')
    mobile_id = fields.Many2one('mobile_device.model', string='Mobile ID')

class HREmployeeInheritModel(models.Model):
    _inherit = 'hr.employee'

    pc_id = fields.Many2one('pc_device.model', compute="_get_devices_id", readonly=True, store=False)
    mobile_id = fields.Many2one('mobile_device.model', compute="_get_devices_id", readonly=True, store=False)
    other = fields.Text(string="Other")

    def _get_devices_id(self):
        for rec in self:
            employee = rec.name
            pc = self.env['pc_device.model'].search([('pc_curr_user', '=', employee)], limit=1)
            mobile = self.env['mobile_device.model'].search([('mobile_cur_user', '=', employee)], limit=1)
            rec.pc_id = pc.id if pc else False
            rec.mobile_id = mobile.id if mobile else False
            if mobile:
                rec.mobile_phone = mobile.mobile_num

class ITDevices(models.Model):
    _name = 'it_devices.model'
    _description = 'IT Devices'
    _order = 'brand_id asc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(compute="_compute_mobile_name", store=True)
    model_name = fields.Many2one('it_device_model.model', string='Model name', domain="[('brand', '=', brand_id)]", required=True)
    brand_id = fields.Many2one('it_device.brand', string='Brand', required=True)
    category_ids = fields.Many2many('category', string='Tags')
    curr_user = fields.Many2one('hr.employee', string='Current user')
    device = fields.Many2one('it_device_type.model', string='Device type')
    date_transfer = fields.Date(string='Date of transfer', default=fields.Date.today)
    date_return = fields.Date(string='Date of return')
    serial = fields.Char(string='Serial No.')
    it_other = fields.Text(string='Other')
    provider = fields.Many2one('res.partner', string='Provider')
    provider_code = fields.Char(string='Provider code')
    producer_code = fields.Char(string='Producer code')
    image = fields.Binary(related='brand_id.image', string="Logo", readonly=False)
    image_medium = fields.Binary(related='brand_id.image_medium', string="Logo (medium)", readonly=False)
    image_small = fields.Binary(related='brand_id.image_small', string="Logo (small)", readonly=False)
    prev_image = fields.Binary(string='Preview image', readonly=False)

    @api.depends('brand_id.name', 'device.name')
    def _compute_mobile_name(self):
        for rec in self:
            rec.name = f"{rec.device.name or ''} / {rec.brand_id.name or ''}"

    @api.onchange('brand_id')
    def _onchange_brand(self):
        if self.brand_id:
            self.image_medium = self.brand_id.image
        else:
            self.image_medium = False

class ITDeviceModel(models.Model):
    _name = 'it_device_model.model'
    _description = 'Model of device'

    name = fields.Char(string="Model name", required=True)
    brand = fields.Many2one('it_device.brand', string='Brand name', required=True)
    device_id = fields.Many2one('it_devices.model', string='Device ID')

class ITDeviceType(models.Model):
    _name = 'it_device_type.model'
    _description = 'Type of device'

    name = fields.Char(string="Type name", required=True)
    device_id = fields.Many2one('it_devices.model', string='Device ID')