/*
[date]
Description:

*/

define(['jquery', 'lodash', 'ko'], function($, _, ko) {
    function appViewModel() {
	var self = this;

	self.loaded = ko.observable("");
	console.log("made it here");
    };

    //ko.applyBindings(new appViewModel());
    //http://stackoverflow.com/questions/8649690/is-there-a-way-to-set-the-page-title-by-data-binding-using-knockout-js
    //using this so page title can be bound as well:
    ko.applyBindings(new appViewModel(), document.getElementById("htmlTop"));

});
