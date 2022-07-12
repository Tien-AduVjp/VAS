$(function(){
	$.when(...window.to_website_doc_defs).done(function() {
		window.myPage.start();
	});
});