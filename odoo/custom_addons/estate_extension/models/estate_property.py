from odoo import models, fields, api

class EstateProperty(models.Model):
    _inherit = 'estate.property'
    
    # Nuevos campos agregados por herencia
    parking_spaces = fields.Integer(string='Parking Spaces', default=0)
    year_built = fields.Integer(string='Year Built')
    energy_rating = fields.Selection([
        ('A', 'A - Excellent'),
        ('B', 'B - Good'),
        ('C', 'C - Average'),
        ('D', 'D - Poor'),
        ('E', 'E - Very Poor'),
    ], string='Energy Rating')
    
    # Campo calculado
    property_age = fields.Integer(compute='_compute_property_age', store=True)
    
    @api.depends('year_built')
    def _compute_property_age(self):
        current_year = fields.Date.today().year
        for record in self:
            if record.year_built:
                record.property_age = current_year - record.year_built
            else:
                record.property_age = 0
    
    # Método que extiende funcionalidad existente
    def action_sold(self):
        result = super(EstateProperty, self).action_sold()
        for prop in self:
            # Logica de la comision
            if prop.salesperson_id and prop.selling_price > 0:
                agent = prop.salesperson_id.partner_id
                if agent and agent.is_real_estate_agent:
                    commission_amount = prop.selling_price * (agent.commission_rate / 100.0)
                    if commission_amount > 0:
                        self.env['estate.commission'].create({
                            'property_id': prop.id,
                            'agent_id': agent.id,
                            'amount': commission_amount,
                        })
        return result 