/*
**2014.10.14 16:03:40 
Description:
logic needed on generic utility form

*/

//http://stackoverflow.com/questions/12125143/giving-initial-value-to-observable-from-the-html-markup
//want to get the date that was sent with the form
ko.bindingHandlers.valueWithInit = {
    init: function(element, valueAccessor, allBindingsAccessor, data) {
        var property = valueAccessor(),
            value = element.value;

        //create the observable, if it doesn't exist 
        if (!ko.isWriteableObservable(data[property])) {
            data[property] = ko.observable();
        }

        data[property](value);

        ko.applyBindingsToNode(element, { value: data[property] });
    }
};

function appViewModel() {
  var self = this;
  
  self.other_company = ko.observable(false);
  
  //self.utility = ko.observable();

  self._utility = ko.observable('');
  self.utility = ko.computed({
    read: function () {
      return self._utility();
    },
    write: function (value) {
      self._utility(value);
      //if we know a provider for this utility, set it automatically
      var provider_options = utility_providers[value];
      //console.log(provider_options);
      
      if (provider_options) {
        self._provider(provider_options[0]);
      }
    },
    owner: self
  });
  
  // computed ...
  // when utility is changed:
  //  - automatically set the company, if we have it in a lookup
  //  - do an ajax request for any existing data in the currently set dates

  //self.provider = ko.observable();

  self._provider = ko.observable('');
  self.provider = ko.computed({
    read: function () {
      return self._provider();
    },
    write: function (value) {
      self._provider(value);
      //verify utility is set correctly:
      var utility_options = [];
      var cur_option;
      for (var key in utility_providers) { 
        cur_option = utility_providers[key][0];
        //console.log(cur_option)

        /*
        //just testing...
        if (cur_option === value) {
          console.log(cur_option, " matches value");
        }
        else {
          console.log(cur_option, " != ", value);
        }

        if (key in utility_options) {
          console.log(key, "is in", utility_options);
        }
        else {
          console.log(key, "not in", utility_options);
        }
        */
        
        if ( (cur_option === value) && !(key in utility_options) ) {
          utility_options.push(key);
        }
      }
      //console.log(utility_options);

      //Only want to change utility if provider is not set to "Other"
      if ( (utility_options) && (value !== "Other") ) {
        self._utility(utility_options[0]);
      }

      if (value === "Other") {
        self.other_company(true);
      }
      else {
        self.other_company(false);
      }
        
        
    },
    owner: self
  });

  //this is the format that a date input seems to require:
  self.format = 'YYYY-MM-DD';
  var today = moment().format(self.format);
  //var today = moment(String);
  console.log(today);
  self.end_date = ko.observable(today);
  self.start_date = ko.observable(moment().subtract(12, 'months').format(self.format));
  
  self.last_start = self.start_date();
  self.last_end = self.end_date();
  
  self.update_range = ko.computed(function() {
    var end_moment;
    var now_moment;
    var start_moment;
    var lowest;
    var alt;
    
    if (self.start_date() !== self.last_start) {
      //console.log(self.start_date(), self.last_start);
      //console.log("changed!");
      end_moment = moment(self.start_date(), self.format).add(1, 'year');
      now_moment = moment();
      //want to make sure we haven't gone past the present day
      if (end_moment.isAfter(now_moment)) {
        //lowest = moment.min(end_moment, now_moment);
        self.end_date(now_moment.format(self.format));
        self.start_date(now_moment.subtract(1, 'year').format(self.format));
      }
      else {
        //already updated start_date elsewhere:
        self.end_date(end_moment.format(self.format));
      }
      
      self.last_start = self.start_date();
      self.last_end = self.end_date();
      
    }

    if (self.end_date() !== self.last_end) {
      end_moment = moment(self.end_date(), self.format);
      now_moment = moment();
      //want to make sure we haven't gone past the present day
      if (end_moment.isAfter(now_moment)) {
        //lowest = moment.min(end_moment, now_moment);
        self.end_date(now_moment.format(self.format));
        self.start_date(now_moment.subtract(1, 'year').format(self.format));
      }
      else {
        start_moment = moment(self.end_date(), self.format).subtract(1, 'year');
        //already updated end_date elsewhere:
        self.start_date(start_moment.format(self.format));
      }
      self.last_start = self.start_date();
      self.last_end = self.end_date();
      
    }
  });

  /*
  // this does NOT work for dictionaries:
  for (var i = 1; i <= utility_providers.length; i++) { 
    cur_option = utility_providers[i];
    console.log(cur_option)
  }
  */

  
  
  //these are getting set above, so the dates can be passed in automatically
  //??? maybe easier just to set them here?
  //self.start_date = ko.observable();
  //self.end_date = ko.observable();
  
  /*
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
  
  */
  console.log("made it here");
};

//ko.applyBindings(new appViewModel());
//http://stackoverflow.com/questions/8649690/is-there-a-way-to-set-the-page-title-by-data-binding-using-knockout-js
//using this so page title can be bound as well:
ko.applyBindings(new appViewModel(), document.getElementById("htmlTop"));
