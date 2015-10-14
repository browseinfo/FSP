openerp.fsp_livecalc = function(instance){

instance.web.FormView.include({

    init: function(parent, dataset, view_id, options) {

        this._super.apply(this, arguments);
        var self = this;
        $("button span:contains('Extra Offer')").parent().bind('click',function(e){
            e.preventDefault();
            e.stopImmediatePropagation();
            so_id = self.dataset.parent_view.datarecord.id
            new instance.web.Model("sale.order").call('extra_offer',[so_id]).done(function(res){
                if (res){
                    var url = 'http://cart.fullserviceplatform.com/ERPlivecalc/search_articles.php?boom_store_id=' + res.boom_store_id + '&quotation_id=' + so_id + '&opencartstore_id=' + res.opencart_store_id + '&token=' + $.md5(so_id)+ '&reload=['+ encodeURIComponent($(location).attr('href')) + ']'
                    window.open(url, '_blank', "toolbar=yes, scrollbars=yes, resizable=yes, top=200, left=200, width=1000, height=400");
                }
            });

        });
    }
});

}
