from odoo import models, fields, api

class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Real Estate Property'

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
    
    # campos calculados
    total_area = fields.Integer(compute='_compute_total_area', store=True)
    # best_offer = fields.Float(compute='_compute_best_offer', store=True)  # Comentado temporalmente
    
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)
    
    # @api.depends('offer_ids.price')  # Comentado temporalmente
    # def _compute_best_offer(self):
    #     for record in self:
    #         if record.offer_ids:
    #             record.best_offer = max(record.offer_ids.mapped('price'))
    #         else:
    #             record.best_offer = 0.0
    
    def action_sold(self):
        for record in self:
            record.state = 'sold'
        return True
    
    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
        return True

