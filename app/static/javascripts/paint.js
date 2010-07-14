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
			if ($('#cancel_image').val() == '1') {
				return true;
			}
			
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
	},
	cancelPaint : function() {
		clearInterval(Paint.active_interval);
		$('#cancel_image').val('1');
		$('#part_form').submit();
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
		clearInterval(Paint.active_interval);
		$.post($('#part_form').attr('action'), data, function(resp) {
			if (resp != 'error') {

       		}
			UI.stopLoading();
		});
	}
}
