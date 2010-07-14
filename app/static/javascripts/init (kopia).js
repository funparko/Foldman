
var tools = {};
tools.pencil = function () {
	var tool = this;
	this.started = false;
	this.size = 2;

	// This is called when you start holding down the mouse button.
	// This starts the pencil drawing.
	this.mousedown = function (ev) {
		Paint.context.beginPath();
		Paint.context.lineWidth = tool.size;
		Paint.context.lineJoin = 'round';
		Paint.context.lineCap = 'round';
		Paint.context.moveTo(ev._x, ev._y);
		tool.started = true;
		return false;
	};

	// This function is called every time you move the mouse. Obviously, it only 
	// draws if the tool.started state is set to true (when you are holding down 
	// the mouse button).
	this.mousemove = function (ev) {
		if (tool.started) {
			Paint.context.lineTo(ev._x, ev._y);
			Paint.context.stroke();
			return false;
		}
	};

	// This is called when you release the mouse button.
	this.mouseup = function (ev) {
		if (tool.started) {
			tool.mousemove(ev);
			tool.started = false;
			Paint.canvasUpdate();
		}
	};
	this.mouseout = function (ev) {
		tool.mouseup(ev);
	};
	
};
tools.eraser = function () {
	this.started = false;
	this.size = 2;
	var tool = this;
		
	this.mousedown = function (ev) {
		// console.log('tool.size: ' + tool.size);
		// Paint.context_main.clearRect(ev._x, ev._y,tool.size,tool.size);
		Paint.context_main.clearRect(ev._x-(tool.size/2), ev._y-(tool.size/2),tool.size,tool.size);
		tool.started = true;
		return false;
	};
	this.mousemove = function (ev) {
		if (tool.started) {
			// Paint.context_main.clearRect(ev._x, ev._y,tool.size,tool.size);
			Paint.context_main.clearRect(ev._x-(tool.size/2), ev._y-(tool.size/2),tool.size,tool.size);
			return false;
		}
	};
	this.mouseup = function (ev) {
		if (tool.started) {
			tool.mousemove(ev);
			tool.started = false;
			Paint.canvasUpdate();
		}
	};
	this.mouseout = function (ev) {
		tool.mouseup(ev);
	};
};


