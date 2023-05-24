from odoo import models, fields

class Pricelist(models.Model):
    _inherit = 'product.pricelist'

    def action_update_prices(self):
        # This method should be called when the prices are updated
        self.ensure_one()

        # Get the customers
        customers = self.env['res.partner'].search([('customer_rank', '>', 0)])

        # Open a wizard to select the customers to update
        return {
            'name': 'Update Prices',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'update.pricelist.wizard',
            'target': 'new',
            'context': {
                'default_pricelist_id': self.id,
                'default_customer_ids': [(6, 0, customers.ids)],
            },
        }

class UpdatePricelistWizard(models.TransientModel):
    _name = 'update.pricelist.wizard'

    pricelist_id = fields.Many2one('product.pricelist', required=True)
    customer_ids = fields.Many2many('res.partner', domain=[('customer_rank', '>', 0)])

    def action_update(self):
        self.ensure_one()

        # Update the pricelist for the selected customers
        self.customer_ids.write({'property_product_pricelist': self.pricelist_id.id})
