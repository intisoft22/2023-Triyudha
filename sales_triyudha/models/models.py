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
