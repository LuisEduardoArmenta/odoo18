from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Type'
    _order = 'sequence, name'

    name = fields.Char(required=True, string='Property Type Name')
    sequence = fields.Integer('Sequence', default=10, help='Order of this type in lists')
    
    # Relación inversa hacia estate.property
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    
    # Campo computado para mostrar el número de propiedades
    property_count = fields.Integer(compute='_compute_property_count', string='Property Count', store=True)
    
    @api.depends('property_ids')
    def _compute_property_count(self):
        for record in self:
            record.property_count = len(record.property_ids)
    
    # Validaciones
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError("Property type name is required!")
            if len(record.name.strip()) < 2:
                raise ValidationError("Property type name must be at least 2 characters long!")
    
    @api.constrains('sequence')
    def _check_sequence(self):
        for record in self:
            if record.sequence < 0:
                raise ValidationError("Sequence must be positive!")
    
    # SQL Constraints
    _sql_constraints = [
        ('check_name_unique', 'UNIQUE(name)', 'Property type name must be unique!'),
        ('check_sequence_positive', 'CHECK(sequence >= 0)', 'Sequence must be positive!'),
    ] 