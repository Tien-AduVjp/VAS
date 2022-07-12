odoo.define('to_website_search_suggestion.field_suggestion', function(require){
  "use strict";

  var snippet_animation = require('website.content.snippets.animation');

  snippet_animation.registry.field_suggestion = snippet_animation.Class.extend({

    selector: '.js_website_suggestion',

    suggestion: function(request, response) {
      var self = this;
      var domain = [[this.valueField, 'ilike', request.term]];
      if (this.add_domain) {
        domain = domain.concat(this.add_domain);
      }
      return $.ajax({
        dataType: 'json',
        url: '/website/field_suggestion/' + self.model,
        method: 'GET',
        data: {
          domain: JSON.stringify(domain),
          fields: JSON.stringify(self.fields),
          limit: self.limit,
        },
      }).then(function(records) {
            var data =[];
            Object.keys(records).map(function(key, index) {
                data.push(records[key]);
            });
            var result = data.reduce(function(a, b) {
    		  a.push({label: b[self.displayField], value: b[self.valueField]});
			  return a;
          }, []);
          response(result);
          return records;
        });
    },
    
    /* Return arguments that are used to initialize autocomplete */
    autocompleteArgs: function() {
      var self = this;
      return {
        source: function(request, response) {
          self.suggestion(request, response);
        },
        select: function( event, ui ) {
        	$('.js_website_suggestion').val(ui.item.value);
        	$('.oe_search_button').click();
    	},
    	open: function( event, ui ) {
    		$('.ui-autocomplete').find("li").each(function(i, e){
    			var html = $(this).html();
    			html = html.replace(/&lt;/g, "<").replace(/&gt;/g, ">");
    			$(this).html(html);
    		});
    		$('.ui-autocomplete').css("width", "auto").css("min-width", "287px");
    	}
      };
    },
    
    start: function() {
      this.model = this.$target.data('model');
      this.queryField = this.$target.data('query-field') || 'name';
      this.displayField = this.$target.data('display-field') || this.queryField;
      this.valueField = this.$target.data('value-field') || this.displayField;
      this.limit = this.$target.data('limit') || 10;
      this.add_domain = this.$target.data('domain');
      this.fields = this.queryField.split(" ")
      this.$target.autocomplete(this.autocompleteArgs());
    },
    
  });
    
  return snippet_animation.registry.field_suggestion;

});
