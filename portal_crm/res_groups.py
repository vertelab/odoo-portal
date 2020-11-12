from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class UsersImplied(models.Model):
    _inherit = 'res.users'
    
    #group_portal_crm = fields.Char("bazonk_foobar")
    
    # this function is never called!! (=> group_portal_crm not initiated)
    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if 'groups_id' in values:
                user = self.new(values)
                group_portal_crm = self.env.ref('base.group_portal_crm', raise_if_not_found=False)
                if group_portal_crm and group_portal_crm in user.groups_id:
                    gs = self.env.ref('base.group_portal_crm') | self.env.ref('base.group_portal_crm').trans_implied_ids
                else:
                    gs = user.groups_id | user.groups_id.mapped('trans_implied_ids')
                values['groups_id'] = type(self).groups_id.convert_to_write(gs, user.groups_id)
        return super(UsersImplied, self).create(vals_list)

class Website(models.Model):
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
