from openerp.osv import osv, fields

class bank_statement_line(osv.Model):
    
    _inherit = 'account.bank.statement.line'
    
    _order = 'id'
    
    
class account_period(osv.Model):
    
    _inherit = 'account.period'
    
    _order = 'company_id'