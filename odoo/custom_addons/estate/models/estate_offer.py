from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta

class EstateOffer(models.Model):
    _name = 'estate.offer'
    _description = 'Estate Property Offer'
    _order = 'price desc'

    # Campos básicos
    price = fields.Float(string='Price', required=True)
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ], string='Status', copy=False)
    
    # Relaciones
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    
    # Campos de validez y fecha límite
    validity = fields.Integer(string='Validity (days)', default=7)
    date_deadline = fields.Date(
        string='Deadline', 
        compute='_compute_date_deadline', 
        inverse='_inverse_date_deadline',
        store=True
    )
    
    # Campo para mostrar información adicional
    property_type_id = fields.Many2one(
        related='property_id.property_type_id', 
        string='Property Type', 
        store=True
    )
    
    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        """Calcula la fecha límite basada en create_date + validity días"""
        for offer in self:
            if offer.create_date and offer.validity:
                base_date = fields.Date.to_date(offer.create_date)
                offer.date_deadline = base_date + timedelta(days=offer.validity)
            else:
                offer.date_deadline = False
    
    def _inverse_date_deadline(self):
        """Método inverso: ajusta validity cuando se edita date_deadline"""
        for offer in self:
            if offer.date_deadline and offer.create_date:
                base_date = fields.Date.to_date(offer.create_date)
                delta = offer.date_deadline - base_date
                offer.validity = delta.days
            else:
                offer.validity = 7
    
    # Métodos de acción
    def action_accept(self):
        """Acepta la oferta y rechaza las demás - Versión mejorada y robusta"""
        # Validación 1: Comprobar el estado de la propiedad
        if self.property_id.state in ['offer_accepted', 'sold', 'cancelled']:
            raise UserError(
                f"Cannot accept offer. The property is already {self.property_id.state}. "
                f"Only properties in 'new' or 'offer_received' state can have offers accepted."
            )
        
        # Validación 2: Comprobar que el precio no sea inferior al 90% del precio esperado
        min_acceptable_price = self.property_id.expected_price * 0.9
        if self.price < min_acceptable_price:
            raise UserError(
                f"Cannot accept offer. The offer price (${self.price:,.2f}) is below "
                f"the minimum acceptable price (${min_acceptable_price:,.2f}), which is 90% "
                f"of the expected price (${self.property_id.expected_price:,.2f})."
            )
        
        # Si pasan todas las validaciones, proceder con la aceptación
        self.status = 'accepted'
        self.property_id.state = 'offer_accepted'
        self.property_id.selling_price = self.price
        self.property_id.buyer_id = self.partner_id
        
        # Rechazar todas las otras ofertas de la misma propiedad
        other_offers = self.env['estate.offer'].search([
            ('property_id', '=', self.property_id.id),
            ('id', '!=', self.id),
            ('status', '!=', 'refused')
        ])
        other_offers.action_refuse()
        
        return True
    
    def action_refuse(self):
        """Rechaza la oferta"""
        self.status = 'refused'
        return True
    
    # Validaciones
    @api.constrains('price')
    def _check_price(self):
        for offer in self:
            if offer.price <= 0:
                raise ValidationError("Offer price must be positive!")
    
    @api.constrains('validity')
    def _check_validity(self):
        for offer in self:
            if offer.validity <= 0:
                raise ValidationError("Validity must be positive!")
    
    @api.model_create_multi
    def create(self, vals_list):
        """Al crear una oferta, cambiar el estado de la propiedad"""
        offers = super().create(vals_list)
        for offer in offers:
            if offer.property_id.state == 'new':
                offer.property_id.state = 'offer_received'
        return offers
    
    # SQL Constraints
    _sql_constraints = [
        ('check_price_positive', 'CHECK(price > 0)', 'Offer price must be positive!'),
        ('check_validity_positive', 'CHECK(validity > 0)', 'Validity must be positive!'),
    ]