var Paint = {
	canvas_main : null,
	context_main : null,
	canvas : null,
	context : null,
	width : 500,
	height : 250,
	tool_default : 'pencil',
	tool : null,
	tool_name : null,
	tools : tools,
	tool_size : 16,
	active_interval : null,
	
	init : function() {
		if($('#paint_area').size() == 0) return;
		Paint.canvas_main = document.getElementById('paint_area');
		if (!Paint.canvas_main) {
			alert('Error: Cannot find the canvas element!');
			return;
		}
		if (!Paint.canvas_main.getContext) {
			alert('Error: no canvas.getContext!');
			return;
		}
		Paint.context_main = Paint.canvas_main.getContext('2d');
		
		if (!Paint.context_main) {
			alert('Error: failed to getContext!');
			return;
		}
		
		var container = Paint.canvas_main.parentNode;
		Paint.canvas = document.createElement('canvas');
		if (!Paint.canvas) {
			alert('Error: I cannot create a new canvas element!');
			return;
		}

		Paint.canvas.id     = 'paint_area_temp';
		Paint.canvas.width  = Paint.canvas_main.width;
		Paint.canvas.height = Paint.canvas_main.height;
		container.appendChild(Paint.canvas);
		
		Paint.context = Paint.canvas.getContext('2d');
		
		if ($('#previous_image').size()) {
			var image = new Image();
			image.onload = function(){  
				Paint.context_main.drawImage(image,0,-240);
			  	Paint.canvasUpdate();
			}
			image.src = $('#previous_image').val();			
		}
		
		Paint.canvas.addEventListener('mouseout', Paint.eventPaint, false);
		Paint.canvas.addEventListener('mousedown', Paint.eventPaint, false);
		Paint.canvas.addEventListener('mousemove', Paint.eventPaint, false);
		Paint.canvas.addEventListener('mouseup',   Paint.eventPaint, false);
		Paint.canvas.addEventListener('mouseover', Paint.setCursor, false);
		Paint.canvas.addEventListener('mousedown', Paint.setCursor, false);
		Paint.canvas.addEventListener('mouseup',   Paint.setCursor, false);
		
		$('#done_button').click(function() {
			// Paint.savePaint();
			// return false;
		});			
		$('#cancel_button').click(function() {
			Paint.cancel();
			return false;
		});	
		
		Paint.active_interval = setInterval("Paint.sendActive()", 60000 );
		
		$('ul#tool_type li').click(function() {
			$('ul#tool_type li.selected').removeClass('selected');
			$(this).addClass('selected');
			Paint.changeTool($(this).attr('rel'));
			return false;
		});		
		$('#tool_size li').click(function() {
			$('ul#tool_size li.selected').removeClass('selected');
			$(this).addClass('selected');
			Paint.changeToolSize($(this).attr('rel'));
			return false;
		});
		$('ul#tool_size li.tool_size_' + Paint.tool_size).addClass('selected');

		if (Paint.tools[Paint.tool_default]) {
			Paint.tool_name = Paint.tool_default;
			Paint.tool = new tools[Paint.tool_default]();
			Paint.tool.size = Paint.tool_size;
			$('ul#tool_type li.tool_' + Paint.tool_default).addClass('selected');
		}
		
		$('#part_form').submit(function() {

			if($('#part_type').val()  != 'legs') {
				if (!Paint.checkImageForNextPainter()) {
					UI.flash('<strong>Rita ända ner till kanten</strong><br/> Nästa person som ska rita måste kunna se var man fortsätter', 'error');
					return false;
				}
			}
			UI.startLoading('Spara..');
			$('#part_image').val(Paint.canvas_main.toDataURL());
			return true;
		});
		
		UrlHandler.setStopLoad(Paint.cancel);
	},
	cancelPaint : function() {
		$.post("/foldman/cancel/" + $('#part_id').val());
		clearInterval(Paint.active_interval);
		UrlHandler.stopLoad = null;
		UrlHandler.load(UrlHandler.url);
		// Foldman.updateIndex();
	},
	cancel : function() {
		var ok_function = Paint.cancelPaint;
		UI.confirm('<strong>Är du säker du vill avbryta?</strong><br/>Det du ritat kommer inte att sparas.', ok_function);
	},
	setCursor : function(e) {
		$('#paint_area').attr('class', '');
		$('#paint_area_temp').attr('class', '');
		$('#paint_area_container').attr('class', '');
		// console.log('cursor_' + Paint.tool_name);
		$('#paint_area').addClass('cursor_' + Paint.tool_name);
		$('#paint_area_temp').addClass('cursor_' + Paint.tool_name);
		$('#paint_area_container').addClass('cursor_' + Paint.tool_name);
		
		// this.style.cursor="crosshair";
		e.preventDefault();
		return false;
	},
	eventPaint : function (ev) {
		if (ev.layerX || ev.layerX == 0) { // Firefox
			ev._x = ev.layerX;
			ev._y = ev.layerY;
		} else if (ev.offsetX || ev.offsetX == 0) { // Opera
			ev._x = ev.offsetX;
			ev._y = ev.offsetY;
		}
		// Call the event handler of the tool.
		var func = Paint.tool[ev.type];

		if (func) {
			func(ev);
		}
	},
	canvasUpdate : function() {
		Paint.context_main.drawImage(Paint.canvas, 0, 0);
		Paint.context.clearRect(0, 0, Paint.canvas.width, Paint.canvas.height);
	},	
	changeTool : function(tool) {
		if (Paint.tools[tool]) {
			Paint.tool_name = tool;
			Paint.tool = new tools[tool]();
			Paint.changeToolSize($('ul#tool_size li.selected').attr('rel'));
		}
	},		
	changeToolSize : function(size) {
		Paint.tool.size = parseInt(size);
	},		
	sendActive : function() {
		if ($('#part_id').val() == undefined) {
			clearInterval(Paint.active_interval);
		} else {
			$.post("/foldman/active/" + $('#part_id').val());
		}
		
	},		
	checkImageForNextPainter : function() {
		var imageData = Paint.context_main.getImageData(0, Paint.height-10, Paint.width, 10);
		var visiblePixels = 0;
		var h = imageData.height;
		var w = imageData.width;
		// console.log(h + "x" + w);
		for (j=0; j<h; j++) {
		    for (i=0; i<w; i++) {
				var index=(i*4)+(j*4);
				var red=imageData.data[index];	  
				var green=imageData.data[index+1];
				var blue=imageData.data[index+2];	  
				var alpha=imageData.data[index+3];
				if (alpha > 100 ) {
					visiblePixels++;
				}
			}
		}
		if(visiblePixels > 10) {
			return true;
		} else {
			return false;
		}
	},	
	savePaint : function() {
		
		if($('#part_type').val()  != 'legs') {
			if (!Paint.checkImageForNextPainter()) {
				UI.flash('<strong>Rita ända ner till kanten</strong><br/> Nästa person som ska rita måste kunna se var man fortsätter', 'error');
				return false;
			}
		}
		UI.startLoading('Spara..');
		var data = {
			u : Paint.canvas_main.toDataURL(), 
			type : $('#part_type').val(),
			part_id : $('#part_id').val()
		}
		
		$('#part_image').val(Paint.canvas_main.toDataURL());
		return true;
		// console.log(localStorage);
		// console.log(localStorage.getItem('user_id'));
		// if (localStorage != null && localStorage.getItem('user_id') != null) {
		// 	data.user_id = localStorage.getItem('user_id');
		// }
		clearInterval(Paint.active_interval);
		$.post($('#part_form').attr('action'), data, function(resp) {
			if (resp != 'error') {

       		}
			UI.stopLoading();
			UrlHandler.stopLoad = null;
			// Foldman.updateYour();
			// Foldman.updateFinished();
			// Foldman.updateIndex();
			UrlHandler.load(resp)
		});
	}
}

