# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class QCChecklist(models.Model):

    _name = 'qc.checklist'
    _description = 'QC checklist'

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        qc_bom_obj = self.env['qc.checklist.bom']
        if res.get('work_order_id'):
            work_order_obj = self.env['mrp.workorder'].browse(
                res.get('work_order_id'))
            if work_order_obj.exists():
                qc_template = []
                bom_rec = work_order_obj.production_bom_id
                qc_lines = qc_bom_obj.search([('bom_id', '=', bom_rec.id)])
                for rec in qc_lines:
                    for checklist in rec.checklist_line_ids:
                        qc_line = {
                            'name': checklist.name,
                            'field_type': checklist.selection_type
                        }
                        qc_template.append((0, 0, qc_line))
                print("qc_template..........", qc_template)
                res.update({'checklist_line_ids': qc_template})
        return res

    name = fields.Char(related="work_order_id.name")
    work_order_id = fields.Many2one('mrp.workorder', 'Work Order')
    checklist_line_ids = fields.One2many(
        'qc.checklist.line', 'qc_checklist_id')


class QCChecklistLine(models.Model):
    _name = 'qc.checklist.line'
    _description = 'QC checklist line'

    name = fields.Char()
    is_yes = fields.Boolean()
    is_no = fields.Boolean()
    remarks = fields.Text()
    field_type = fields.Selection(
        [('remarks', 'Remarks'), ('checkbox', 'CheckBox')])
    qc_checklist_id = fields.Many2one('qc.checklist')


class MRPWorkOrder(models.Model):

    _inherit = 'mrp.workorder'

    def qc_checklist(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('QC Checklist'),
            'res_model': 'qc.checklist',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_work_order_id': self.id
            }
        }


class QCChecklistBOM(models.Model):

    _name = 'qc.checklist.bom'
    _description = 'QC checklist Bom'

    bom_line_id = fields.Many2one('mrp.bom.line', 'BOM line')
    bom_id = fields.Many2one('mrp.bom', 'BOM')
    checklist_line_ids = fields.One2many(
        'qc.checklist.bom.line', 'mrp_bom_line_id')

    def create(self, vals):
        res = super().create(vals)
        res.bom_line_id.qc_template_id = res.id
        return res


class QCChecklistLine(models.Model):
    _name = 'qc.checklist.bom.line'
    _description = 'QC checklist bom line'

    name = fields.Char()
    selection_type = fields.Selection(
        [('remarks', 'Remarks'), ('checkbox', 'CheckBox')])
    mrp_bom_line_id = fields.Many2one('qc.checklist.bom')


class MRPBomLine(models.Model):

    _inherit = 'mrp.bom.line'

    qc_template_id = fields.Many2one('qc.checklist.bom')
    # child_product_bom_id = fields.Many2one(
    #     'mrp.bom', domain="[('is_child_bom','=', True)]", string="BOM")

    # checklist_line_ids = fields.One2many(
    #     'qc.checklist.bom.line', 'mrp_bom_line_id')

    def create_qc_cases(self):
        res_id = False
        if self.qc_template_id:
            res_id = self.qc_template_id.id
        else:
            res = self.qc_template_id.create({
                'bom_line_id': self.id
            })
            res_id = res.id
        return {
            'type': 'ir.actions.act_window',
            'name': _('QC Checklist'),
            'res_model': 'qc.checklist.bom',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'view_id': self.env.ref('qc_checklist.qc_checklist_template_form').id,
            'context': {
                'default_bom_line_id': self.id,
                'default_bom_id': self.bom_id.id
            },
            'res_id': res_id
        }

    # {'invisible': ['|', '|', ('state', 'in', ('draft', 'cancel', 'done', 'to_close')), ('qty_producing', '=', 0), ('move_raw_ids', '=', []), ('is_service_eng', '=', False), ('is_assembly_superivisor', '=', False)]}


class ProductTemplateOperationVendor(models.Model):

    _name = 'product.tmpl.operation.vendor'

    partner_id = fields.Many2one('res.partner')
    product_tmpl_id = fields.Many2one('product.template')
    vendor_id = fields.Many2one('res.partner')


# class ResPartner(models.Model):

#     _inherit = 'res.partner'

#     product_id = fields.Many2one('product.template')


class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    # is_child_bom = fields.Boolean("Is Part?")
    product_type = fields.Selection([('assembly', 'ASSEMBLY'),
                                     ('sub_assembly', 'SUB ASSEMBLY'),
                                     ('part', 'Part')],
                                    default='part',
                                    string="Product Type")
    vendor_list_ids = fields.One2many(
        related="product_tmpl_id.vendor_list_ids")
    process_ids = fields.One2many('mrp.bom.process.line', 'bom_id')

    @api.constrains('operation_ids', 'byproduct_ids', 'type')
    def _check_subcontracting_no_operation(self):
        return False


class MrpRoutingWorkcenter(models.Model):

    _inherit = 'mrp.routing.workcenter'

    # allowed_vendors_ids = fields.Many2many(
    #     'res.partner', compute="_compute_allowed_value_ids")
    vendor_id = fields.Many2one(
        'res.partner')
    manufacturing_type = fields.Selection(
        [('in_house', 'In House'), ('subcontract', 'Subcontract')])
    process_id = fields.Many2one('mrp.process')

    # @api.depends('bom_id.product_tmpl_id')
    # def _compute_allowed_value_ids(self):
    #     for rec in self:
    #         rec.allowed_vendors_ids = self.env['res.partner'].search(
    #             [('id', '=', self.bom_id.product_tmpl_id.vendor_list_ids.mapped('partner_id.id') or [])])


class ManufacturingProcess(models.Model):

    _name = 'mrp.process'

    name = fields.Char('Name')
    code = fields.Char('Code')
    mrp_workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center')
    vendor_ids = fields.Many2many('res.partner')
    process_code = fields.Char('Code')


class MrpBomProcessLine(models.Model):

    _name = 'mrp.bom.process.line'

    process_id = fields.Many2one('mrp.process', "Process")
    bom_id = fields.Many2one('mrp.bom')
    vendor_ids = fields.Many2many(related="process_id.vendor_ids")
    vendor_id = fields.Many2one(
        'res.partner', domain="[('id', 'in', vendor_ids)]")
    routing_workcenter_id = fields.Many2one(
        'mrp.routing.workcenter', ondelete="cascade")

    @api.model
    def create(self, vals):
        print("create process lines.............")
        mrp_routing_workcenter_obj = self.env['mrp.routing.workcenter']
        res = super(MrpBomProcessLine, self).create(vals)
        default_vals = mrp_routing_workcenter_obj.default_get(
            self.env['mrp.routing.workcenter']._fields)
        print("default_vals", default_vals)
        default_vals.update({
            'name': res.process_id.name,
            'workcenter_id': res.process_id.mrp_workcenter_id.id,
            'bom_id': res.bom_id.id,
            'process_id': res.process_id.id
        })
        res.routing_workcenter_id = mrp_routing_workcenter_obj.create(
            default_vals)
        return res
