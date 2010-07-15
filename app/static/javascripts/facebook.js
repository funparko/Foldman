function checkHasPermission(perms) {
	var user = FB.getSession();
	FB.api({
		'method': 'fql.query',
		'query' : 'SELECT ' + perms + ' FROM permissions WHERE uid = '+ user.uid
	}, function (result) {
		result = result[0];
		var perm = perms.split(",");
		var hasPermission = true;
		for (v in perm) {
			if (result[perm[v]] == "0") {
				hasPermission = false;
			}
		}	
		if (!hasPermission) {
			FB.login(function(response) {
				console.log(response);
			},
			{ perms: perms });
		};
	});
}

window.fbAsyncInit = function() {
	FB.init({appId: FACEBOOK_APP_ID, status: true, cookie: true, xfbml: true});
	FB.Event.subscribe('{% if current_user %}auth.logout{% else %}auth.login{% endif %}', function(response) {
		window.location.reload();
	});
	$('.login').bind('click', function() {
		// FB.login(handleSessionResponse, {});
		FB.login(handleSessionResponse, {perms: 'email,offline_access'});
	});

	$('#logout').bind('click', function() {
		FB.logout(function() {
			window.location.reload();
		});
	});
};
function handleSessionResponse(response) {
	if (response.session) {
		window.location.reload();
	}
}

function initFacebook() {
	var e = document.createElement('script');
	e.type = 'text/javascript';
	e.src = document.location.protocol + '//connect.facebook.net/sv_SE/all.js';
	e.async = true;
	document.getElementById('fb-root').appendChild(e);
}

$(document).ready(initFacebook);