from openerp.osv import osv, fields
import yaml

class account_chart(osv.TransientModel):
    
    _inherit = 'account.chart'
    
    _columns = {
        'company_id' : fields.many2one('res.company', 'Company')
    }

    def account_chart_open_window(self, cr, uid, ids, context=None):
        retval = super(account_chart, self).account_chart_open_window(cr, uid, ids, context=context)
        data = self.read(cr, uid, ids, [], context=context)[0]
        retval['domain'] = retval['domain']
        if retval.get('context', False) and data.get('company_id', False):
            con = eval(retval['domain'])
            con = con + [('company_id','=',data['company_id'][0])]
            retval['domain'] = str(con)
        return retval
