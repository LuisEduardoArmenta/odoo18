from odoo import models, fields, api
from datetime import date


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    # Nuevos campos para sprinkles
    image = fields.Binary(
        string='Property Image',
        help='Main image of the property'
    )
    
    latitude = fields.Float(
        string='Latitude',
        digits=(8, 6),
        help='Latitude coordinate for map location'
    )
    
    longitude = fields.Float(
        string='Longitude', 
        digits=(8, 6),
        help='Longitude coordinate for map location'
    )
    
    # Campos computados para análisis
    price_per_sqm = fields.Float(
        string='Price per m²',
        compute='_compute_price_per_sqm',
        store=True,
        help='Price per square meter'
    )
    
    days_on_market = fields.Integer(
        string='Days on Market',
        compute='_compute_days_on_market',
        store=True
    )
    
    offer_count = fields.Integer(
        string='Number of Offers',
        compute='_compute_offer_stats',
        store=True
    )
    
    avg_offer_price = fields.Float(
        string='Average Offer Price',
        compute='_compute_offer_stats',
        store=True
    )
    
    price_vs_expected = fields.Float(
        string='Price vs Expected (%)',
        compute='_compute_price_performance',
        store=True
    )
    
    market_attractiveness = fields.Float(
        string='Market Attractiveness',
        compute='_compute_market_attractiveness',
        store=True,
        help='Score from 0 to 100 based on number of offers and time on market'
    )
    
    @api.depends('expected_price', 'total_area')
    def _compute_price_per_sqm(self):
        """Calcula el precio por metro cuadrado"""
        for property_rec in self:
            if property_rec.total_area > 0:
                property_rec.price_per_sqm = property_rec.expected_price / property_rec.total_area
            else:
                property_rec.price_per_sqm = 0
    
    @api.depends('create_date', 'state')
    def _compute_days_on_market(self):
        """Calcula los días en el mercado"""
        for property_rec in self:
            if property_rec.create_date:
                if property_rec.state == 'sold':
                    # Si está vendida, usar la fecha de la última oferta aceptada
                    accepted_offer = property_rec.offer_ids.filtered(lambda o: o.status == 'accepted')
                    if accepted_offer:
                        end_date = fields.Date.to_date(accepted_offer[0].write_date)
                    else:
                        end_date = date.today()
                else:
                    end_date = date.today()
                
                start_date = fields.Date.to_date(property_rec.create_date)
                property_rec.days_on_market = (end_date - start_date).days
            else:
                property_rec.days_on_market = 0
    
    @api.depends('offer_ids', 'offer_ids.price')
    def _compute_offer_stats(self):
        """Calcula estadísticas de ofertas"""
        for property_rec in self:
            offers = property_rec.offer_ids
            property_rec.offer_count = len(offers)
            property_rec.avg_offer_price = (
                sum(offers.mapped('price')) / len(offers) 
                if offers else 0
            )
    
    @api.depends('best_price', 'expected_price')
    def _compute_price_performance(self):
        """Calcula el rendimiento del precio"""
        for property_rec in self:
            if property_rec.expected_price > 0 and property_rec.best_price:
                property_rec.price_vs_expected = (
                    property_rec.best_price / property_rec.expected_price * 100
                )
            else:
                property_rec.price_vs_expected = 0
    
    @api.depends('offer_count', 'days_on_market')
    def _compute_market_attractiveness(self):
        """Calcula el atractivo del mercado"""
        for property_rec in self:
            # Algoritmo simple: más ofertas = más atractivo, menos días = más atractivo
            base_score = 50
            
            # Bonus por ofertas (max 30 puntos)
            offer_bonus = min(property_rec.offer_count * 10, 30)
            
            # Penalty por días en mercado (max -30 puntos)
            if property_rec.days_on_market > 0:
                day_penalty = min(property_rec.days_on_market / 10, 30)
            else:
                day_penalty = 0
            
            score = base_score + offer_bonus - day_penalty
            property_rec.market_attractiveness = max(0, min(100, score))


class EstateBaseModel(models.AbstractModel):
    """Modelo base abstracto para funcionalidades comunes"""
    _name = 'estate.base.model'
    _description = 'Estate Base Model with Common Features'

    # Campos de auditoría mejorados
    create_uid = fields.Many2one(
        'res.users', 
        string='Created by', 
        readonly=True
    )
    
    create_date = fields.Datetime(
        string='Created on', 
        readonly=True
    )
    
    write_uid = fields.Many2one(
        'res.users', 
        string='Last Updated by', 
        readonly=True
    )
    
    write_date = fields.Datetime(
        string='Last Updated on', 
        readonly=True
    )
    
    # Campo de notas interno
    internal_notes = fields.Text(
        string='Internal Notes',
        help='Internal notes for staff only'
    )
    
    # Campo de prioridad
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Very High')
    ], string='Priority', default='1')
    
    # Campo de etiquetas
    color = fields.Integer(string='Color', default=0)
    
    def get_base_url(self):
        """Obtiene la URL base del sistema"""
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    
    def send_notification(self, message, title="Notification"):
        """Envía una notificación al usuario"""
        self.env.user.notify_info(
            message=message,
            title=title,
            sticky=False
        )
