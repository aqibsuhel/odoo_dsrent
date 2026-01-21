# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Region(models.Model):
    _name = 'limousine.region'
    _description = 'Region'
    _order = 'name'

    name = fields.Char(string='Region Name', required=True, translate=True)
    code = fields.Char(string='Region Code')
    city_ids = fields.One2many('limousine.city', 'region_id', string='Cities')
    city_count = fields.Integer(string='Number of Cities', compute='_compute_city_count')

    @api.depends('city_ids')
    def _compute_city_count(self):
        for region in self:
            region.city_count = len(region.city_ids)