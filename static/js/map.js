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
	    //remove old markers from the map:
	    for (var i = 0, len = self.markers.length; i < len; i++) {
		marker = self.markers[i];
		marker.setMap(null);
	    }
	    //clear the array:
	    //http://stackoverflow.com/questions/1232040/how-to-empty-an-array-in-javascript
	    self.markers.length = 0;

	    //add the new markers to the map
	    for (var i = 0, len = result['buildings'].length; i < len; i++) {
		building = result['buildings'][i];
		//console.log(building)
		marker = new google.maps.Marker({
		    position: new google.maps.LatLng(building.lat, building.lng),		    
		    map: self.map,
		    title: building.address
		});
		var image;
		if (building.score > 500) {
		    image = '/static/img/marker-green.png';
		}
		else if (building.score > 250) {
		    image = '/static/img/marker-yellow.png';
		}
		else if (building.score > 50) {
		    image = '/static/img/marker-orange.png';
		}
		else if (building.score > .0001) {
		    image = '/static/img/marker-red.png';
		}
		else if (building.score == .0001) {
		    image = '/static/img/marker-dark_gray.png';
		}
		else if (building.score == 0) {
		    image = '/static/img/marker-light_gray.png';
		}
		else {
		    //shouldn't get this, but... 
		    image = '/static/img/marker-light_gray.png';
		}

		var icon = {
		    url: image, 
		    // This marker is 20 pixels wide by 32 pixels tall.
		    //size: new google.maps.Size(20, 32),
		    scaledSize: new google.maps.Size(23, 40),
		    
		    // The origin for this image is 0,0.
		    //origin: new google.maps.Point(0,10),
		    // The anchor for this image is the base of the flagpole at 0,32.
		    anchor: new google.maps.Point(0, 12)
		};

		marker.setIcon(icon);

		//not sure if this is the best place to generate the view
		//self.pop_up_content = 
		//could pass it in as part of json request
		//
		// building is a json object 
		// that gets returned by the ajax request above
		// it is generated in building.models.Building.to_dict()
		// and collected in building.views.lookup()

		//self.update_info(building.address, marker)
		self.update_info(building.profile, marker)
		self.markers.push(marker)
	    }

	    
	    /*
	    if( console && console.log ) {
		console.log("Sample of data:", result);
	    }
	    */
	    
	});
	//alert(bounds);
    }

    //http://stackoverflow.com/questions/11467070/how-to-set-a-popup-on-markers-with-google-maps-api
    //https://developers.google.com/maps/documentation/javascript/overlays#InfoWindows

    //update_info gets called during showMarkers() function above:
    self.update_info = function (content, marker) {
	google.maps.event.addListener(marker, 'click', function() {
	    self.infowindow.setContent(content);
	    infowindow.open(map, marker);
	});
    }

    self.initialize = function () {
	var mapOptions = {
            center: new google.maps.LatLng(self.lat, self.lng),
            zoom: zoom,
            mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	self.map = new google.maps.Map(document.getElementById("map-canvas"),
				  mapOptions);
	
	self.map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(
	    document.getElementById('legend'));

	self.infowindow = new google.maps.InfoWindow();
	//doesn't seem to have an effect:
	//self.infowindow.setOptions({maxWidth:600});

	google.maps.event.addListener(self.map, 'idle', self.showMarkers);
        
    }
    return(self);
}
