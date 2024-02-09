

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    production_id = fields.Many2one('mrp.production')
