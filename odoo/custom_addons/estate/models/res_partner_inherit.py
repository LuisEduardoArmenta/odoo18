from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campos específicos para bienes raíces
    is_real_estate_agent = fields.Boolean(
        string='Es Agente Inmobiliario',
        help='Marcar si este contacto es un agente inmobiliario'
    )
    
    agent_license = fields.Char(
        string='Licencia de Agente',
        help='Número de licencia del agente inmobiliario'
    )
    
    specialization = fields.Selection([
        ('residential', 'Residencial'),
        ('commercial', 'Comercial'),
        ('industrial', 'Industrial'),
        ('luxury', 'Lujo'),
        ('rental', 'Alquiler')
    ], string='Especialización')
    
    commission_rate = fields.Float(
        string='Tasa de Comisión (%)',
        default=3.0,
        help='Porcentaje de comisión por venta'
    )
    
    # Campos relacionados con propiedades
    property_ids = fields.One2many(
        'estate.property', 
        'salesperson_id', 
        string='Propiedades como Vendedor'
    )
    
    bought_property_ids = fields.One2many(
        'estate.property', 
        'buyer_id', 
        string='Propiedades Compradas'
    )
    
    offer_ids = fields.One2many(
        'estate.offer', 
        'partner_id', 
        string='Ofertas Realizadas'
    )

    commission_ids = fields.One2many('estate.commission', 'agent_id', string='Commissions')
    
    # Campos computados
    total_properties_sold = fields.Integer(
        string='Propiedades Vendidas',
        compute='_compute_sales_stats',
        store=True
    )
    
    total_sales_amount = fields.Float(
        string='Monto Total de Ventas',
        compute='_compute_sales_stats',
        store=True
    )
    
    average_property_price = fields.Float(
        string='Precio Promedio',
        compute='_compute_sales_stats',
        store=True
    )
    
    success_rate = fields.Float(
        string='Tasa de Éxito (%)',
        compute='_compute_success_rate',
        store=True
    )
    
    @api.depends('property_ids', 'property_ids.state', 'property_ids.selling_price')
    def _compute_sales_stats(self):
        """Calcula estadísticas de ventas del agente"""
        for partner in self:
            sold_properties = partner.property_ids.filtered(lambda p: p.state == 'sold')
            partner.total_properties_sold = len(sold_properties)
            partner.total_sales_amount = sum(sold_properties.mapped('selling_price'))
            partner.average_property_price = (
                partner.total_sales_amount / partner.total_properties_sold 
                if partner.total_properties_sold > 0 else 0
            )
    
    @api.depends('property_ids', 'property_ids.state')
    def _compute_success_rate(self):
        """Calcula la tasa de éxito del agente"""
        for partner in self:
            total_properties = len(partner.property_ids)
            sold_properties = len(partner.property_ids.filtered(lambda p: p.state == 'sold'))
            partner.success_rate = (
                (sold_properties / total_properties) * 100 
                if total_properties > 0 else 0
            )
    
    @api.constrains('commission_rate')
    def _check_commission_rate(self):
        """Validar que la tasa de comisión sea razonable"""
        for partner in self:
            if partner.commission_rate < 0 or partner.commission_rate > 15:
                raise ValidationError("La tasa de comisión debe estar entre 0% y 15%")