from odoo import models, fields

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Real Estate Property Tag'
    _order = 'name'

    name = fields.Char(required=True)
    color = fields.Integer()
    
    # Restricción SQL para nombres únicos
    _sql_constraints = [
        ('check_name_unique', 'UNIQUE(name)', 'Tag name must be unique!')
    ] 