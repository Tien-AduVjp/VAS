$(document).ready(function() {
	$(".form-check-input").each(function() {
		$(this).click(function() {
			var purchaseProductId = $(this).data("purchase");
			var omvId = $(this).data("omv");
			if (purchaseProductId) {
				$("#addToCart").addClass("d-none");
				$("#download").attr("href", `/my/apps/download/${omvId}?`);
				$("#download").removeClass("d-none");
			} else {
				$("#download").addClass("d-none");
				$("#addToCart").removeClass("d-none");
			}
		});
	});
});
