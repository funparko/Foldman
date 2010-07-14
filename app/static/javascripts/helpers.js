Array.prototype.remove = function(from, to) {
	var rest = this.slice((to || from) + 1 || this.length);
	this.length = from < 0 ? this.length + from : from;
	return this.push.apply(this, rest);
};

jQuery.preloadImages = function() {
	for(var i = 0; i<arguments.length; i++) {
		jQuery("<img>").attr("src", arguments[i]);
	}
}