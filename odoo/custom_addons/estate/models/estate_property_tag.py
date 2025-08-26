from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Real Estate Property Tag'
    _order = 'name'

    name = fields.Char(required=True, string='Tag Name')
    color = fields.Integer(string='Color', default=0)
    
    # Campo para descripción del tag
    description = fields.Text(string='Description')
    
    # Campo computado para mostrar el número de propiedades con este tag
    property_count = fields.Integer(compute='_compute_property_count', string='Property Count', store=True)
    
    @api.depends('name')
    def _compute_property_count(self):
        for record in self:
            # Contar propiedades que tienen este tag
            count = self.env['estate.property'].search_count([('tag_ids', 'in', record.id)])
            record.property_count = count
    
    # Validaciones
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError("Tag name is required!")
            if len(record.name.strip()) < 2:
                raise ValidationError("Tag name must be at least 2 characters long!")
            # Verificar que no contenga caracteres especiales problemáticos
            import re
            if not re.match(r'^[A-Za-z0-9\s\-_]+$', record.name.strip()):
                raise ValidationError("Tag name can only contain letters, numbers, spaces, hyphens and underscores!")
    
    @api.constrains('color')
    def _check_color(self):
        for record in self:
            if record.color < 0 or record.color > 11:
                raise ValidationError("Color must be between 0 and 11!")
    
    # Restricción SQL para nombres únicos
    _sql_constraints = [
        ('check_name_unique', 'UNIQUE(name)', 'Tag name must be unique!')
    ] 