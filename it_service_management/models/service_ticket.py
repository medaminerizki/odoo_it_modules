from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError

class ServiceTicket(models.Model):
    _name = 'it.service.ticket'
    _description = 'IT Service Ticket'

    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')

    client_group_id = fields.Many2one(
        'res.groups',
        compute='_compute_client_group_id',
        store=False,
        default=lambda self: self.env.ref('it_service_management.group_it_client', raise_if_not_found=False).id
    )
    technician_group_id = fields.Many2one(
        'res.groups',
        compute='_compute_technician_group_id',
        store=False,
        default=lambda self: self.env.ref('it_service_management.group_it_technician', raise_if_not_found=False).id
    )

    client_id = fields.Many2one(
        'res.partner',
        string='Client',
        domain="[('user_ids.groups_id', '=', client_group_id)]"
    )
    assigned_to = fields.Many2one(
        'res.users',
        string='Technician',
        domain="[('groups_id', '=', technician_group_id)]"
    )

    device_ref = fields.Reference(
    selection=[
        ('it_devices.model', 'Device'),
        ('pc_device.model', 'PC'),
        ('mobile_device.model', 'Mobile'),
    ],
    string='Device',
    help="Select the device (PC, Mobile, or other) assigned to you that has a problem."
)
    
    date_created = fields.Datetime(string='Created On', default=fields.Datetime.now)
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('waiting_info', 'Waiting for Info'),
        ('solved', 'Solved'),
        ('closed', 'Closed'),
    ], string='Status', default='new')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', default='1')
    deadline = fields.Date(string='Deadline')
    can_close = fields.Boolean(
        compute='_compute_can_close',
        string='Can Close Ticket',
        store=False
    )
    can_start_progress = fields.Boolean(compute='_compute_button_visibility', store=False)
    can_waiting_info = fields.Boolean(compute='_compute_button_visibility', store=False)
    can_solve = fields.Boolean(compute='_compute_button_visibility', store=False)

    @api.model
    def create(self, vals):
        ticket = super().create(vals)
        if ticket.assigned_to and ticket.assigned_to.partner_id.email:
            template = self.env.ref('it_service_management.mail_template_ticket_assigned', raise_if_not_found=False)
            if template:
                template.send_mail(ticket.id, force_send=True)
        return ticket

    def write(self, vals):
        res = super().write(vals)
        for ticket in self:
            if 'assigned_to' in vals and ticket.assigned_to and ticket.assigned_to.partner_id.email:
                template = self.env.ref('it_service_management.mail_template_ticket_assigned', raise_if_not_found=False)
                if template:
                    template.send_mail(ticket.id, force_send=True)
        return res
    
    def action_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_waiting_info(self):
        self.write({'state': 'waiting_info'})

    def action_solved(self):
        self.write({'state': 'solved'})

    def action_closed(self):
        if not self.env.user.has_group('it_service_management.group_it_client'):
            raise UserError("Seul le client peut fermer le ticket.")
        self.write({'state': 'closed'})

    def send_deadline_reminder(self):
        tomorrow = fields.Date.today() + timedelta(days=1)
        tickets = self.search([('deadline', '=', tomorrow), ('state', '!=', 'done')])
        template = self.env.ref('it_service_management.mail_template_ticket_deadline', raise_if_not_found=False)
        for ticket in tickets:
            if template:
                template.send_mail(ticket.id, force_send=True)

    def print_ticket_pdf(self):
        return self.env.ref('it_service_management.action_report_service_ticket').report_action(self)

    def _compute_can_close(self):
        for ticket in self:
            ticket.can_close = (
                ticket.state == 'solved'
                and ticket.client_id.id == self.env.user.partner_id.id
                and self.env.user.has_group('it_service_management.group_it_client')
            )

    @api.depends()
    def _compute_client_group_id(self):
        group = self.env.ref('it_service_management.group_it_client', raise_if_not_found=False)
        for rec in self:
            rec.client_group_id = group.id if group else False

    @api.depends()
    def _compute_technician_group_id(self):
        group = self.env.ref('it_service_management.group_it_technician', raise_if_not_found=False)
        for rec in self:
            rec.technician_group_id = group.id if group else False

    def _compute_button_visibility(self):
        for ticket in self:
            ticket.can_start_progress = (
                ticket.state == 'new' and
                self.env.user.has_group('it_service_management.group_it_technician') or
                self.env.user.has_group('it_service_management.group_it_admin')
            )
            ticket.can_waiting_info = (
                ticket.state == 'in_progress' and
                self.env.user.has_group('it_service_management.group_it_technician') or
                self.env.user.has_group('it_service_management.group_it_admin')
            )
            ticket.can_solve = (
                ticket.state == 'waiting_info' and
                self.env.user.has_group('it_service_management.group_it_technician') or
                self.env.user.has_group('it_service_management.group_it_admin')
            )

    @api.onchange('client_id')
    def _onchange_client_id(self):
        domain = {}
        if self.client_id:
            user = self.env['res.users'].search([('partner_id', '=', self.client_id.id)], limit=1)
            if user and user.employee_id:
                emp_id = user.employee_id.id
                domain = {
                    'device_ref': [
                        '|', '|',
                        '&', ('_name', '=', 'it_devices.model'), ('curr_user', '=', emp_id),
                        '&', ('_name', '=', 'pc_device.model'), ('curr_user', '=', emp_id),
                        '&', ('_name', '=', 'mobile_device.model'), ('curr_user', '=', emp_id),
                    ]
                }
        return {'domain': domain}