var UrlHandler = {
	stopLoad : null,
	url : null,
	loadCurrentUrl : function() {
		var url = location.href.split('#');
		if (url[1]) {
			UrlHandler.load(url[1], '');
		}
	},
	setStopLoad : function(f) {
		UrlHandler.stopLoad = f;
	},
	load : function(url, section) {
		// console.log(url);
		UrlHandler.url = url;
		// console.log(UrlHandler.beforeLoad);
		if (UrlHandler.stopLoad) {
			UrlHandler.stopLoad();
			return false;
		}
		section = section ? '#' + section : '#area';
		// console.log(section);
		// console.log('URL' + url);
		$(section).fadeOut('fast');
		$(section).load(url+'?ajax=1', function(responseText, textStatus) {
			$(section).hide();
			var height = $(section).height();
			$(section).parent().animate({height:height}, function() {
				$(section).fadeIn('fast');
				// console.log(textStatus);
				if (textStatus == 'error'){
					// console.log(responseText);
					UI.flash(responseText, 'error');
					UrlHandler.load('/');
					return;
				} else {
					location.href = '/#' + url;
					Paint.init();
					UrlHandler.init(section);
					Foldman.stopUpdateIndex();
				}
			});
		});
	},
	init : function(id) {
		// console.log(id);
		$((id ? id + ' ': '') + 'a').each(function(i) { 
			if ($(this).attr('rel') != 'no_ajax') {
				var href = $(this).attr('href');
				if (href) {
					href = href.split('#');			
					$(this).click(function() {
						var href = $(this).attr('href');
						var url = href.split('#');
						if (url[1]) {
							UrlHandler.load(url[1], $(this).attr('rel'));
						} else {
							UrlHandler.load(url[0], $(this).attr('rel'));
							return false;
						}
					});
				}
			}
		});
		
		var height = $('#area').height();
		$('#area_holder').parent().animate({height:height}, function() {});
		
	}
}

var Foldman = {
	updaterIndex : null,
	user_id : null,
	
	init : function() {
		// Foldman.getUser();
		// Foldman.updateYour();
		// var updaterIndex = setInterval('Foldman.updateIndex()', 1000);
		// Foldman.updateFinished();
		// setInterval('Foldman.updateFinished()', 60000);
		// setInterval('Foldman.updateChoose()', 5000);
	},	
	updateFinished : function() {
		return;
		$('#finished').load('/foldmen/finished', {}, function() {
			$(this).find('a img').click(function() {
				UI.overlay(this);
			});
			$('.show_all').click(function() {
				UrlHandler.load($(this).attr('href'));
				return false;
			});
			// UrlHandler.init('finished');
		})
	},		
	updateChoose : function() {
		
		if ($('#choose').size() > 0) {
			$.get("/json/choose", function(data){
				var choose = eval(data);
				var exist = false;
				var blocked = [];
				$('#choose_list li').each(function() {
					var should_block = true;
					for(x in choose) {
						if ($(this).attr('id') == 'f_'+ choose[x].id) {
							should_block=false;
							break;
						}
					}
					if (should_block) {
						blocked.push($(this).attr('id'))
					}
					
				});
				var add = new Array()
				for(z in choose) {
					if ($('#f_'+ choose[z].id).size() == 0) {
						add.push(choose[z])
					}
				}
				for (y in blocked) {
					$('#'+blocked[y]).animate({width:0},'slow', function() {
						$(this).remove();
						var c = add.shift()
						if (c) {
							var id = 'f_' + c.id;
							$('#choose_list').append('<li class="part_' + c.parts_finished + '" id="'+ id +'"><a href="#/canvas/' + c.id +'"></a></li>');
							$('#'+id).hide().fadeIn();
						}
					});
				}
			});
		}
	},	
	updateYour : function() {
		$('#num_of_user_foldmen').load('/home/foldmen_count');
	},	
	updateIndex : function() {
		UrlHandler.load('/');
	},	
	stopUpdateIndex : function() {
		clearInterval(Foldman.updaterIndex);
	}
};

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
			$('#flash, #flash_overlay').fadeOut(function() {
				$(this).remove();
			});
			if ($(this).attr('id') == 'flash_ok_button') {
				return ok_function();
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
						$(this).hide();
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
		})
	}
}

function init() {
	Foldman.init();
	if (Modernizr.canvas) {
		Paint.init();
	}
	// UrlHandler.init();
	Friends.init();
	// UrlHandler.loadCurrentUrl();
}

$(document).ready(init);

