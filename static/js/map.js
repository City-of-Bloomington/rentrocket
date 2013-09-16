var RRMap = function(args) { 
    var self = this;

    self.zoom = 14;
    self.lat = 18.427288;
    self.lng = -64.446392;
    self.map;

    self.markers = [];

    self.showMarkers = function () {
	var bounds = self.map.getBounds();
	var sw = bounds.getSouthWest();
	var ne = bounds.getNorthEast();
	$.ajax({
	    url: "/building/in/" + 
		sw.lat() + "/" + sw.lng() + "/and/" +
		ne.lat() + "/" + ne.lng() 
	}).done(function ( result ) {
	    var marker;
	    var building; 
	    for (var i = 0, len = self.markers.length; i < len; i++) {
		marker = self.markers[i];
		marker.setMap(null);
	    }
	    //clear the array:
	    //http://stackoverflow.com/questions/1232040/how-to-empty-an-array-in-javascript
	    self.markers.length = 0;
	    for (var i = 0, len = result['buildings'].length; i < len; i++) {
		building = result['buildings'][i];
		//console.log(building)
		marker = new google.maps.Marker({
		    position: new google.maps.LatLng(building.lat, building.lng),
		    
		      icon: {
			//path: "M 100 100 L 300 100 L 200 300 z",
			//path: 'M 100 0 L 0 0 L 0 100 L 35 100 L 50 120 L 65 100 L 100 100 Z',

			path: "m 10.810585,0.2 c -3.154567,0.017 -5.9630316,3.0545 -5.5882546,6.2195 0.1035128,2.0729 1.28101,3.851 2.467512,5.4724 2.0433498,3.1529 3.0127996,6.442 3.3060406,9.8954 0.329757,-3.3768 1.167804,-6.8182 3.134746,-9.6359 1.164875,-1.6442 2.432417,-3.3637 2.616329,-5.4406 0.377815,-2.3259 -0.943925,-4.7036 -2.984497,-5.8083 -0.896011,-0.5107 -1.923465,-0.7461 -2.951876,-0.7025 z",

			fillColor: "black",
			fillOpacity: .7,
			strokeColor: 'black',
			strokeWeight: 1,
			origin: new google.maps.Point(0, 0),
			anchor: new google.maps.Point(17, 17),
			scale: 2,
			},

		    map: self.map,
		    title: building.address
		});
		self.markers.push(marker)
	    }

	    
	    if( console && console.log ) {
		console.log("Sample of data:", result);
	    }
	    
	});
	//alert(bounds);
    }

    self.initialize = function () {
	var mapOptions = {
            center: new google.maps.LatLng(self.lat, self.lng),
            zoom: zoom,
            mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	self.map = new google.maps.Map(document.getElementById("map-canvas"),
				  mapOptions);
	
	google.maps.event.addListener(self.map, 'idle', self.showMarkers);
        
    }
    return(self);
}
