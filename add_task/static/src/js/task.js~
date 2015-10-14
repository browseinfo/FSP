openerp.task = function (session) {
    var _t = session.web._t,
       _lt = session.web._lt;

    var mail = session.mail = {};

    openerp_mail_followers(session, mail);        // import mail_followers.js
    openerp_FieldMany2ManyTagsEmail(session);      // import manyy2many_tags_email.js
    openerp_announcement(session);
	mail.ThreadComposeMessage.include({
        bind_events: function () {
            this._super.apply(this, arguments);
			console.log("this",this);
			alert("called");		
		},		
	});
};
