var docs_editor_def = $.Deferred();
window.to_website_doc_defs.push(docs_editor_def);

odoo.define('to_website_docs.editor', function(require) {
	'use strict';
	var core = require('web.core');
	var QWeb = core.qweb;
	var ajax = require('web.ajax');
	var Dialog = require('web.Dialog');
	var MainPage = require('to_website_docs.docs');
	var weWidgets = require('wysiwyg.widgets');
	var rootWidget = require('root.widget');
	var _t = core._t;
	ajax.loadXML('/to_website_docs/static/src/xml/qweb.xml', QWeb);

	/**
	 * The Link Dialog allows to customize link content and style.
	 */
	var DocumentDialog = Dialog.extend({
		template : 'DialogDocument',
		events : _.extend({}, Dialog.prototype.events, {}),
		init : function(parent, options, editable, dataInfo) {
			this._super(parent, _.extend({}, {
				title : options.title || _t("Document"),
				size : 'medium'
			}, options || {}));
			this.editable = editable;
			this.data = dataInfo || {};
			this.method = options.method;
		},
		start : function() {
			this.bind_data();
			return this._super.apply(this, arguments);
		},
		get_data : function(test) {
			var self = this;
			var def = new $.Deferred();
			var $e = this.$("#document-name");
			var val = $e.val();
			if (!test && (!val || !$e[0].checkValidity())) {
				$e.closest('.form-group').addClass('has-error');
				$e.focus();
				return false;
			}
			return _.extend(self.data, {
				name : val,
			});
		},
		save : function() {
			var data = this.get_data();
			if (!data) {
				return false;
			}
			return myPage.jsonRpc('/docs/' + this.method, 'call', data);
		},
		bind_data : function() {
			var $e = this.$("#document-name");
			$e.val(this.data.name);
			$e.focus();
			$e.bind('keyup', function(e) {
				if (e.keyCode == 13) {
					$(this).closest('.modal-body').next().find('.btn-primary').click();
					e.preventDefault();
					return false;
				}
			});
		}
	});


	var contextMethod = {
		create : function(data) {
			if (!data.write) {
				return;
			}
			myPage.displayDialog(_t('New of') + ' ' + data.name, 'create', _t("Create"), {
				category_id : myPage.category,
				parent_id : data.id
			});
		},
		create_category : function(data) {
			if (!data.write && data.type != 'subject') {
				return;
			}
			myPage.displayDialog(_t('New of') + ' ' + data.name, 'create_category', _t("Create"), {
				category : myPage.category,
				parent_id : data.id
			});
		},
		change_cols : function(data, value) {
			if (!data.write) {
				return;
			}
			busy(true);
			return myPage.jsonRpc('/docs/update_category', 'call', {
				category_id : data.id,
				css_section : value
			}).then(function(result) {
				if (result) {
					window.location.reload();
				}
			}).fail(function() {
				setTimeout(function() {
					window.location.reload();
				}, 1000);
			}).always(function() {
				busy(false);
			});
		},
		change_item_cols : function(data, value) {
			if (!data.write) {
				return;
			}
			busy(true);
			return myPage.jsonRpc('/docs/update_category', 'call', {
				category_id : data.id,
				css_section_item : value
			}).then(function(result) {
				if (result) {
					window.location.reload();
				}
			}).fail(function() {
				setTimeout(function() {
					window.location.reload();
				}, 1000);
			}).always(function() {
				busy(false);
			});
		},
		change_image : function(data) {
			if (!data.write) {
				return;
			}
			var me = this;
			var $image = data.$el.find('img');

			var _editor = new weWidgets.MediaDialog(rootWidget, {
										onlyImages: true,
										res_model: 'ir.ui.view',
									}, null, $image[0]).open();

			_editor.on('save', me, function(img) {
				var src = img?.src || $image.attr('src');
				busy(true);
				return myPage.jsonRpc('/docs/update_category', 'call', {
					category_id : data.id,
					image : src
				}).then(function() {
					if($image.length) $image.attr('src', src);
				}).fail(function() {
					setTimeout(function() {
						window.location.reload();
					}, 1000);
				}).always(function() {
					busy(false);
					_editor.close();
				});
			});
		},
		edit : function(data) {
			if (!data.write) {
				return;
			}
			if (data.res_model == 'website.document') {
				myPage.displayDialog(_t('Edit') + ' ' + data.name, 'update_document', _t("Save"), {
					document_id : data.id,
					name : data.name
				});
			} else {
				myPage.displayDialog(_t('Edit') + ' ' + data.name, 'update_category', _t("Save"), {
					category_id : data.id,
					name : data.name
				});
			}
		},
		change_to_link : function(data) {
			this._change_document_type(data, 'link');
		},
		change_to_hash : function(data) {
			this._change_document_type(data, 'hash');
		},
		_change_document_type : function(data, type) {
			if (!data.write) {
				return;
			}
			busy(true);
			return myPage.jsonRpc('/docs/update_category', 'call', {
				category_id : data.id,
				document_type : type
			}).then(function(result) {
				if (result) {
					window.location.reload();
//					window.location = result.url;
				}
			}).fail(function() {
				setTimeout(function() {
					window.location.reload();
				}, 1000);
			}).always(function() {
				busy(false);
			});
		},
		full_edit : function(data) {
			if (!data.write) {
				return;
			}
			busy(true);
			return myPage.jsonRpc('/docs/view_edit', 'call', {
				res_id : data.id,
				res_model : data.res_model
			}).then(function(result) {
				if (result) {
					window.location = result;
				}
			}).fail(function() {
				setTimeout(function() {
					window.location.reload();
				}, 1000);
			}).always(function() {
				busy(false);
			});
		},
		'action_context_delete' : function(data) {
			if (!data.unlink) {
				return;
			}
			var self = this;
			Dialog.confirm(null, _t("Delete") + " " + data.name + "?", {
				title : _t("Delete"),
				confirm_callback : function() {
					busy(true);
					return myPage.jsonRpc('/docs/delete', 'call', {
						res_id : data.id,
						res_model : data.res_model
					}).then(function(result) {
						window.location = result;
						if (data.res_model == 'website.document') {
							myPage.getItem(data.id).remove();
							myPage.getItemContent(data.id).remove();
						}
					}).always(function() {
						busy(false);
					});
				}
			});
		},
		cancel : function(data) {
			if (!data.write) {
				return;
			}
			this.change_status(data, 'cancelled');
		},
		draft : function(data) {
			if (!data.write) {
				return;
			}
			this.change_status(data, 'draft');
		},
		confirm : function(data) {
			if (!data.write) {
				return;
			}
			this.change_status(data, 'confirmed');
		},
		approve : function(data) {
			if (!data.approve) {
				return;
			}
			this.change_status(data, 'approved');
		},
		approve_publish : function(data) {
			this.change_status(data, 'approved', true);
		},
		_change_status : function(data, result) {
			result = result.state;
			var action = myPage.getItemAction(data);
			var item = myPage.getItem(data.id);
			this._change_display_status(action, data, result);
			this._change_display_status(item, data, result);
			return item;
		},
		_change_display_status : function($el, data, result) {
			var old = $el.data('state');
			$el.data('state', result);
			$el.attr('data-state', result);
			$el.find('.docs-status').removeClass('docs-' + old).addClass('docs-' + result);
		},
		change_status : function(data, status, published) {
			var self = this;
			busy(true);
			published = published || false;
			return myPage.jsonRpc('/docs/change_status', 'call', {
				res_id : data.id,
				res_model : data.res_model,
				state : status,
				published : published
			}).then(function(result) {
				var item = self._change_status(data, result);
				if (status == 'draft') {
					published = true;
				}
				if (published) {
					self._toggle_published(data, result);
				}
				if (item) {
					item.find('.docs-editable').each(function() {
						var params = {
							id : $(this).data('id')
						};
						self._change_status(params, result);
						if (published) {
							self._toggle_published(params, result);
						}
					});
				}
			}).always(function() {
				busy(false);
			});
		},
		publish : function(data) {
			this.toggle_published(data, true);
		},
		unpublish : function(data) {
			this.toggle_published(data, false);
		},
		_toggle_published : function(data, result) {
			if($('.js_publish_management').length == 0)
				return location.reload();
			$('.js_publish_btn input#id').prop("checked", result.website_published );
			if(result.website_published){
				$('.js_publish_management').removeClass('css_unpublished');
				$('.js_publish_management').addClass('css_published');
			}else{
				$('.js_publish_management').removeClass('css_published');
				$('.js_publish_management').addClass('css_unpublished');
			}

			result = result.website_published;
			result = result ? 'on' : 'off';
			var action = myPage.getItemAction(data);
			var item = myPage.getItem(data.id);
			var version = myPage.getItemVersion(data.id)
			this._change_display_publish(action, data, result);
			this._change_display_publish(item, data, result);
			this._change_display_publish(version, data, result);
			return item;
		},
		_change_display_publish : function($el, data, result) {
			var old = $el.data('publish');
			$el.data('publish', result);
			$el.attr('data-publish', result);
		},
		toggle_published : function(data, publish) {
			if ((data.res_model == 'website.document' || data.res_model == 'website.document.content') && !data.approve) {
				return;
			}
			if (data.res_model == 'website.doc.category' && !data.write) {
				return;
			}
			var self = this;
			busy(true);
			return myPage.jsonRpc('/docs/toggle_published', 'call', {
				res_id : data.id,
				res_model : data.res_model,
				publish : publish,
			}).then(function(result) {
				var item = self._toggle_published(data, result);
				if (item) {
					item.find('.docs-editable').each(function() {
						self._toggle_published({
							id : $(this).data('id')
						}, result);
					});
				}
				window.location.reload();
			}).always(function() {
				busy(false);
			});
		}
	}; // contextMethod
	var website_root = require('website.root').WebsiteRoot;
	var document_website_root = website_root.include({

		events: _.extend({}, {
        		'click .js_publish_management .js_publish_btn': '_onPublishBtnClick',
    		}),
		_onPublishBtnClick : function(ev){
			this._super.apply(this, arguments);
			if ($(".js_publish_management").data('object') != 'website.document.content'){
				return;
			}
			var isPublic = Boolean($('.css_unpublished').length)
       		if (isPublic == true) {
				$('a.badge.badge-primary').attr("data-publish","on");
				$('.js-public').text('Published');
			}
			else{
				$('a.badge.badge-primary').attr("data-publish","off");
				$('.js-public').text('Not Published');
			}

		},
	});

	MainPage.include({
		displayDialog : function(title, method, saveLabel, params, fnc) {
			var me = this;
			var dialog = new DocumentDialog(null, {
				method : method,
				title : title,
				buttons : [ {
					text : saveLabel,
					classes : 'btn-primary',
					close : false,
					click : function() {
						if (fnc) {
							me.callbackDialog = fnc;
							me.callbackDialog();
						} else {
							var refer = dialog.save();
							if (refer) {
								busy(true);
								refer.then(function(result) {
									if (result.url == '#') {
										window.location.reload();
									} else {
										window.location = result.url;
									}
								}).always(function() {
									busy(false);
								});
							}
						}
					}
				}, {
					text : _t("Close"),
					classes : 'btn-default',
					close : true
				} ]
			}, true, params).open();
			setTimeout(function() {
				FE.getId('document-name').focus();
			}, 200);
			return dialog;
		},
		onSorting : function($e, parent) {
			var ids = [];
			$e.children().each(function() {
				ids.push($(this).data('id'));
			});
			if (ids.length > 1) {
				busy(true);
				return myPage.jsonRpc('/docs/resequence', 'call', {
					ids : ids,
					parent : parent || false,
					category : myPage.category
				}).fail(function() {
					setTimeout(function() {
						window.location.reload();
					}, 1000);
				}).always(function() {
					busy(false);
				});
			}
		},
		initEditorEvent : function() {
			var me = this;
			me.onTagEvent();
			me.onLeftEvent();
			me.onCategoryEvent();
			var isMobile = false
			if (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase())) isMobile= true;

			var $btnCover = FE.getId('btnDocsChangeCover');
			if ($btnCover.exists()) {
				$btnCover.click(function(e) {
					me.onChangeCover();
				});
				me.onChangeColor();
			}

			if (me.$btnCreateSubject.exists()) {
				me.$btnCreateSubject.click(function() {
					myPage.displayDialog(_t('New Subject'), 'create_category', _t("Create"), {});
				});

				if (!me.$btnCreateSubject.hasClass('no-content')) {
					var rootSubject = me.$btnCreateSubject.parent().find('> .row');
					if(!isMobile){
						rootSubject.sortable({
							items : '> div',
							delay : 100,
							revert : 100,
							stop : function(event, ui) {
								me.onSortingCategory(rootSubject);
							}
						});
					}
				}
			}

			var $btnCreateSection = FE.getId('btnDocsCreateSection');

			if ($btnCreateSection.exists()) {
				$btnCreateSection.click(function() {
					myPage.displayDialog(_t('New Section'), 'create_category', _t("Create"), {
						parent_id : me.category
					});
				});

				if (!$btnCreateSection.hasClass('no-content')) {
					var rootSection = $btnCreateSection.parent().find('> .row');
					if(!isMobile){
						rootSection.sortable({
							items : '> div',
							delay : 100,
							revert : 100,
							stop : function(event, ui) {
								me.onSortingCategory(rootSection, me.category, '.cat-section.cat-editable');
							}
						});

						rootSection.find('> div > .row').each(function() {
							var $section = $(this);
							$section.sortable({
								items : '> div.category-item',
								delay : 100,
								revert : 100,
								stop : function(event, ui) {
									var $target = $(event.target);
									me.onSortingCategory($target, $target.find('> .cat-editable').data('id'));
								}
							});
						});
					}
				}
			}
		},
		openContext : function($context) {
			var me = this;
			FE.body.unbind('click.pcontext').bind('click.pcontext', function(e) {
				var $target = $(e.target);
				if (!$target.hasClass('fa-cog') && !$target.hasClass('popover-context')
				&& !$target.closest('.popover-context').exists()) {
					me.removeOpenedContext($context);
				}
			});
		},
		closeOpenedContext : function() {
			var $context = FE.body.find('.popover-context');
			if ($context.exists()) {
				this.removeOpenedContext($context);
			}
		},
		removeOpenedContext : function($context) {
			FE.body.unbind('click.pcontext');
			$context.parent().find('> .fa-cog').removeClass('active');
			$context.remove();
		},
		onContextEvent : function(name, selector, dataFn) {
			var me = this;
			FE.body.on('click', selector + ' .fa-cog', function() {
				var $target = $(this);
				var $el = $target.closest(selector);
				if ($target.hasClass('active')) {
					if ($el.data('context')) {
						$el.data('context').remove();
					}
					$target.removeClass('active');
				} else {
					$target.addClass('active');
					me.closeOpenedContext();
					var data = dataFn($el);
					var context = $(QWeb.render(name, {
						options : data
					}));
					context.insertBefore($target);
					data.$el = $el;
					context.data('data', data);
					$el.data('context', context);
					me.openContext(context);
					context.on('click', '.docs-context-item', function() {
						var $this = $(this);
						var $context = $this.closest('.popover-context');
						if ($this.hasClass('dropdown')) {
							if ($this.hasClass('open')) {
								$this.removeClass('open');
							} else {
								$this.parent().find('> .open').removeClass('open');
								$this.addClass('open');
							}
						} else {
							if ($this.data('method')) {
								if (contextMethod[$this.data('method')]) {
									contextMethod[$this.data('method')]($context.data('data'), $this.data('value'));
								}
							}
							me.removeOpenedContext($context);
						}
					});
				}
			});
		},
		onCategoryEvent : function() {
			var me = this;
			me.onContextEvent('ContextCategory', '.cat-editable', function($el) {
				var data = {};
				data.id = $el.data('id');
				data.res_model = 'website.doc.category';
				data.type = $el.data('type');
				data.name = $el.data('name');
				data.is_hash = $el.data('document-type') == 'hash';
				data.publish = $el.data('publish');
				data.position = $el.data('position') || 'right';
				var role = $el.data('role')
				data.write = role.role_write;
				data.unlink = role.role_unlink;
				data.create = role.role_create;
				return data;
			});
		},
		onTagEvent : function() {
			var me = this;
			me.$txtTags = FE.getId('txtTags');
			if (me.$txtTags.exists()) {
				me.$txtTags.keyup(function(e) {
					if (e.keyCode == 40) {
						if (me.$searchTags && me.$searchTags.exists()) {
							me.$searchTags.focus();
						}
					} else if (e.keyCode == 13) {
						var val = $.trim(me.$txtTags.val());
						if (val.length > 0) {
							me._closeSearchTags();
							me.addTags({
								name : val
							});
						}
					} else {
						me.onKeySearchTags();
					}
				}).blur(function() {
					me.onCloseSearchTags();
				}).focus(function() {
					me.searchTagsClosed = false;
				});

				me.$tags = me.$txtTags.closest('.docs-tags');
				me.$tags.on('click', '.fa-remove', function() {
					var $e = $(this);
					me.removeTags({
						tag : $e.data('tag')
					}).then(function() {
						me.keySearchTags = false;
						$e.parent().remove();
					});
				});
				me.tagsData = {
					res_id : me.$txtTags.data('id'),
					res_model : me.$txtTags.data('category') ? 'website.doc.category' : 'website.document'
				}
			}
		},
		onLeftEvent : function() {
			var me = this;
			var isMobile = false
			if (/android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase())) isMobile=  true;
			if (me.$left.exists()) {
				if(!isMobile){
					me.$left.sortable({
						items : '> .docs-sortable',
						delay : 100,
						revert : 100,
						stop : function(event, ui) {
							me.onSorting($(event.target));
						}
					});

					me.$left.find('.docs-nav-sub').each(function() {
						$(this).sortable({
							items : '> .docs-sortable',
							delay : 100,
							revert : 100,
							stop : function(event, ui) {
								me.onSorting($(event.target), $(event.target).parent().data('id'));
							}
						});
					});
				}

				var me = this;
				me.onContextEvent('ContextDocument', '.docs-editable', function($el) {
					var data = {};
					data.id = $el.data('id');
					data.name = $el.data('name');
					data.state = $el.data('state');
					data.publish = $el.data('publish');
					data.position = $el.data('position') || 'right';

					data.res_model = 'website.document';
					data.write = $el.data('write');
					data.unlink = $el.data('unlink');
					data.parent = $el.data('parent');
					data.approve = $el.data('approve');

					return data;
				});

				me.onContextEvent('ContextDocumentContent', '.docs-content-editable', function($el) {
					var data = {};
					data.id = $el.data('id');
					data.name = $el.data('name');
					data.state = $el.data('state');
					data.publish = $el.data('publish');
					data.position = $el.data('position') || 'right';

					data.res_model = 'website.document.content';
					data.write = $el.data('write');
					data.unlink = $el.data('unlink');
					data.parent = $el.data('parent');
					data.approve = $el.data('approve');

					return data;
				});

				FE.getId('btnDocsCreate').click(function() {
					me.displayDialog(_t('New Document'), 'create', _t("Create"), {
						category_id : me.category,
						version_id: me.version,

					});
				});
			}
		},
		onSortingCategory : function($el, category, selector) {
			if (!selector) {
				selector = '> .cat-editable';
			}
			var ids = [];
			$el.children().each(function() {
				var $item = $(this).find(selector).first();
				if ($item.exists()) {
					ids.push($item.data('id'));
				}
			});
			if (ids.length > 1) {
				busy(true);
				return myPage.jsonRpc('/docs/resequence_category', 'call', {
					ids : ids,
					parent : category || false
				}).fail(function() {
					setTimeout(function() {
						window.location.reload();
					}, 1000);
				}).always(function() {
					busy(false);
				});
			}
		},
		onChangeColor : function() {
			var $input = FE.getId('evol-colorpicker');
			$input.colorpicker({
				defaultPalette : 'web'
			});
			$input.change(function() {
				var val = $.trim($input.val());
				if (val) {
					busy(true);
					return myPage.jsonRpc('/docs/update_category', 'call', {
						category_id : FE.getId('imgSummary').data('id'),
						color_cover : val
					}).then(function(result) {
						FE.getId('colorSummary').css({
							'background' : result.color_cover
						});
					}).fail(function() {
						setTimeout(function() {
							window.location.reload();
						}, 1000);
					}).always(function() {
						busy(false);
					});
				}
			});
		},
		onChangeCover : function() {
			var me = this;
			var $image = FE.getId('imgSummary');
			var _editor = new weWidgets.MediaDialog(rootWidget, {
										onlyImages: true,
										res_model: 'ir.ui.view',
									}, null, $image[0]).open();

			_editor.on('save', me, function(img) {
				var src = img.src;
				busy(true);
				return myPage.jsonRpc('/docs/update_category', 'call', {
					category_id : $image.data('id'),
					image_cover : src
				}).then(function() {
					if($image.length) $image.attr('src',img.src);
				}).fail(function() {
					setTimeout(function() {
						window.location.reload();
					}, 1000);
				}).always(function() {
					busy(false);
					_editor.close();
				});
			});
		},
		_closeSearchTags : function() {
			if (this.$searchTags) {
				this.$searchTags.remove();
				this.$searchTags = false;
				this.searchTagsClosed = false;
			}
		},
		addTags : function(vals) {
			busy(true);
			var me = this;
			vals = _.extend(vals, me.tagsData);
			myPage.jsonRpc('/docs/add_tags', 'call', vals).then(function(result) {
				if (result) {
					me.keySearchTags = false;
					me.$txtTags.val(null);
					var $e = $('<span class="pull-left docs-tag docs-tag-editor">' + '<a class="badge badge-info" href="'
					+ result.url + '">' + result.name + '<i class="fa fa-remove" data-tag="' + result.id
					+ '" /></a></span>');
					$e.insertBefore(me.$txtTags.parent());
				}
			}).always(function() {
				busy(false);
			});
		},
		removeTags : function(vals) {
			var me = this;
			vals = _.extend(vals, me.tagsData);
			busy(true);
			return myPage.jsonRpc('/docs/remove_tags', 'call', vals).always(function() {
				busy(false);
			});
		},
		onKeySearchTags : function() {
			var me = this;
			clearTimeout(me.timeoutSearchTags);
			me._closeSearchTags();
			me.timeoutSearchTags = setTimeout(function() {
				var val = $.trim(me.$txtTags.val());
				if (val.length > 0) {
					if (!me.keySearchTags) {
						me.keySearchTags = {};
					}
					var data = me.keySearchTags[val];
					if (data == null) {
						me.keySearchTags[val] = null;
						return myPage.jsonRpc('/docs/search_tags', 'call', _.extend({
							search : val
						}, me.tagsData)).then(function(result) {
							me.keySearchTags[result.key] = result.data;
							me.loadSearchTags(result.data);
						});
					} else {
						me.loadSearchTags(data);
					}
				}
			}, 500);
		},
		onCloseSearchTags : function() {
			var me = this;
			me.searchTagsClosed = true;
			clearTimeout(me.timeoutCloseSearchTags);
			me.timeoutCloseSearchTags = setTimeout(function() {
				if (me.searchTagsClosed) {
					me._closeSearchTags();
				}
			}, 1000);
		},
		loadSearchTags : function(data) {
			var me = this;
			me._closeSearchTags();
			if (data.length > 0) {
				me.$searchTags = $("<ul class=\"search-data\"/>");
				me.$searchTags.attr('tabindex', 0);
				var lis = "";
				$.each(data, function(i, v) {
					lis += "<li data-tag=\"" + v.id + "\"><a>" + v.name + "</a></li>";
				});
				me.$searchTags.html(lis);
				var parent = me.$txtTags.parent();
				me.$searchTags.appendTo(parent);

				me.$searchTags.mouseenter(function() {
					me.searchTagsClosed = false;
				}).mouseleave(function() {
					me.onCloseSearchTags();
				}).blur(function() {
					me.onCloseSearchTags();
				}).focus(function() {
					me.searchTagsClosed = false;
					var active = me.$searchTags.find('> .active');
					if (!active.exists()) {
						active = me.$searchTags.children().first();
						active.addClass('active');
					}
				}).keyup(function(e) {
					if (e.keyCode == 40) {
						var active = me.$searchTags.find('> .active');
						var elem = active.next();
						if (elem.exists()) {
							active.removeClass('active');
							elem.addClass('active');
						}
					} else if (e.keyCode == 38) {
						var active = me.$searchTags.find('> .active');
						var elem = active.next();
						if (elem.exists()) {
							active.removeClass('active');
							elem.addClass('active');
						} else {
							me.$txtTags.focus();
						}
					} else if (e.keyCode == 13) {
						me.$searchTags.find('> .active').click();
					}
				}).on('click', 'li', function() {
					me._closeSearchTags();
					me.$txtTags.val(null);
					me.addTags({
						tag : $(this).attr('id'),
						name : $(this).text().trim()
					});
				});
			}
		},
	});

	docs_editor_def.resolve();

	return {
		main_page: MainPage,
		document_dialog: DocumentDialog
	};
});
