from openerp import models, fields, api

class sopo(models.Model):
    _inherit = 'sale.order'

    order_type = fields.Many2one('account.analytic.account', string='Order Type', required=True, domain=[('parent_id', 'ilike', 'ordertype')])
    staff = fields.Many2one('account.analytic.account', string='Staff', required=True, domain=[('parent_id', 'ilike', 'staff')])

    project = fields.Char(string='Project', required=True)
    contract = fields.Char(string='Contract No', required=True)

    sale_order = fields.One2many('purchase.order', 'related_sale', string='Related Purchase Order')
    sales_commission = fields.One2many('sales.commission', 'orders_id', string='Salesman Commission')

    prepared_by = fields.Char(string='Prepared By', readonly=True)
    approved_by = fields.Char(string='Approved By', readonly=True)

    state = fields.Selection([('draft', 'Draft Quotation'), ('quotation_approved', "To Check"), ('quotation_second', "Checked"), ('quotation_validate', "Approved"), ('sent', 'Quotation Sent'), ('cancel', 'Cancelled'), ('waiting_date', 'Waiting Schedule'), ('progress', 'Sales Order'), ('manual', 'Sale to Invoice'), ('invoice_except', 'Invoice Exception'), ('done', 'Done')])

    def action_quotation_approved(self):
        self.state = 'quotation_approved'

    def action_quotation_approve_second(self):
        self.state = 'quotation_second'

    def action_quotation_approve_validate(self):
        self.state = 'quotation_validate'

    @api.multi
    def button_preparer(self):
        user_id = self.env.user
        self.prepared_by = user_id.name


    @api.multi
    def button_approver(self):

        user_id = self.env.user
        self.approved_by = user_id.name

class purch(models.Model):
    _inherit = 'purchase.order'

    order_type = fields.Many2one('account.analytic.account', string='Order Type', required=True, domain=[('parent_id', 'ilike', 'ordertype')])
    staff = fields.Many2one('account.analytic.account', string='Staff', required=True, domain=[('parent_id', 'ilike', 'staff')])

    contractno = fields.Char(string='Contract NO', required=True)
    related_sale = fields.Many2one('sale.order', string='Related Sale Order', required=True)

    def gett(self, cr, uid, ids, related_sale, context=None):
        result = {}
        if related_sale:
            obj = self.pool.get('sale.order').browse(cr, uid, related_sale, context=context)
            result['contractno'] = obj.contract
        return {'value': result}

class commission(models.Model):
    _name = 'sales.commission'

    orders_id = fields.Many2one('sale.order')

    def getres(self):
        self.sales_value = self.orders_id.amount_total

    def getcommission(self):
        self.commission = (self.sales_value * self.percent) / 100


    sales_value = fields.Float(compute=getres, string='Sales Value')
    percent = fields.Float('Percentage')
    commission = fields.Float(compute=getcommission, string='Commission')
    user = fields.Many2one('res.users', 'User')

class invoiceline(models.Model):
    _inherit = 'account.invoice'

    order_type = fields.Many2one('account.analytic.account', string='Order Type', required=True, domain = [('parent_id', 'ilike', 'ordertype')])
    staff = fields.Many2one('account.analytic.account', string='Staff', required=True, domain = [('parent_id', 'ilike', 'staff')])

class passinvoice(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self, cr, uid, order, lines, context=None):

        res = super(passinvoice, self)._prepare_invoice(cr, uid, order, lines, context=context)
        res.update({'order_type': order.order_type.id, 'staff': order.staff.id})
        return res

class stock_move(models.Model):

    _inherit = "stock.picking"

    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move, context=None):
        print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", self
        res = super(stock_move, self)._get_invoice_vals(cr, uid, key, inv_type, journal_id, move, context=context)
        sale = move.picking_id.sale_id
        if sale and inv_type in ('out_invoice', 'out_refund'):
            res.update({'order_type': sale.order_type.id,'staff': sale.staff.id})
        return res