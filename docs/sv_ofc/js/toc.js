$('[data-toggle=collapse]').click(function() {
    $(this).find("span").toggleClass("glyphicon-chevron-right glyphicon-chevron-down");
});

$('.select2').select2({
    placeholder : '',
    minimumInputLength : 3,
    theme : "bootstrap",
	matcher: function(params, data) {
		if ($.trim(params.term) === '')
			return data;

		if (typeof data.children === 'undefined')
			return null;

		var re=null;
		if (params.term.indexOf("*") > -1)
			var re = new RegExp(params.term.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*'), "i");

		var filteredChildren = [];
		$.each(data.children, function (idx, child) {
			if ((re !== null && child.text.match(re)) || (child.text.toUpperCase().indexOf(params.term.toUpperCase()) > -1))
				filteredChildren.push(child);
		});

		if (filteredChildren.length) {
			var modifiedData = $.extend({}, data, true);
			modifiedData.children = filteredChildren;
			return modifiedData;
		}
		return null;
	}
});

$('button[data-select2-open]').click(function() {
	$('#' + $(this).data('select2-open')).select2('open');
});

$("#toc-search").on("change", function(e) {
	parent.content.postMessage($(this).val(), "*");
	$("#toc-search").val($(this)).trigger("select2:unselect");
});

