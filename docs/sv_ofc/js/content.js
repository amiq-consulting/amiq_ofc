jQuery.extend( jQuery.fn, {
	within: function(p) {
		return this.filter(function() {
			return $(p).find(this).length;
		});
	}
});

/* Scroll to top instantiation */
$(function() {
    $.scrollUp({
        scrollDistance : 100,
        scrollSpeed : 400,
        easingType : 'swing',
        animation : 'fade',
        animationSpeed : 200,
        scrollText : '<span class="badge">Top <span class="glyphicon glyphicon-chevron-up"></span></span>',
    });
});

/* Change the chevron for collapsable targets */
var toggleChevronFunction = function() {
    $(this).find("span").toggleClass("glyphicon-chevron-right glyphicon-chevron-down");
};
$('[data-toggle=collapse]').click(toggleChevronFunction);
$('[data-scroll^="#"]').click(function() {
    var id = $(this).data('scroll');
    if (! $(id).hasClass('in')) {
        $(id).collapse('show');
        $(id).siblings('[data-toggle=collapse]').each(toggleChevronFunction);
    };

    var position = 0;
    if ($(id).hasClass('panel-collapse') && $(id).parent().hasClass('panel')) {
        position = $(id).parent().offset().top;
    } else {
        position = $(id).offset().top;
    }
    $('html, body').animate({
        scrollTop : position
    }, 400);
});

/* Add bookmark url */
$(function() {
    $('body').prepend('<div class="modal fade" id="save-modal" tabindex="-1" role="dialog" aria-hidden="true"><div class="modal-dialog modal-lg"><div class="modal-content"><div class="modal-header"><h4 class="modal-title">Save this URL to restore the documentation on this page:</h4></div><div class="modal-body"><textarea class="form-control save-url" rows="4" wrap="soft" readonly></textarea></div><div class="modal-footer"><button type="button" class="btn btn-default" data-dismiss="modal">Close</button></div></div></div></div>');
    $('body').prepend('<a id="bookmark"><span class="badge"><span class="glyphicon glyphicon-star"></span></span></a>');
    $('#bookmark').click(function() {
        var href = window.location.href;
        var base = href.substring(0, href.lastIndexOf("/") + 1);
        var page = href.substring(href.lastIndexOf("/") + 1, href.length);
        var $textArea = $('#save-modal textarea');
        $textArea.val(base + 'index.html?' + page);
        $textArea.click(function() {
            $(this).select();
        });
        $("#save-modal").modal('show');
    });
});

const UML_DIAGRAMS = '#package_inheritance_diagram_svg, #inheritance_diagram_svg, #collaboration_diagram_svg, #direct_associations_diagram_svg';
const DESIGN_DIAGRAMS = '#schematic_diagram_svg, #flow_diagram_svg'

$(function() {
	$('svg rect[href]')
	.on("dblclick", function (e) {
		location.href = $(this).attr("href");
	})
	.on("mouseenter", function (e) {
        if ($(this).parents(UML_DIAGRAMS).length > 0) 
        	return;
        $(this).css("stroke", "red").css("stroke-width", "5").css("stroke-dasharray", "none");
	})
	.on("mouseleave", function (e) {
        if ($(this).parents(UML_DIAGRAMS).length > 0)
        	return;
	    $(this).css("stroke", "none").css("stroke-width", "0");
	});
});

$(function() {
	$(UML_DIAGRAMS + ' ,' + DESIGN_DIAGRAMS).find('svg text[rectid]')
	.on("dblclick", function (e) {
        var candidates = $(this).closest('svg').find('#' + $(this).attr("rectid") + "[href]");
        if (candidates === undefined || candidates.length == 0)
        	return;
        
	    var rectangle = candidates.first();
        if (rectangle !== undefined)
            location.href = $(rectangle).attr("href");
	})
	.on("mouseenter", function (e) {
        var rectangle = $(this).closest('svg').find('#' + $(this).attr("rectid") + "[href]").first();
        if (rectangle !== undefined)
		    rectangle.css("stroke", "red").css("stroke-width", "5").css("stroke-dasharray", "none");
	})
    .on("mouseleave", function (e) {
        var rectangle = $(this).closest('svg').find('#' + $(this).attr("rectid") + "[href]").first();
        if (rectangle !== undefined)
		    rectangle.css("stroke", "none").css("stroke-width", "0");
	});
});

