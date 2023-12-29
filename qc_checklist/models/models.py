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
    child_product_bom_id = fields.Many2one(
        'mrp.bom', domain="[('is_child_bom','=', True)]", string="BOM")

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


class MRPProduction(models.Model):
    _inherit = 'mrp.production'

    is_service_eng = fields.Boolean()
    is_assembly_superivisor = fields.Boolean()
    service_eng_id = fields.Many2one('res.users')
    assembly_eng_id = fields.Many2one('res.users')

    def superEng_btn(self):
        if not self.is_service_eng:
            self.is_service_eng = True

    def is_assembly_superivisor_btn(self):
        if not self.is_assembly_superivisor:
            self.is_assembly_superivisor = True

    # {'invisible': ['|', '|', ('state', 'in', ('draft', 'cancel', 'done', 'to_close')), ('qty_producing', '=', 0), ('move_raw_ids', '=', []), ('is_service_eng', '=', False), ('is_assembly_superivisor', '=', False)]}


class ProductTemplateOperationVendor(models.Model):

    _name = 'product.tmpl.operation.vendor'

    partner_id = fields.Many2one('res.partner')
    product_tmpl_id = fields.Many2one('product.template')


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    vendor_list_ids = fields.One2many(
        'product.tmpl.operation.vendor', 'product_tmpl_id')


# class ResPartner(models.Model):

#     _inherit = 'res.partner'

#     product_id = fields.Many2one('product.template')


class MrpBom(models.Model):

    _inherit = 'mrp.bom'

    is_child_bom = fields.Boolean("Is Part?")
    vendor_list_ids = fields.One2many(
        related="product_tmpl_id.vendor_list_ids")

    @api.constrains('operation_ids', 'byproduct_ids', 'type')
    def _check_subcontracting_no_operation(self):
        return False


class MrpRoutingWorkcenter(models.Model):

    _inherit = 'mrp.routing.workcenter'

    allowed_vendors_ids = fields.Many2many(
        'res.partner', compute="_compute_allowed_value_ids")
    vendor_id = fields.Many2one(
        'res.partner', domain="[('id', 'in', allowed_vendors_ids)]")

    @api.depends('bom_id.product_tmpl_id')
    def _compute_allowed_value_ids(self):
        for rec in self:
            rec.allowed_vendors_ids = self.env['res.partner'].search(
                [('id', '=', self.bom_id.product_tmpl_id.vendor_list_ids.mapped('partner_id.id') or [])])
