openerp.google_drive = function(instance, m) {
var _t = instance.web._t,
    QWeb = instance.web.qweb;

    instance.web.Sidebar.include({
        redraw: function() {
            var self = this;
	        self.$el.html(QWeb.render('Sidebar', {widget: self}));
            self.$el.find('.oe_sidebar_add_attachment').after(QWeb.render('AddGoogleItem', {widget: self}))
	        // Hides Sidebar sections when item list is empty
	        this.filenames = "";
	        this.$('.oe_form_dropdown_section').each(function() {
	            $(this).toggle(!!$(this).find('li').length);
	        });

	        self.$("[title]").tipsy({
	            'html': true,
	            'delayIn': 500,
	        })
        },
        do_attachement_update: function(dataset, model_id, args) {
            var self = this;
            this.dataset = dataset;
            this.model_id = model_id;
            if (args && args[0].error) {
                this.do_warn(_t('Uploading Error'), args[0].error);
            }
            if (args && !args[0].error && this.filenames) {
                console.log("finally file nameeeeeeeeeeeee", this.filenames);
                var fnames = this.filenames;
                var P = new instance.web.Model('ir.attachment');
                P.call('get_doc_file', [args[0].id], {'fnames':fnames});
            }
            if (!model_id) {
                this.on_attachments_loaded([]);
            } else {
                var dom = [ ['res_model', '=', dataset.model], ['res_id', '=', model_id], ['type', 'in', ['binary', 'url']] ];
                var ds = new instance.web.DataSetSearch(this, 'ir.attachment', dataset.get_context(), dom);
                ds.read_slice(['name', 'url', 'type', 'create_uid', 'create_date', 'write_uid', 'write_date'], {}).done(this.on_attachments_loaded);
            }
        },
        on_attachments_loaded: function(attachments) {
            var self = this;
            var items = [];
            var prefix = self.session.url('/web/binary/saveas', {model: 'ir.attachment', field: 'datas', filename_field: 'name'});
            _.each(attachments,function(a) {
                a.label = a.name;
                if(a.type === "binary") {
                    a.url = prefix  + '&id=' + a.id + '&t=' + (new Date().getTime());
                }
            });
            self.items['files'] = attachments;
            self.redraw();
            this.$('.oe_sidebar_add_attachment .oe_form_binary_file').change(this.on_attachment_changed);
            this.$('.oe_sidebar_add_artwork .oe_form_binary_file').change(this.on_artwork_changed);
            this.$('.oe_sidebar_add_barcode .oe_form_binary_file').change(this.on_barcode_changed);
            this.$el.find('.oe_sidebar_delete_item').click(this.on_attachment_delete);
        },
        on_artwork_changed: function(e) {
            var $e = $(e.target);
            if ($e.val() !== '') {
                this.filenames = 'Artwork';
                this.$el.find('form.oe_form_binary_form2').submit();
                $e.parent().find('input[type=file]').prop('disabled', true);
                $e.parent().find('button').prop('disabled', true).find('img, span').toggle();
                this.$('.oe_sidebar_add_attachment span').text(_t('Uploading...'));
                instance.web.blockUI();
            }
        },
        on_barcode_changed: function(e) {
            var $e = $(e.target);
            if ($e.val() !== '') {
                this.filenames = 'Shipping';
                this.$el.find('form.oe_form_binary_form3').submit();
                $e.parent().find('input[type=file]').prop('disabled', true);
                $e.parent().find('button').prop('disabled', true).find('img, span').toggle();
                this.$('.oe_sidebar_add_attachment span').text(_t('Uploading...'));
                instance.web.blockUI();
            }
        },
    });
};
