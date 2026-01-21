# -*- coding: utf-8 -*-

from odoo import models, fields, api


class City(models.Model):
    _name = 'limousine.city'
    _description = 'City'
    _order = 'name'

    name = fields.Char(string='City Name', required=True, translate=True)
    name_arabic = fields.Char(string='City Name (Arabic)')
    region_id = fields.Many2one('limousine.region', string='Region', required=True)
    branch_ids = fields.One2many('limousine.branch', 'city_id', string='Branches')
    airport_ids = fields.One2many('limousine.airport', 'city_id', string='Airports')
    branch_count = fields.Integer(string='Number of Branches', compute='_compute_branch_count')

    @api.depends('branch_ids')
    def _compute_branch_count(self):
        for city in self:
            city.branch_count = len(city.branch_ids)

    def name_get(self):
        result = []
        for record in self:
            if record.name_arabic:
                name = f"{record.name} - {record.name_arabic}"
            else:
                name = record.name
            result.append((record.id, name))
        return result