/* Add SVG Pan and Zoom */
$('ul.collapse').on('shown.bs.collapse', function () {
	if ($(this).is('#bitfield_diagram_svg')) {
		
		if ($('#bitfieldTable').length)
			return;

		var table = $('<table></table>').attr('id', 'bitfieldTable');
		var thead = $('<thead></thead>');
		var row = $('<tr></tr>');
		row.append($('<th style="display: none">Key</th>'));
		row.append($('<th></th>').text('Field'));
		row.append($('<th></th>').text('Size'));
		row.append($('<th></th>').text('Position'));
		row.append($('<th></th>').text('Access'));
		row.append($('<th></th>').text('Volatile'));
		row.append($('<th></th>').text('Reset Value'));
		row.append($('<th></th>').text('Has reset'));
		row.append($('<th></th>').text('Randomized'));
		row.append($('<th></th>').html('Individually<br>Accessible'));
		thead.append(row);
		table.append(thead);
		$(this).append(table);

		for (var key in registerModelMap) {       
			if (isNaN(key)) {
				continue;
			}

			$('#bitfieldTable').prepend('<tr>' + 
				'<td style="display:none;">' + key +'</td>' + 
				'<td>' + registerModelMap[key][0] +'</td>' + 
				'<td>' + registerModelMap[key][1] +'</td>' + 
				'<td>' + registerModelMap[key][2] +'</td>' +
				'<td>' + registerModelMap[key][3] +'</td>' +
				'<td>' + registerModelMap[key][4] +'</td>' +
				'<td>' + registerModelMap[key][5] +'</td>' +
				'<td>' + registerModelMap[key][6] +'</td>' +
				'<td>' + registerModelMap[key][7] +'</td>' +
				'<td>' + registerModelMap[key][8] +'</td>' +
			'</tr>');
		}

		$('#bitfieldTable tbody tr').click(function() {
			$(this).toggleClass('bitfieldHighlightTableRow').siblings().removeClass('bitfieldHighlightTableRow');
			var value = $(this).find('td:eq(0)').text();

			var classAttr = $('rect[x=\"' + value + '\"]').attr("class");
			if (typeof classAttr !== typeof undefined && classAttr !== false) {
				$('rect[x=\"' + value + '\"]').removeAttr("class");
				return;
			}

			$('rect[x=\"' + value + '\"]').css("stroke", "black");
			$('rect[x=\"' + value + '\"]').attr("class", "bitfieldHighlightRectangle");
			$('rect[x=\"' + value + '\"]').siblings().removeAttr("class");
		});

		return;
	}

	$container = $(this).find('div.svg-container');

	if ($container.length == 1) {
		windowHeight = $(window).innerHeight() * 0.8;
		$container.css('height', windowHeight);
		
		$containerHeight = $container.height();
		$containerWidth = $container.width();
		
		$svg = $(this).find('div.svg-container').find('svg').get(0);
		$svgHeight = 0;
		if ($svg.hasAttribute('height')) {
			$svgHeight = parseInt($svg.getAttribute('height'));
		}
		
		$svgWidth = 0;
		if ($svg.hasAttribute('width')) {
			$svgWidth = parseInt($svg.getAttribute('width'));
		}
				
		$fitSvg = ($containerHeight > $svgHeight && $containerWidth > $svgWidth) ? false : true;
		
		if ($container.data("svgPanZoomInitialized") !== "true") {
			$container.data("svgPanZoomInitialized", "true");
			var spz = svgPanZoom($svg, {
				controlIconsEnabled: true,
				zoomEnabled: true,
				panEnabled: true,
				dblClickZoomEnabled: false,
				mouseWheelZoomEnabled: true,
				minZoom: 0.5,
				maxZoom: 100,
				fit: $fitSvg,
				center: true
			});
			$(window).resize(function(){
				spz.resize();
			});
		}
	}
});


