# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MRPWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    is_subcontract = fields.Boolean('Subcontract', default=False)

    def action_subcontract(self):
        purchase_obj = self.env['purchase.order']
        purchase_order_line_obj = self.env['purchase.order.line']
        bom_id = self.env['mrp.bom'].search(
            [('product_tmpl_id', '=', self.production_id.product_id.product_tmpl_id.id)])
        process_id = bom_id.process_ids.filtered(
            lambda x: x.process_id.mrp_workcenter_id == self.workcenter_id)
        purchase = purchase_obj.create({
            'partner_id': process_id.vendor_id and process_id.vendor_id.id or False,
            'date_order': fields.Datetime.now(),
            'currency_id': self.product_id.currency_id and self.product_id.currency_id.id or False,
            'manufecturing_id': self.production_id and self.production_id.id or False,
            'process_id': process_id.process_id and process_id.process_id.id or False
        })
        purchase_order_line_obj.create({
            'order_id': purchase.id,
            'product_id': self.product_id and self.product_id.id or False,
            'name': self.product_id.product_tmpl_id.name or '',
            'product_qty': bom_id.product_qty and bom_id.product_qty or 0.00,
        })
        # default service product purchase order line
        service_product_id = self.env['product.product'].search(
            [('name', '=', 'service'), ('detailed_type', '=', 'product')])
        purchase_order_line_obj.create({
            'order_id': purchase.id,
            'product_id': service_product_id and service_product_id.id or False,
            'name': 'subcontracting service product',
            'price_unit': service_product_id.lst_price and service_product_id.lst_price or 0.00,
        })
        picking_obj = self.env['stock.picking']
        self.button_start()
        res = picking_obj.create({
            'partner_id': process_id.vendor_id and process_id.vendor_id.id or False,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            # 'move_ids_without_package': [()]
        })
        print("res..............",
              self.production_id.move_workorder_component_ids.read(['location_id', 'location_dest_id', 'product_id']), res)
        if purchase:
            purchase.button_confirm()
            self.is_subcontract = True

    def action_jobcard(self):
        bom_id = self.production_bom_id
        process_id = bom_id.process_ids.filtered(
            lambda x: x.process_id.mrp_workcenter_id == self.workcenter_id)
        vals = {
            'partner_id': process_id.vendor_id and process_id.vendor_id.id or False,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'origin': self.production_id.name,
            'production_id': self.production_id.id
        }
        res = self.env['stock.picking'].create(vals)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'res_id': res.id,
            'view_mode': 'form',
            'view_type': 'form'
        }


class MRPProductionInherit(models.Model):
    _inherit = 'mrp.production'

    resupply_order_count = fields.Integer(
        string="Ticket Count", compute="compute_custom_resupply_order", copy=False)

    def compute_custom_resupply_order(self):
        for record in self:
            resupply_orders = self.env['stock.picking'].search(
                [('purchase_id.manufecturing_id', '=', record.id)])
            record.resupply_order_count = len(resupply_orders)

    def action_view_resupply_order(self):
        resupply_orders = self.env['stock.picking'].search(
            [('purchase_id.manufecturing_id', '=', self.id)])
        if resupply_orders:
            return {
                'name': _("Resupply Order"),
                'res_model': 'stock.picking',
                'target': 'current',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', resupply_orders.ids)]
            }


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    manufecturing_id = fields.Many2one(
        'mrp.production', string="Manufacturing No")
    process_id = fields.Many2one('mrp.process', "Process")
