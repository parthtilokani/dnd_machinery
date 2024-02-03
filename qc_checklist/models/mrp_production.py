
from odoo import api, fields, models, Command


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    is_service_eng = fields.Boolean()
    is_assembly_superivisor = fields.Boolean()
    service_eng_id = fields.Many2one('res.users')
    assembly_eng_id = fields.Many2one('res.users')

    move_workorder_component_ids = fields.One2many(
        'stock.move', 'workorder_component_production_id', 'Raw Materials',
        domain=[('scrapped', '=', False), ('state', '=', 'draft')])

    def superEng_btn(self):
        if not self.is_service_eng:
            self.is_service_eng = True

    def is_assembly_superivisor_btn(self):
        if not self.is_assembly_superivisor:
            self.is_assembly_superivisor = True

    def _get_move_workorder_component(self, product_id, product_uom_qty, product_uom, operation_id=False, process_id=False, cost_share=0):
        group_orders = self.procurement_group_id.mrp_production_ids
        move_dest_ids = self.move_dest_ids
        if len(group_orders) > 1:
            move_dest_ids |= group_orders[0].move_finished_ids.filtered(
                lambda m: m.product_id == self.product_id).move_dest_ids
        return {
            'product_id': product_id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom,
            'operation_id': operation_id,
            'process_id': process_id,
            'name': _('New'),
            'date': self._get_date_planned_finished(),
            'date_deadline': self.date_deadline,
            'picking_type_id': self.picking_type_id.id,
            'location_id': self.product_id.with_company(self.company_id).property_stock_production.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
            'production_id': self.id,
            'warehouse_id': self.location_dest_id.warehouse_id.id,
            'origin': self.product_id.partner_ref,
            'group_id': self.procurement_group_id.id,
            'propagate_cancel': self.propagate_cancel,
            'move_dest_ids': [(4, x.id) for x in self.move_dest_ids if not byproduct_id],
            'cost_share': cost_share,
        }


class StockMove(models.Model):

    _inherit = 'stock.move'

    workorder_component_production_id = fields.Many2one('mrp.production')
    process_id = fields.Many2one('mrp.process')
