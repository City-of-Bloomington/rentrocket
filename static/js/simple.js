/*
*2014.08.28 16:23:18 
Description:
Simple javascript helper to only show rent amount when rent selected

*/

//define(['jquery', 'lodash', 'ko'], function($, _, ko) {
  function appViewModel() {
    var self = this;
    
    self.property_type = ko.observable();
    
    self.show_rent = ko.computed(function() {
      if (self.property_type() === "rental") {
	return true;
      }
      else {
	return false;
      }	    
    });	
    
    //console.log(self.show_rent());
    //console.log(self.property_type());
    //console.log("made it here");
  };
  
  //ko.applyBindings(new appViewModel());
  //http://stackoverflow.com/questions/8649690/is-there-a-way-to-set-the-page-title-by-data-binding-using-knockout-js
  //using this so page title can be bound as well:
  ko.applyBindings(new appViewModel(), document.getElementById("htmlTop"));
  
//});
