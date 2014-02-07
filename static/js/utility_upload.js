/*
*2014.02.06 15:55:22 
Description:
Simple javascript helper to customize utility upload form behavior

*/

define(['jquery', 'lodash', 'ko'], function($, _, ko) {
    function appViewModel() {
	var self = this;

	self.utility = ko.observable();

	self.show_alts = ko.computed(function() {
	    if (self.utility() === "other") {
		return true;
	    }
	    else {
		return false;
	    }	    
	});	

	self.energy_upload = ko.computed(function() {
	    if (self.utility() === "electricity" || self.utility() === "gas" || self.utility() === "oil") {
		return true;
	    }
	    else {
		return false;
	    }	    
	});	

	
	console.log("made it here");
    };

    //ko.applyBindings(new appViewModel());
    //http://stackoverflow.com/questions/8649690/is-there-a-way-to-set-the-page-title-by-data-binding-using-knockout-js
    //using this so page title can be bound as well:
    ko.applyBindings(new appViewModel(), document.getElementById("htmlTop"));

});
