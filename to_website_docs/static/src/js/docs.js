window.to_website_doc_defs = [];

odoo.define('to_website_docs.docs', function(require) {
	'use strict';
	var core = require('web.core');
	var Dialog = require('web.Dialog');

	function genericJsonRpc(fct_name, params, fct) {
		var data = {
			jsonrpc : "2.0",
			method : fct_name,
			params : params,
			id : Math.floor(Math.random() * 1000 * 1000 * 1000)
		};
		var xhr = fct(data);
		var me = this;
		var result = xhr.pipe(function(result) {
			if (result.error !== undefined) {
				var userData = result.error.data;
				if (userData && userData.message) {
					try {
						Dialog.alert(null, userData.arguments[0]);
					} catch (e) {
						Dialog.alert(null, userData.message);
					}
				} else {
					Dialog.alert(null, 'Opps! error ' + result.error.code + ' -  ' + result.error.message);
				}
				busy(false);
				console.error("Server application error", result.error);
				return $.Deferred().reject("server", result.error);
			} else {
				return result.result;
			}
		}, function() {
			var def = $.Deferred();
			return def.reject.apply(def, [ "communication" ].concat($.toArray(arguments)));
		});
		result.abort = function() {
			xhr.abort && xhr.abort();
		};
		return result;
	}

	function lpad(val, len) {
		val = val + "";
		for (var i = val.length; i < len; i++) {
			val = '0' + val;
		}
		return val;
	}

	function datetime_to_str(obj) {
		if (!obj) {
			return false;
		}
		return lpad(obj.getUTCFullYear(), 4) + "-" + lpad(obj.getUTCMonth() + 1, 2) + "-" + lpad(obj.getUTCDate(), 2)
		+ " " + lpad(obj.getUTCHours(), 2) + ":" + lpad(obj.getUTCMinutes(), 2) + ":" + lpad(obj.getUTCSeconds(), 2);
	}

	function date_to_utc(k, v) {
		var value = this[k];
		if (!(value instanceof Date)) {
			return v;
		}
		return datetime_to_str(value);
	}

	var MainPage = core.Class.extend({
		init : function() {
		},
		start : function() {
			var me = this;
			var fn = function() {
				me.refresh();
			};
			this.events = [];
			window.onresize = fn;
			if (window.orientation != null) {
				$(window).on('orientationchange', fn);
			}
			this.$category = FE.getId('docsCategory');
			this.$btnCreateSubject = FE.getId('btnDocsCreateSubject');
			this.$btnDocsCreate = FE.getId('btnDocsCreate');
			this.$breadcrumb = FE.getId('docsBreadcrumb');
			this.$left = FE.getId('docsLeft');
			this.$body = FE.getId('docsBody');
			this.$version = FE.getId('docsVersion');
			if (this.initEvent) {
				this.initEvent();
			}
			if ((this.$btnCreateSubject.exists() || this.$category.exists()) && this.initEditorEvent) {
				this.category = parseInt(this.$category.val());
				this.initEditorEvent();
			}
			if ((this.$btnCreateSubject.exists() || this.$version.exists()) && this.initEditorEvent) {
				this.version= parseInt(this.$version.val());
			}

			if (this.$left.exists()) {
				this.$left.on('click', '.docs-item > .docs-arrow', function() {
					me.expandleftItem($(this).closest('.docs-item'));
				});
				FE.window.on('hashchange', function() {
					me.onHashChange();
				});
				this.checkLeftActive();
			}
		},
		onHashChange : function() {
			var me = this;
			if (!me.skipHash) {
				me.$left.find('.docs-item').each(function() {
					var $item = $(this);
					var id = $item.data('id');
					if (me.getItemEditor(id).attr('href') != null){
						var href = me.getItemEditor(id).attr('href').split('#');
						if (href.length > 1 && ('#' + href[1]) == window.location.hash) {
							me.$left.find('.docs-item.active').removeClass('active');
							$item.addClass('active');
							me.scrollToAnchor(id);
							me.anchorId = id;
							return false;
						}
					}
				});
			} else {
				me.skipHash = false;
			}
		},
		scrollToAnchor : function(id) {
			var me = this;
			clearTimeout(me.timeoutScrollToAnchor);
			me.scrollDelay = true;
			var $anchor = me.getItemAnchor(id);
			if ($anchor.exists()) {
				$anchor.scrollTo();
			} else {
				FE.getId('docsSecurity').scrollTo();
			}
			me.timeoutScrollToAnchor = setTimeout(function() {
				me.scrollDelay = false;
				me.$left.removeClass('delay');
			}, 1000);
		},
		onScrollToAnchor : function(scrollTop, subH) {
			var me = this;
			me.anchors.each(function() {
				var $e = $(this);
				var h = (scrollTop + subH) - $e.offset().top;
				if (h > 0 && h < $e.height()) {
					me.changeAnchor($e.data('id'));
					return false;
				}
			});
		},
		changeAnchor : function(id) {
			var me = this;
			if (me.anchorId != id) {
				var lastId = me.anchorId;
				me.anchorId = id;
				var $editor = me.getItemEditor(id);
				var $item = me.getItem(id);
				var $parent = me.getItemParent($editor);

				if (lastId) {
					me.getItem(lastId).removeClass('active');
					var $lastParent = me.getItemParent(me.getItemEditor(lastId));
					if ($lastParent.data('id') != $parent.data('id') && $lastParent.hasClass('open')) {
						if (!$lastParent.find('#docs-' + id).exists()) {
							me.expandleftItem($lastParent);
						}
					}
				}
				me.skipHash = true;
				window.location = $editor.attr('href');

				$item.addClass('active');
				if (!$parent.hasClass('open')) {
					me.expandleftItem($parent);
				}
			}
		},
		onScroll : function(first) {
			var me = this;
			var winOp = null;
			var win = FE.window;
			var scrollTop = win.scrollTop();
			var winH = win.height();
			var top = scrollTop + winH;
			var mainH = me.$mainMenu.height() || 0;
			var breadcrumbH = me.$breadcrumb.height();
			var breadcrumbT = me.$scrollBreadcrumb.offset().top;
			// what dose it do?
			/*if (FE.body.hasClass('fixed')) {
				breadcrumbT -= breadcrumbH;
			}*/
			if (scrollTop + mainH > breadcrumbT) {
				FE.body.addClass('fixed');
				me.$breadcrumb.addClass('fixed').css({
					'top' : mainH + 'px'
				});
			} else {
				FE.body.removeClass('fixed');
				me.$breadcrumb.removeClass('fixed').css({
					'top' : '0px'
				});
			}
			if (me.$left.exists()) {
				var bodyTop = me.$body.offset().top;
				var winTop = scrollTop + mainH + breadcrumbH;
				clearTimeout(me.timeoutScrollLeft);
				if (winTop > bodyTop) {
					var lh = me.$left.height();
					var bh = me.$body.height();
					var h = Math.max(lh, bh);
					var leftTop = winTop - bodyTop;
					var maxTop = h - lh;
					if (leftTop < maxTop) {
						if (me.scrollDelay) {
							me.$left.addClass('delay');
						}
						me.$left.removeClass('abs').addClass('fixed').css({
							'top' : (mainH + breadcrumbH) + 'px',
							'width' : me.$left.parent().width()
						});
					} else {
						me.$left.addClass('abs').css({
							'top' : maxTop + 'px'
						});
					}
					me.$left.parent().css({
						'min-height' : h + 'px'
					});
				} else {
					me.$left.removeClass('fixed delay abs').css({
						'top' : '0px',
						'width' : 'auto'
					}).parent().css({
						'min-height' : 'auto'
					});
				}
			}
			if (!me.scrollDelay) {
				me.onScrollToAnchor(scrollTop, mainH + breadcrumbH);
			}
			if (!me.initScrollOnSize) {
				me.initScrollOnSize = true;
				me.events.push(function() {
					clearTimeout(me.timeoutScrollOnSize);
					me.timeoutScrollOnSize = setTimeout(function() {
						me.onScroll();
					}, 500);
				});
			}
		},
		checkFirstScroll : function() {
			var me = this;
			if (me.$summary.height() > 200) {
				me.onScroll(true);
			} else {
				me.timeoutScroll = setTimeout(function() {
					me.checkFirstScroll();
				}, 1000);
			}
		},
		initScrollEvent : function() {
			var me = this;
			var userAgent = window.navigator.userAgent;
			me.$mainMenu = FE.getId('oe_main_menu_navbar');
			me.$scrollBreadcrumb = FE.getId('scrollDocsBreadcrumb');
			me.isIOS = userAgent.match(/iPad/i) || userAgent.match(/iPhone/i);
			me.anchors = me.$body.find('.docs-anchor');
			me.$summary = FE.getId('docsSummary');
			me.checkFirstScroll();

			if (!me.isIOS) {
				window.onscroll_old = window.onscroll;
				if (window.onscroll_old != null) {
					window.onscroll = function() {
						window.onscroll_old();
						clearTimeout(me.timeoutScroll);
						me.onScroll();
					};
				} else {
					window.onscroll = function() {
						clearTimeout(me.timeoutScroll);
						me.onScroll();
					};
				}
			} else {
				document.addEventListener('scroll', function() {
					clearTimeout(me.timeoutScroll);
					me.onScroll();
				});
				document.body.style['-webkit-overflow-scrolling'] = 'touch';
			}
		},
		initEditorEvent : function() {

		},
		refresh : function() {
			var me = this;
			var w = FE.body.width();
			var first = me.lastW == null;
			if (first || me.lastW != w) {
				me.lastW = w;
				$.each(this.events, function(i, v) {
					me.eventFn = v;
					me.eventFn();
				});
			}
		},
		jsonRpc : function(url, fct_name, params, settings) {
			return genericJsonRpc(fct_name, params, function(data) {
				return $.ajax(url, $.extend({}, settings, {
					url : url,
					dataType : 'json',
					type : 'POST',
					data : JSON.stringify(data, date_to_utc),
					contentType : 'application/json'
				}));
			});
		},
		getItemParent : function(editor) {
			var parent = editor.data('parent');
			if (parent) {
				return this.getItem(parent);
			}
			return this.getItem(editor.data('id'));
		},
		getItem : function(id) {
			return FE.getId('docs-' + id);
		},
		getItemEditor : function(id) {
			return FE.getId('docsItem-' + id);
		},
		getItemAnchor : function(id) {
			return FE.getId('anchor-' + id);
		},
		getItemContent : function(id) {
			return FE.getId('docsItemContent-' + id);
		},
		getItemAction : function(data) {
			if (data.res_model == 'website.doc.category') {
				return FE.getId('docsActionItem-c' + data.id);
			}
			return FE.getId('docsActionItem-' + data.id);
		},
		getItemVersion : function(id) {
			return FE.getId('docsItemVersion-' + id);
		},
		openLeftItem : function($item, $ul) {
			var $parentUl = $item.parent().parent('ul');
			var $parentItem = false;
			if ($parentUl.exists()) {
				$parentItem = $parentUl.parent();
			}
			if ($parentItem && !$parentItem.hasClass('open')) {
				this.openLeftItem($parentItem, $parentUl);
			}
			var timeout = setTimeout(function() {
				$item.addClass('open');
			}, 350);
			$ul.data('timeout', timeout);
		},
		expandleftItem : function($item) {
			var $ul = $item.find('> ul.docs-nav-sub');
			if ($ul.exists()) {
				if ($item.hasClass('open')) {
					clearTimeout($ul.data('timeout'));
					$item.removeClass('open');
					$ul.css({
						'height' : '0px'
					});
				} else {
					this.openLeftItem($item, $ul);
				}
			}
		},
		checkLeftActive : function() {
			var me = this;
			var active = me.$left.find('.docs-item.active');
			var activeByHash = false;
			if (window.location.hash) {
				me.$left.find('.docs-item').each(function() {
					var $item = $(this);
					var id = $item.data('id');
					if (me.getItemEditor(id).attr('href') != null )
					{
						var href = me.getItemEditor(id).attr('href').split('#');
						if (href.length > 1 && ('#' + href[1]) == window.location.hash) {
							active.removeClass('active');
							active = $item;
							activeByHash = true;
							return false;
						}
					}

				});
			}
			if (active.exists()) {
				me.expandleftItem(me.getItemParent(active));
				active.addClass('active');
				me.anchorId = active.data('id');
				if (activeByHash) {
					me.timeoutScrollToAnchor = setTimeout(function() {
						me.scrollToAnchor(me.anchorId);
					}, 1500);
				}
			}
		}
	});

	$(function(){
		window.myPage = new MainPage();
	});

	return MainPage;
});
$(document).ready(function (){
	if ($('#js-init-socials').length == 1)
		(function(d, s, id) {
			var js, fjs = d.getElementsByTagName(s)[0];
			if (d.getElementById(id))
				return;
			js = d.createElement(s);
			js.id = id;
			js.src = "//connect.facebook.net/en_US/all.js#xfbml=1";
			fjs.parentNode.insertBefore(js, fjs);
		}(document, 'script', 'facebook-jssdk'));

		(function(d, s, id) {
			var js, fjs = d.getElementsByTagName(s)[0];
			if (d.getElementById(id))
				return;
			js = d.createElement(s);
			js.id = id;
			js.src = "//apis.google.com/js/platform.js";
			js.async = true;
			js.async = true;
			fjs.parentNode.insertBefore(js, fjs);
		}(document, 'script', 'google-platform'));
});
