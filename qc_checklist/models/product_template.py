
from odoo import models, fields, api, _


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    vendor_list_ids = fields.One2many(
        'product.tmpl.operation.vendor', 'product_tmpl_id')
    is_raw_material = fields.Boolean('Raw Material?')

    def _prepare_variant_values(self, combination):
        self.ensure_one()
        res = super(ProductTemplate, self)._prepare_variant_values(combination)
        # if self.default_code:
        print("self...................", self)
        res.update({
            'default_code':  self.default_code
        })
        return res

    @api.depends('product_variant_ids', 'product_variant_ids.default_code')
    def _compute_default_code(self):
        pass


class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.model
    def create(self, vals):

        res = super(ProductProduct, self).create(vals)
        count = self.search_count(
            [('product_tmpl_id', '=', res.product_tmpl_id.id)])

        if res.default_code:
            res.default_code = f'{res.default_code or ""}-A{count-1}'

        return res
