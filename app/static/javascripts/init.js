var UI = {
	flash : function(mess, type) {
		if ($('#flash').size() > 0) {
			return false;
		}
		$('body').append('<div id="flash_overlay"></div><div id="flash"><div class="'+type+'"><p>' + mess + '</p></div><button id="flash_button">OK</button></div>');
		var top = parseInt((window.innerHeight-$('#flash').height())/2);
		$('#flash').hide().css({top : top+'px'}).fadeIn(function() {
			
		});
		$('#flash_button').click(function() {
			$('#flash, #flash_overlay').fadeOut(function() {
				$(this).remove();
			});
			return false;
		});
		
	},
	confirm : function(mess, ok_function) {
		if ($('#flash').size() > 0) {
			return false;
		}
		
		$('body').append('<div id="flash_overlay"></div><div id="flash"><div><p>' + mess + '</p></div><button id="flash_ok_button">OK</button><button id="flash_cancel_button">Avbryt</button></div>');
		var top = parseInt((window.innerHeight-$('#flash').height())/2);
		
		$('#flash').hide().css({top : top+'px'}).fadeIn(function() {
			
		});
		$('#flash_ok_button, #flash_cancel_button').click(function() {
			if ($(this).attr('id') == 'flash_ok_button') {
				return ok_function();
			} else {
				$('#flash, #flash_overlay').fadeOut(function() {
					$(this).remove();
				});
			}
			return false;
		});
	},
	startLoading : function(mess) {
		$('body').append('<div id="flash_overlay"></div><div id="flash"><div><span id="loader"></span><p>' + mess + '</p></div></div>');
	},
	stopLoading : function() {
		$('#flash, #flash_overlay').fadeOut(function() {
			$(this).remove();
		});
	},
	overlay : function(a) {
		$('body').append('<div id="overlay"><a href="#" id="overlay_close">Stäng</a></div>');
		$('#overlay').hide().fadeIn(function() {
			$('body').append('<div id="full_foldman_holder"><img src="' + $(a).attr('data-url') + '" /></div>');
		});
		$('#overlay, #overlay_close').click(function() {
			$('#full_foldman_holder').remove();
			$('#overlay').fadeOut('medium', function() {
				$(this).remove();
			});
		});
	}
}

var Friends = {
	init : function() {
		$('#search_friends').keyup(function() {
			var match = $(this).val();
			if (match.length > 0) {
				var re = new RegExp(''+ match +'', "gi")
				$('#choose_friend_list li').each(function(i) {
					if ($('.name', this).text().match(re) == null) {
						$(this).slideUp();
					} else {
						$(this).show();
					}
				})
			} else {
				$('#choose_friend_list li').show();
			}
		});
		
		$('#notification input').change(function() {
			if ($(this).val() != 'none') {
				if ($(this).val() == 'wall') {
					var perms = 'offline_access,publish_stream';
				} else if ($(this).val() == 'email') {
					var perms = 'email';
				}
				checkHasPermission(perms);
			}
		});
	}
}

function init() {
	// Foldman.init();
	if (Modernizr.canvas) {
		Paint.init();
	}
	// UrlHandler.init();
	Friends.init();
	// UrlHandler.loadCurrentUrl();
	$.preloadImages('/images/layout/ajax-loader.gif');
}

$(document).ready(init);

