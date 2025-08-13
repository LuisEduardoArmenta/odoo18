from odoo import models, fields, api

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Real Estate Property Type'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=10)
    
    # Relación inversa
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    
    # Campos calculados (comentados temporalmente)
    # offer_count = fields.Integer(compute='_compute_offer_count')
    # offer_ids = fields.Many2many('estate.property.offer', compute='_compute_offer_ids')
    
    # @api.depends('property_ids.offer_ids')  # Comentado temporalmente
    # def _compute_offer_count(self):
    #     for record in self:
    #         record.offer_count = len(record.offer_ids)
    
    # @api.depends('property_ids.offer_ids')  # Comentado temporalmente
    # def _compute_offer_ids(self):
    #     for record in self:
    #         record.offer_ids = record.property_ids.mapped('offer_ids') 