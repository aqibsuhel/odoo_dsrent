# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Branch(models.Model):
    _name = 'limousine.branch'
    _description = 'Branch'
    _order = 'name'

    name = fields.Char(string='Branch Name', required=True, translate=True)
    name_arabic = fields.Char(string='Branch Name (Arabic)')
    city_id = fields.Many2one('limousine.city', string='City', required=True)
    region_id = fields.Many2one('limousine.region', string='Region',
                                related='city_id.region_id', store=True, readonly=True)
    address = fields.Text(string='Address')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    active = fields.Boolean(string='Active', default=True)

    def name_get(self):
        result = []
        for record in self:
            if record.name_arabic:
                name = f"{record.name} - {record.name_arabic}"
            else:
                name = record.name
            result.append((record.id, name))
        return result