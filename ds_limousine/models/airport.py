# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Airport(models.Model):
    _name = 'limousine.airport'
    _description = 'Airport'
    _order = 'name'

    name = fields.Char(string='Airport Name', required=True, translate=True)
    name_arabic = fields.Char(string='Airport Name (Arabic)')
    code = fields.Char(string='Airport Code (IATA)', size=3)
    city_id = fields.Many2one('limousine.city', string='City', required=True)
    region_id = fields.Many2one('limousine.region', string='Region',
                                related='city_id.region_id', store=True, readonly=True)
    active = fields.Boolean(string='Active', default=True)

    def name_get(self):
        result = []
        for record in self:
            if record.code:
                name = f"[{record.code}] {record.name}"
            else:
                name = record.name
            if record.name_arabic:
                name += f" - {record.name_arabic}"
            result.append((record.id, name))
        return result