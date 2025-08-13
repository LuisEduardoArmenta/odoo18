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
        # Llamar al método original
        result = super().action_sold()
        # Agregar funcionalidad adicional
        for record in self:
            if record.property_age > 50:
                record.description = f"{record.description or ''}\n\n⚠️ Property is over 50 years old!"
        return result 