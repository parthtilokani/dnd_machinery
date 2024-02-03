
from odoo import api, fields, models, Command


class MrpWorkOrder(models.Model):

    _inherit = 'mrp.workorder'

    # process_id = fields.Many2one('mrp.process')

    # _get_move_finished_values

    def button_finish(self):
        moves = []
        for workorder in self:
            process_code = workorder.operation_id.process_id.process_code

            if workorder.state in ('done', 'cancel'):
                continue
            else:
                # production.product_id.id, production.product_qty, production.product_uom_id.id

                if workorder.production_id.move_workorder_component_ids:
                    for bom_line in workorder.production_id.move_workorder_component_ids:
                        product_rec = self.env['product.product'].search(
                            [('default_code', '=',
                              f'{bom_line.product_id.default_code}-{process_code}')], limit=1)

                        if product_rec.exists():
                            move_dict = workorder.production_id._get_move_finished_values(
                                product_rec.id, bom_line.product_qty, bom_line.product_uom.id)
                            move_dict.update({
                                'state': 'draft'
                            })
                            moves.append(move_dict)
                        else:
                            product_rec = bom_line.product_id.copy({
                                'name': bom_line.product_id.name,
                                'default_code': f'{bom_line.product_id.default_code}-{process_code}'
                            })
                            move_dict = workorder.production_id._get_move_finished_values(
                                product_rec.id, bom_line.product_qty, bom_line.product_uom.id)
                            move_dict.update({
                                'state': 'draft'
                            })
                            moves.append(move_dict)
                    # workorder.production_id.move_workorder_component_ids = [
                    #     Command.clear()]
                    workorder.production_id.move_workorder_component_ids._action_confirm()
                    workorder.production_id.move_workorder_component_ids = [
                        (0, 0, line) for line in moves]
                    print("moves............", moves)
                else:

                    for bom_line in workorder.production_bom_id.bom_line_ids:

                        product_rec = self.env['product.product'].search(
                            [('default_code', '=',
                              f'{bom_line.product_id.default_code}-{process_code}')], limit=1)

                        if product_rec.exists():
                            move_dict = workorder.production_id._get_move_finished_values(
                                product_rec.id, bom_line.product_qty, bom_line.product_uom_id.id)
                            move_dict.update({'state': 'draft'})
                            moves.append(move_dict)
                        else:
                            product_rec = bom_line.product_id.copy({
                                'name': bom_line.product_id.name,
                                'default_code': f'{bom_line.product_id.default_code}-{process_code}'
                            })
                            move_dict = workorder.production_id._get_move_finished_values(
                                product_rec.id, bom_line.product_qty, bom_line.product_uom_id.id)
                            move_dict.update({'state': 'draft'})
                            moves.append(move_dict)

                    print("moves...........", moves)
                    # workorder.production_id.move_workorder_component_ids._action_confirm()
                    workorder.production_id.move_workorder_component_ids = [
                        (0, 0, line) for line in moves]
        res = super(MrpWorkOrder, self).button_finish()

        return res


# {
#             'product_id': product_id,
#             'product_uom_qty': product_uom_qty,
#             'product_uom': product_uom,
#             'operation_id': operation_id,
#             'byproduct_id': byproduct_id,
#             'name': _('New'),
#             'date': self._get_date_planned_finished(),
#             'date_deadline': self.date_deadline,
#             'picking_type_id': self.picking_type_id.id,
#             'location_id': self.product_id.with_company(self.company_id).property_stock_production.id,
#             'location_dest_id': self.location_dest_id.id,
#             'company_id': self.company_id.id,
#             'production_id': self.id,
#             'warehouse_id': self.location_dest_id.warehouse_id.id,
#             'origin': self.product_id.partner_ref,
#             'group_id': self.procurement_group_id.id,
#             'propagate_cancel': self.propagate_cancel,
#             'move_dest_ids': [(4, x.id) for x in self.move_dest_ids if not byproduct_id],
#             'cost_share': cost_share,
#         }
#         {
#             'sequence': bom_line.sequence if bom_line else 10,
#             'name': _('New'),
#             'date': self.date_planned_start,
#             'date_deadline': self.date_planned_start,
#             'bom_line_id': bom_line.id if bom_line else False,
#             'picking_type_id': self.picking_type_id.id,
#             'product_id': product_id.id,
#             'product_uom_qty': product_uom_qty,
#             'product_uom': product_uom.id,
#             'location_id': source_location.id,
#             'location_dest_id': self.product_id.with_company(self.company_id).property_stock_production.id,
#             'raw_material_production_id': self.id,
#             'company_id': self.company_id.id,
#             'operation_id': operation_id,
#             'price_unit': product_id.standard_price,
#             'procure_method': 'make_to_stock',
#             'origin': self._get_origin(),
#             'state': 'draft',
#             'warehouse_id': source_location.warehouse_id.id,
#             'group_id': self.procurement_group_id.id,
#             'propagate_cancel': self.propagate_cancel,
#             'manual_consumption': self.env['stock.move']._determine_is_manual_consumption(product_id, self, bom_line),
#         }
