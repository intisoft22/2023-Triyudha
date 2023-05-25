from odoo import fields, models, api


class ProductMotif(models.Model):
    _name = "product.motif"
    _description ="Product Motif"

    name =  fields.Char('Name')

class ProductTebal(models.Model):
    _name = "product.tebal"
    _description ="Product Tebal"

    name =  fields.Float('Name')

class ProductTemplate(models.Model):
    _inherit = "product.template"

    type_spec = fields.Selection([('201', '201'), ('304', '304'), ], string='Type', )
    bentuk = fields.Selection([('bulat', 'Bulat'), ('kotak', 'Kotak'), ], string='Bentuk', )
    dia = fields.Float('Diameter (mm)')
    dia_inc = fields.Float('Diameter (inc)')
    panjang = fields.Float('Panjang (mm)')
    lebar = fields.Float('Lebar (mm)')
    khl = fields.Selection([('K', 'K'), ('HL', 'HL'), ], string='K/HL', )
    motif = fields.Many2one('product.motif','Motif')
    tebal = fields.Many2one('product.tebal','Tebal')
