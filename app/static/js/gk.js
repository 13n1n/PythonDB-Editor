var w = 17, h = 7;
var list = [[0, 0], [0, 1], [1, 0], [0, -1], [-1, 0], [1, 1], [-1, -1], [-1, 1], [1, -1], [0, 2], [2, 0], [0, -2], [-2, 0]];

var result = [];

var remove = 1;

function intersect(arr1, arr2){
	return arr1.filter(function(n){
		return arr2.indexOf(n) != -1;
	});
}

function cut(x, y){
	return "background-position: " + x + "px " + y + "px";
}

function select(x, y){
	if (remove == 1) {
		$("body").children().each(function () {
			$(this).removeClass("border");
		});
	}
	$.each(list, function(i, v){
		$("#"+ (x+v[0]) +"x"+ (y+v[1])).addClass("border");
	});
}

function toggle(x, y){
	remove = (remove+1) % 2;
}

function rand(min, max){
	return Math.floor(Math.random() * (max - min) + min);
}

function position(x, y){
	return "top:" + 66*y + "px;left:" + (66*x + 140) + "px";
}

function shuffle(o){
	for(var i = 0; i < 1000; i++){
		var x1 = rand(0, w), y1 = rand(0, h),
			x2 = rand(0, w), y2 = rand(0, h);
			
		var t = o[x1][y1];
		o[x1][y1] = o[x2][y2];
		o[x2][y2] = t;
	}
	return o;
}

var coord = [];

function graphickey(suffl) {
	for(var x = 0; x < w; x++) {
		coord.push([]);
		for(var y = 0; y < h; y++) {
			coord[coord.length-1].push([x, y]);
		}
	}
	
	if(suffl) shuffle(coord);
	
	for(var y = 0; y < h; y++) {
		for(var x = 0; x < w; x++) {
			var _x = x, _y = y;
			var some = $('<div/>', {
				class: "node",
				style: cut(x*60, y*60) + ";" + position(coord[x][y][0],coord[x][y][1]),
				id: coord[x][y].join("x"),
				name: x + "x" + y,
				onmousemove: "select("+coord[x][y].join() + ")",
			}).mousedown(function(){
				console.log("FUCK U, MOTHERFUCKER!");
				toggle();
			}).mouseup(function(){
				console.log("JUST FUCK URSELF!");
				toggle();
				process(coord[_x][_y][0], coord[_x][_y][1]);
			});
			
			some.appendTo("body");
		}
	}
}