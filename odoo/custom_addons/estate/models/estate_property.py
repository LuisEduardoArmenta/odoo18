from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta
import re

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Real Estate Property'
    _order = 'id desc'

    # campos básicos
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(default=fields.Date.context_today, copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        [('north', 'North'),
         ('south', 'South'),
         ('east', 'East'),
         ('west', 'West')],
        string='Garden Orientation')
    
    # campos adicionales del Capítulo 5
    state = fields.Selection(
        [('new', 'New'),
         ('offer_received', 'Offer Received'),
         ('offer_accepted', 'Offer Accepted'),
         ('sold', 'Sold'),
         ('cancelled', 'Cancelled')],
        default='new',
        required=True,
        copy=False)
    
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    salesperson_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    tag_ids = fields.Many2many('estate.property.tag', string='Tags')
    
    # CAPÍTULO 9: Relación con ofertas
    offer_ids = fields.One2many('estate.offer', 'property_id', string='Offers')
    
    # Campos para reportes
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(related='company_id.currency_id', string='Currency', readonly=True)
    
    # CAPÍTULO 8: Nuevos campos para campos computados y onchanges
    validity = fields.Integer(string='Validity (days)', default=7, help='Number of days the property listing is valid')
    
    # campos calculados
    total_area = fields.Integer(compute='_compute_total_area', store=True, string='Total Area')
    best_price = fields.Float(compute='_compute_best_price', string='Best Offer', help='Highest offer received')
    date_deadline = fields.Date(
        compute='_compute_date_deadline', 
        inverse='_inverse_date_deadline',
        store=True,
        string='Deadline Date',
        help='Automatically calculated as creation date + validity days'
    )
    
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        """Calcula el área total sumando living_area y garden_area"""
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)
    
    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        """Calcula el mejor precio entre todas las ofertas"""
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0
    
    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        """Calcula la fecha límite basada en create_date + validity días"""
        for record in self:
            if record.create_date and record.validity:
                # Convertir create_date (datetime) a date antes de sumar
                base_date = fields.Date.to_date(record.create_date)
                record.date_deadline = base_date + timedelta(days=record.validity)
            else:
                record.date_deadline = False
    
    def _inverse_date_deadline(self):
        """Método inverso: ajusta validity cuando se edita date_deadline"""
        for record in self:
            if record.date_deadline and record.create_date:
                # Convertir create_date (datetime) a date antes de restar
                base_date = fields.Date.to_date(record.create_date)
                delta = record.date_deadline - base_date
                record.validity = delta.days
            else:
                record.validity = 0
    
    @api.onchange('garden')
    def _onchange_garden(self):
        """Onchange para el campo garden: ajusta garden_area y garden_orientation"""
        if self.garden:
            # Si se activa garden, asigna valores por defecto
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            # Si se desactiva garden, resetea los campos
            self.garden_area = False
            self.garden_orientation = False
    
    def action_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError("Cannot sell a cancelled property!")
            record.state = 'sold'
        return True

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Cannot cancel a sold property!")
            record.state = 'cancelled'
        return True
    
    # Método para duplicar propiedades con validaciones
    def copy(self, default=None):
        default = dict(default or {})
        default.update({
            'name': self.name + ' (Copy)',
            'state': 'new',
            'selling_price': 0,
            'buyer_id': False,
        })
        return super().copy(default)
    
    # Método para obtener el área total como texto
    def get_total_area_display(self):
        self.ensure_one()
        if self.total_area:
            return f"{self.total_area} m²"
        return "Not specified"    # Validaciones con @api.constrains
    @api.constrains('expected_price', 'selling_price')
    def _check_prices(self):
        for record in self:
            if record.expected_price <= 0:
                raise ValidationError("Expected price must be positive!")
            if record.selling_price and record.selling_price <= 0:
                raise ValidationError("Selling price must be positive!")
            # Nota: La validación del 90% del precio ahora se maneja en estate_offer.action_accept()
            # para mayor control y mejores mensajes de error.
    
    @api.constrains('offer_ids')
    def _check_offer_price(self):
        """Validar que las ofertas no sean demasiado bajas"""
        for record in self:
            for offer in record.offer_ids:
                if offer.price < record.expected_price * 0.5:
                    raise ValidationError(
                        f"Offer price ({offer.price}) cannot be lower than 50% of expected price ({record.expected_price})!"
                    )
    
    @api.constrains('bedrooms', 'living_area', 'facades')
    def _check_positive_values(self):
        for record in self:
            if record.bedrooms < 0:
                raise ValidationError("Bedrooms cannot be negative!")
            if record.living_area < 0:
                raise ValidationError("Living area cannot be negative!")
            if record.facades < 0:
                raise ValidationError("Facades cannot be negative!")
    
    @api.constrains('garden_area')
    def _check_garden_area(self):
        for record in self:
            if record.garden and record.garden_area <= 0:
                raise ValidationError("Garden area must be positive when property has a garden!")
    
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError("Property name is required!")
            if len(record.name.strip()) < 3:
                raise ValidationError("Property name must be at least 3 characters long!")
    
    @api.constrains('postcode')
    def _check_postcode(self):
        for record in self:
            if record.postcode:
                # Validación básica de código postal (solo números y letras, 3-10 caracteres)
                if not re.match(r'^[A-Za-z0-9]{3,10}$', record.postcode):
                    raise ValidationError("Postcode must contain only letters and numbers, 3-10 characters!")
    
    # SQL Constraints
    _sql_constraints = [
        ('check_expected_price_positive', 'CHECK(expected_price > 0)', 'Expected price must be positive!'),
        ('check_selling_price_positive', 'CHECK(selling_price >= 0)', 'Selling price must be positive!'),
    ]

