/*
*2014.10.14 16:03:40 
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

//https://docs.djangoproject.com/en/dev/ref/csrf/
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  }
});
    

function appViewModel() {
  var self = this;
  
  self.other_company = ko.observable(false);
  self.other_company_name = ko.observable('');

  self.enable_units = ko.observable(false);
  //self.show_enabled_status = ko.computed(function() {

  /*
  self.enable_units.subscribe(function(new_value) {
    console.log('enable_units changed:', new_value);
  });
  */
    
  //self.utility = ko.observable();

  self._utility = ko.observable('');
  self.utility = ko.computed({
    read: function () {
      return self._utility();
    },
    write: function (value) {
      //save any changes first
      self.save_data();

      self._utility(value);
      //if we know a provider for this utility, set it automatically
      var provider_options = utility_providers[value];
      //console.log(provider_options);
      
      if (provider_options) {
        self._provider(provider_options[0]);
        //need to check this here too:
        if (self._provider() === "Other") {
          self.other_company(true);
        }
        else {
          self.other_company(false);
        }
      }

      //go ahead an look up new data
      self.update_data();
      
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
      //save any changes (if possible) first
      self.save_data();
      
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
        //go ahead an look up new data
        self.update_data();
      }

      if (value === "Other") {
        self.other_company(true);
      }
      else {
        self.other_company(false);
      }

      console.log(self.other_company());
        
    },
    owner: self
  });

  self.company_name = ko.computed(function() {
    if (self.other_company()) {
      return self.other_company_name();
    }
    else {
      return self.provider();
    }
  });
  
  //this is the format that a HTML5 date input requires:
  self.format = 'YYYY-MM-DD';
  var today = moment().format(self.format);
  //var today = moment(String);
  //console.log(today);
  self.end_date = ko.observable(today);
  self.start_date = ko.observable(moment().subtract(12, 'months').format(self.format));
  
  self.last_start = self.start_date();
  self.last_end = self.end_date();

  self.url = window.location.href.toString().split(window.location.host)[1];

  self.save_data = function(callback) {
    var url = self.url.replace(/edit?/g, "save");
    console.log(url);

    var cur_date;
    var cur_cost;
    var cur_amount;
    var cur_input_id;
    var cur_cost_id;
    var cur_amount_id;
    
    var cur_values = {};
    for (var i = 0; i < 12; i++) {
      cur_cost_id = '#id_months-' + i + '-cost';
      cur_amount_id = '#id_months-' + i + '-amount';
      cur_cost = $(cur_cost_id).val();
      cur_amount = $(cur_amount_id).val();
      if (cur_cost || cur_amount) {
        cur_input_id = '#id_months-' + i + '-start_date';
        cur_date = moment($(cur_input_id).val()).format(self.format);
        cur_values[cur_date] = { 'cost': parseFloat(cur_cost), 'amount': parseFloat(cur_amount) }
      }
    }
    
    $.ajax({
      url: url,
      type: 'POST',
      contentType: 'application/json; charset=utf-8',
      data: JSON.stringify({ 'utility': self.utility(),
              'other_company': self.other_company(),
              'company_name': self.company_name(),
              'values': cur_values
                           }),
      dataType: 'text',
      success: callback
    });
  };

  
  self.update_data = function() {
    //this could be called by update rows
    //or after a change in utility_type or utility_provider

    var url = self.url.replace(/edit?/g, "json");
    //console.log(url);

    $.ajax({
      url: url,
      type: 'POST',
      contentType: 'application/json; charset=utf-8',
      data: JSON.stringify({ 'utility': self.utility(),
              'other_company': self.other_company(),
              'company_name': self.company_name(),
              'start': self.start_date(),
              'end': self.end_date()
                           }),
      dataType: 'text',
      success: self.update_results
    });
  };

  self.update_results = function(result) {
    //console.log(result);
    result = JSON.parse(result);
    //console.log('update_data');
    //console.log(typeof result);
    
    if (result) {
      var cur_date;
      var cur_input_id;
      var cur_cost_id;
      var cur_amount_id;
      for (var i = 0; i < 12; i++) {
        cur_input_id = '#id_months-' + i + '-start_date';
        cur_date = moment($(cur_input_id).val()).format(self.format);
        cur_cost_id = '#id_months-' + i + '-cost';
        cur_amount_id = '#id_months-' + i + '-amount';
        
        //console.log(cur_date);
        //console.log(typeof cur_date);
        //console.log(typeof 'abc');
        if ( result.hasOwnProperty(cur_date) ) {
        //if ( hasOwnProperty(result, cur_date) ) {
        //if ( cur_date in result ) {

          //console.log('has key!');
          //console.log(result[cur_date]);
          $(cur_cost_id).val(result[cur_date]['cost']);
          $(cur_amount_id).val(result[cur_date]['amount']);
        }
        else {
          //otherwise we want to make sure it doesn't have data left over
          $(cur_cost_id).val('');
          $(cur_amount_id).val('');
          
        }
      }
    }
  };

  
  self.update_rows = function() {
      
    //should be triggered after update_range makes a change
    //since there are multiple places that could happen, abstracting
    var cur_moment = moment(self.start_date(), self.format);
    var cur_input_id = '';
    //var cur_input;
    for (var i = 0; i <= 12; i++) {
      cur_input_id = '#id_months-' + i + '-start_date';
      //cur_input = $(cur_input_id);
      $(cur_input_id).val(cur_moment.format('YYYY-MM-01'));
      //console.log($(cur_input_id).val());
      cur_moment.add(1, 'months')
    }

    //go ahead an look up new data
    self.update_data();
    
  };
  
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

      //self.update_rows();
      //save any changes (if possible) first
      self.save_data(self.update_rows);
      
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
      
      //self.update_rows();
      //save any changes (if possible) first
      self.save_data(self.update_rows);
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