$(window).load(function() {
	
	if (typeof WaveDrom === 'undefined') {
		return;
	}

	var WaveDromFunction = function() {
		var r = $.Deferred();
		WaveDrom.ProcessAll();
		return r;
	}

	const DATA_MAP_REGISTER_SIZE_PARAMETER = "REGISTER_SIZE";
	const DATA_MAP_REPLACE_INDEX_PARAMETER = "REPLACE_INDEX";
	const DATA_MAP_HORIZONTAL_MODE_PARAMETER = "HORIZONTAL_MODE";
	const DATA_MAP_REGISTER_TITLE_PARAMETER = "REGISTER_TITLE";;
	
	var DVTEnhanceRegisterFunction = function() {
		
		if (typeof window.registerModelMap === "undefined") {
			return;
		}
				
		if (typeof window.registerModelMap[DATA_MAP_REGISTER_TITLE_PARAMETER] !== "undefined") {
			var registerTitle = document.getElementById("registerTitle");
			registerTitle.innerText = "Bitfields of reg " + window.registerModelMap[DATA_MAP_REGISTER_TITLE_PARAMETER];
		}

		// Adjust the svg image and create the tooltip rectangle
		$.each($('svg'), function(index, value) {

			if (!$(this).parent().is("div[id^='WaveDrom_Display_']")) {
				return;
			}

			const SVGHeightAttrVertical = '220';
            const SVGHeightAttrHorizontal = '125'
			if (typeof window.registerModelMap[DATA_MAP_HORIZONTAL_MODE_PARAMETER] === 'undefined') {
				$(value).attr('height', SVGHeightAttrVertical);
			} else {
				$(value).attr('height', SVGHeightAttrHorizontal);
			}
			$(value).attr('overflow', "visible");
			$(value).removeAttr('viewBox');
		});
		
		// Replace the last index with the actual size of register after cropping
		$.each($( "svg > g > g > g > text" ), function(index, value) {

			if (isNaN($(value).text())) {         // returns true if the variable does NOT contain a valid number
				return;
			}

			if (parseInt($(value).text()) === window.registerModelMap[DATA_MAP_REPLACE_INDEX_PARAMETER]) {
				$(value).text(window.registerModelMap[DATA_MAP_REGISTER_SIZE_PARAMETER]);
			}
		});


		$('rect').on('click', function(index, value) {
			var rectX = parseInt($(this).attr('x'));
			if (typeof registerModelMap[rectX] === 'undefined') {
				return;
			}

			$(this).css("stroke", "black");
			var attr = $(this).attr("class");
			if (typeof attr !== typeof undefined && attr !== false) {
				$(this).removeAttr("class");
			} else {
				$(this).attr("class", "bitfieldHighlightRectangle");
				$(this).siblings().removeAttr("class");
			}

			$.each($('#bitfieldTable tbody tr'), function (index, value) {
				if ($(this).find('td:eq(0)').text().localeCompare(rectX) == 0) {
					$(this).toggleClass('bitfieldHighlightTableRow').siblings().removeClass('bitfieldHighlightTableRow');
					return;
				}
			});
		});

		// Trim very long names in vertical mode
		if (typeof window.registerModelMap[DATA_MAP_HORIZONTAL_MODE_PARAMETER] === 'undefined') {
			const MAX_CHARS_NAME = 16;
			$.each($('text'), function (index, value) {
				var xAxisOffset = parseInt($(value).attr('x'));
				if (isNaN(xAxisOffset)) {
					xAxisOffset = 0;					
				}

                var text = $(value).text();
                
                for (var key in registerModelMap) {
                    if (registerModelMap[key][0] === text) {
                        $(value).attr("transform", "rotate(-90," + (xAxisOffset + 35) + ", 30)");
                        if (text.length > MAX_CHARS_NAME) {
                            $(value).text(text.substring(0, MAX_CHARS_NAME - 1) + "...");
                        }
                    }
                }
			});
		}
	}

  	var SetOverFlowAttribute = function() {
		$("div[id^='WaveDrom_Display_']").each( function() {
			$(this).css("overflow", "auto"); 
		});

		$("#bitfield_diagram_svg").find(".svg-container").each( function() {
			$(this).css("text-align", "center"); 
		});
  	}

  	WaveDromFunction().done(SetOverFlowAttribute(), DVTEnhanceRegisterFunction());

});

