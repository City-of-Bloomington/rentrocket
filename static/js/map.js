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
