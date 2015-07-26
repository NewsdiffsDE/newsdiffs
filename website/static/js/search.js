// $(window).load(function () {
	
// 	$("#search-input-line").focus(function(e) {
// 		console.log(e);
// 		console.log(e.target);
// 		$("#search-foldout").show();
// 	}).blur(function()	{
// 		$("#search-foldout").hide();
// 	});
// });

// document.getElementById("stichwort-link").addEventListener("click", function(){
// 	console.log("hey");
// 	document.getElementById("search-input-line").placeholder = "Stichwort";
// });



var hideElementFunction = function(element) {
	console.log(element + ' hidden!');
	$(element).hide();
};

var showElementFunction = function(element) {
	$(element).show();
};

var chooseListItemFunction = function(e) {
	console.log('click event');
	console.log(e.target);
	// handle this!
	// Weil je nach Kick-Ziel (Link, Icon, Listenelement) etwas anderes das Target ist, muss man ggf suchen.
	var clickedListItem;
	if (e.target.tagName.toUpperCase() === 'LI') {
		clickedListItem = $(e.target);
	} else {
		clickedListItem = $(e.target).closest('li');
	}
	console.log(clickedListItem);

	// Und nun kann man ID und Text auslesen und damit weiterarbeiten:
	// console.log(clickedListItem.attr('id'));
	console.log(clickedListItem.text());

	var icon = document.createElement("span");
	icon.className = "glyphicon glyphicon-link";

	//Input Zeile füllen
	document.getElementById("search-input-line").placeholder = clickedListItem.text();
    document.getElementById("search_type").value = clickedListItem.text();

	//Wieder einklappen und Cursor platzieren
	$("#search-input-line").focus();
	//$("#search-foldout").hide();
};

$(window).load(function () {

	var searchInputLineElement = document.getElementById('search-input');
	var searchFoldOutElement = document.getElementById('search-foldout');
	var searchElement = document.getElementById('search-element');
	var body = document.body;
    var dateElement = document.getElementById('datepicker');
    var sortButton = document.getElementById('sortbutton');


	searchInputLineElement.onclick = function(e) {
		showElementFunction(searchFoldOutElement);
	};

	searchFoldOutElement.onclick = function(e) {
		chooseListItemFunction(e);
		hideElementFunction(searchFoldOutElement);
	};

    //advice from https://css-tricks.com/dangers-stopping-event-propagation/
	$(document).on('click', function(event) {
		if (!$(event.target).closest('#search-element').length) {
			hideElementFunction(searchFoldOutElement);
		}
	});

    $.fn.datepicker.dates['de'] = {
            days: ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"],
            daysShort: ["Son", "Mon", "Din", "Mit", "Don", "Fre", "Sam"],
            daysMin: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],
            months: ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"],
            monthsShort: ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
            today: "Heute",
            clear: "Löschen"
    };

    $('#datepicker').datepicker({
        //format: "dd/mm/yyyy",
        format: "dd.mm.yyyy",
        clearBtn: true,
        endDate: '+0d',
        todayHighlight: true,
        language: 'de',
        autoclose: true
    }).on("changeDate", function(e){
        date_value = $('#datepicker').val();
        var date_regex = /date=\d{2}([./-])\d{2}\1\d{4}$/;
        var date_tag = "date=";
        var url = window.location.href;

        if(url.indexOf(date_tag) > -1){
            index = url.indexOf(date_tag);
            end = url.length;
            suburl = url.substring(index, end);
            leer = url.substring(index+5,index+6);
            if(leer == ''){
                suburl = suburl.replace("date=", "date="+date_value);
            }else{
                suburl = suburl.replace(date_regex, "date="+date_value);
            }
            url = url.substring(0,index)+suburl;
        }else{
            concat = '?';
            if(url.indexOf(concat) > -1){
                concat = '&';
            }
            url = url+concat+date_tag+date_value;
        }
        window.location = url;
    });


    $('#sort-btn').click(function(){
        $(this).text(function(i,old){
            return old=='Sortieren & Filtern verbergen' ?  'Sortieren & Filtern anzeigen' : 'Sortieren & Filtern verbergen';
        });
    });

});
