/*
*2014.01.22 13:19:50 
view model for building details page
*/

define(['jquery', 'lodash', 'ko'], function($, _, ko) {
    function appViewModel() {
	var self = this;

	self.viewing = ko.observable("street_view");

	self.editing_building = ko.observable(false);
	self.editing_unit = ko.observable(false);
	self.current_unit = ko.observable("");

	//console.log("made it here");

	self.view_map = function() {
	    self.viewing('map');
	    //console.log("viewing updated to: ", self.viewing());
	};

	self.view_street_view = function() {
	    self.viewing('street_view');
	    //console.log("viewing updated to: ", self.viewing());
	};

	self.view_photos = function() {
	    self.viewing('photos');
	    //console.log("viewing updated to: ", self.viewing());
	};

    };

    //ko.applyBindings(new appViewModel());
    //http://stackoverflow.com/questions/8649690/is-there-a-way-to-set-the-page-title-by-data-binding-using-knockout-js
    //using this so page title can be bound as well:
    ko.applyBindings(new appViewModel(), document.getElementById("htmlTop"));

});
