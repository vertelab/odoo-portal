from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class UsersImplied(models.Model):
    _inherit = 'res.users'

    group_portal_crm = fields.Selection(selection=[(4, "Portal CRM 2")])
    
    def init(self):
        self.sel_groups_1_9_10 = fields.Selection(add_selection=[(4, "Portal CRM 1")])

class Website(models.Model):
    _name = "website"
    _inherit = "website"
    
    @api.model
    def create(self, vals):
        if 'user_id' not in vals:
            company = self.env['res.company'].browse(vals.get('company_id'))
            vals['user_id'] = company._get_public_user().id if company else self.env.ref('base.public_user').id

        res = super(Website, self).create(vals)
        res._bootstrap_homepage()

        if not self.env.user.has_group('website.group_multi_website') and self.search_count([]) > 1:
            all_user_groups = 'base.group_portal,base.group_user,base.group_public,base.group_portal_crm'
            groups = self.env['res.groups'].concat(*(self.env.ref(it) for it in all_user_groups.split(',')))
            groups.write({'implied_ids': [(4, self.env.ref('website.group_multi_website').id)]})

        return res
        
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    group_show_line_subtotals_tax_excluded = fields.Boolean(
        "Show line subtotals without taxes (B2B)",
        implied_group='account.group_show_line_subtotals_tax_excluded',
        group='base.group_portal,base.group_user,base.group_public,base.group_portal_crm')
    group_show_line_subtotals_tax_included = fields.Boolean(
        "Show line subtotals with taxes (B2C)",
        implied_group='account.group_show_line_subtotals_tax_included',
        group='base.group_portal,base.group_user,base.group_public,base.group_portal_crm')
