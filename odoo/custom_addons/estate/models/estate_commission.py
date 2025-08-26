from odoo import models, fields, api

class EstateCommission(models.Model):
    _name = 'estate.commission'
    _description = 'Real Estate Commission'

    name = fields.Char(string='Description', compute='_compute_name', store=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    agent_id = fields.Many2one('res.partner', string='Agent', required=True, domain="[('is_real_estate_agent', '=', True)]")
    amount = fields.Float(string='Amount', required=True)
    date = fields.Date(string='Date', default=fields.Date.context_today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('paid', 'Paid'),
    ], string='Status', default='draft')

    @api.depends('property_id', 'agent_id')
    def _compute_name(self):
        for commission in self:
            if commission.property_id and commission.agent_id:
                commission.name = f"Commission for {commission.property_id.name} - {commission.agent_id.name}"
            else:
                commission.name = "Commission"
