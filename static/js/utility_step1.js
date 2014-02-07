/*
*2014.01.31 09:45:26 
Description:
Simple javascript helper to only show alt city when "Other" is selected

*/

define(['jquery', 'lodash', 'ko'], function($, _, ko) {
    function appViewModel() {
	var self = this;

	self.city = ko.observable();

	self.show_alts = ko.computed(function() {
	    if (self.city() === "other") {
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