jQuery.expr[':'].icontains = function(a, i, m) {
	return jQuery(a).text().toUpperCase()
		.indexOf(m[3].toUpperCase()) >= 0;
};

$.expr[':'].textEquals = function(el, i, m) {
    var searchText = m[3].toUpperCase();
    var match = $(el).text().toUpperCase().trim().match("^" + searchText + "$")
    return match && match.length > 0;
}

function isEmpty(str) {
	return (!str || 0 === str.length);
}

$('table[id=FSMTable] > tbody > tr').click(function() {
	var prevCurrentState = $('.selected').find("td:eq(0)").text();
	var prevNextState = $('.selected').find("td:eq(1)").text();
	$('.selected').removeClass('selected');

    $(this).addClass("selected");
	
	var currentState = $(this).find("td:eq(0)").text();
	var nextState = $(this).find("td:eq(1)").text();
	
	$svg = $(this).closest("ul").find('div.svg-container > svg');
	
	if (!isEmpty(prevCurrentState)) {
		$svg.find("text:textEquals(" + prevCurrentState + ")").prev("rect").css('fill', 'white');
	}
	if (!isEmpty(prevNextState)) {
		$svg.find("text:textEquals(" + prevNextState + ")").prev("rect").css('fill', 'white');
	}

	if (!isEmpty(currentState)) {
		$svg.find("text:textEquals(" + currentState + ")").prev("rect").css('fill', 'lightcoral');
	}
	if (!isEmpty(nextState)) {
		$svg.find("text:textEquals(" + nextState + ")").prev("rect").css('fill', 'lightgreen');
	}

});


window.onload = function() {
	if (this.location.href.lastIndexOf("#") != -1) {
		var id = this.location.href.substring(this.location.href.lastIndexOf("#"), this.location.href.length)
		$(document).find(id).within("ul#fsm_diagrams").trigger( "click" );
		
		if (id.includes("bitfield_diagram"))
			$(document).find(id).trigger( "click" );
		
		var position = 0;
		if ($(id).hasClass('panel-collapse') && $(id).parent().hasClass('panel')) {
			position = $(id).parent().offset().top;
		} else {
			position = $(id).offset().top;
		}
		$('html, body').animate({
			scrollTop : position
		}, 400);
	}
};

const SUPPORTED_LANGUAGES = ['SystemVerilog', 'VHDL', 'eLanguage', 'SLN', 'M-SDL', 'PSS'];

window.addEventListener("message", function(event) {

	var href = event.data;
	if (href.indexOf('/') !== -1) { // it's a mixed project, the event has $LANGUAGE/$FILE format
		for (var i = 0; i < SUPPORTED_LANGUAGES.length; i++) {
			if (this.location.href.indexOf("/" + SUPPORTED_LANGUAGES[i] + "/") !== -1) {
				href = "../" + href; // we exit the language directory, and enter a new one from the event
				break;
			}
		}	
	}
	location.href = href;
}, false);


