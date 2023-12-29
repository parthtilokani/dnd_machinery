# -*- coding: utf-8 -*-
# from odoo import http


# class QcChecklist(http.Controller):
#     @http.route('/qc_checklist/qc_checklist', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/qc_checklist/qc_checklist/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('qc_checklist.listing', {
#             'root': '/qc_checklist/qc_checklist',
#             'objects': http.request.env['qc_checklist.qc_checklist'].search([]),
#         })

#     @http.route('/qc_checklist/qc_checklist/objects/<model("qc_checklist.qc_checklist"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('qc_checklist.object', {
#             'object': obj
#         })
