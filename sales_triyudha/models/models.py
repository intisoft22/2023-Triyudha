from odoo import models, fields, api


class salesCustom(models.Model):
    _inherit = 'res.partner'


    id_card_no = fields.Char(string='ID Card No')
    pricelist =  fields.Many2one('product.pricelist',
        string='Pricelist',
    )
    team_id = fields.Many2one('crm.team',
        string='Salesman',
    )
    

# class ProductPricelist(models.Model):
#     _name = 'product.pricelist'
#     _description = 'Product Pricelist'
#     _approval = {
#         'approver_field': 'user_id',
#         'approval_template_id': False,
#         'notify_after_approval': True,
#     }

#     name = fields.Char(string='Name', required=True)
#     start_date = fields.Date(string='Start Date', required=True)
#     end_date = fields.Date(string='End Date')
#     lines = fields.One2many('product.pricelist.item', 'pricelist_id', string='Pricelist Items')
#     include_tax = fields.Boolean(string='Include Tax')
#     weight_type = fields.Selection([('standard', 'Standard'), ('custom', 'Custom')], string='Weight Type', default='standard')
#     user_id = fields.Many2one('res.users', string='Responsible')
