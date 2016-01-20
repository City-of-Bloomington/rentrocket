/*!
 * enerscore-basic 0.0.1
 * Prez Cannady, http://www.enerscore.com
 * License: AGPL
 */

(function() {

    'use strict';

    angular
        .module('enerscore.services.search.rentrocket.EnerscorePropertySearch', [])
        .factory('EnerscorePropertySearch', EnerscorePropertySearch)
    
    angular
        .module('enerscore.controllers.rentrocket.EnerscoreCtrl', [ 
            'ngResource',
            'enerscore.services.search.rentrocket.EnerscorePropertySearch',
        ])
        .controller('EnerscoreCtrl', EnerscoreCtrl)
        
    angular
        .module('enerscore.directive.enerscoreRentrocket', [
            'enerscore.controllers.rentrocket.EnerscoreCtrl',
        ])
        .directive('enerscoreRentrocket', enerscoreDirectiveRentRocket);

    angular.module('rentrocketApp', [ 
                // Directives
                'enerscore.directive.enerscoreRentrocket',
            ]);

    function EnerscoreCtrl($scope, EnerscorePropertySearch) {
        
        var address = $scope.address;
        var city = $scope.city;
        var state = $scope.state;
        var zip = $scope.zip;

        var formattedAddress = address + ' ' + city + ', ' + state + ' ' + zip;
        console.log(formattedAddress);

        $scope.query = 'http://map-alpha.enerscore.com/#/map?q=' + encodeURI(formattedAddress);
        $scope.placeholder = null;

        var onSuccess = function(properties) {
            if (properties.length < 1) {
                return;
            }

            console.log(properties);
            $scope.property = properties[0];
            $scope.propertyJson = JSON.stringify($scope.property, undefined, 4);

            $scope.totalColor = "{color: 'red'}";
            
            console.log($scope.query);

        };

        var onError = function(err) {

            console.log(err);

            $scope.property = null;
            $scope.placeholder = 'unavailable';
            
        };

        EnerscorePropertySearch.search({
            address: formattedAddress
        }).$promise.then(onSuccess, onError);

    }

    function link($scope, element, attrs) {

        



    }

    function enerscoreDirectiveRentRocket() {

        return {
            restrict: 'A',
            templateUrl: '/static/js/vendor/enerscore/enerscore.tpl.html',
            scope: {
                property: '=',
                query: '=',
                placeholder: '=',
            },
            link: link

        };
    }

    function EnerscorePropertySearch($q, $resource) {

        var baseUrl = 'http://api-alpha.enerscore.com/api/address/neighbors/:address';

        var resource = $resource(
            baseUrl, {
                citystatezip: '@citystatezip',
                address: '@address'
            }, {
                'search': {
                    method: 'GET',
                    isArray: true,
                    timeout: 30000,
                    transformResponse: function(data) {

                        try {
                            var properties = JSON.parse(data);
                            return properties;
                        } catch (error) {
                            return [];
                        }


                    }
                }
            });

        resource.prototype.year = function() {
            var self = this;

            return (self.yearUpdated) ? self.yearUpdated : self.yearBuilt;
        };

        resource.prototype.area = function() {
            var self = this;

            // var area = (self.livingSize) ? self.livingSize : 0;
            return self.livingSize + ' sq ft';
        };

        resource.prototype.formatted_address = function() {
            var self = this;

            return formattedAddress(self);
        };

        resource.prototype.cost = function() {
            var self = this;

            return formattedCurrency(self.energyCost, 'USD');
        };

        resource.prototype.electrical = function() {
            var self = this;

            return formattedValue(self.electricBaseloadTotal, self.electricBaseloadTotalType.energyTypeCode);
        };

        resource.prototype.heating = function() {
            var self = this;

            return formattedValue(self.heatingUsage, self.heatingUsageType.energyTypeCode);
        };

        resource.prototype.cooling = function() {
            var self = this;

            var units = (self.coolingUsageType) ? self.coolingUsageType.energyTypeCode : '';
            return formattedValue(self.coolingUsage, units);
        };


        resource.prototype.water = function() {
            var self = this;

            return formattedValue(self.domesticHotWaterTotal, self.domesticHotWaterTotalType.energyTypeCode);
        };


        resource.prototype.usage = function() {
            var self = this;
            return usage(self.year(), self.area());

        };

        resource.prototype.score = function() {
            var self = this;
            if (!self.energyScore)  {
                return 'U';
            }
            return self.energyScore.energyScore;
        }

        

        return resource;

    }

    function formattedValue(value, units) {

        if (!value) {
            return '0 ' + units;
        }

        return value.toFixed(0) + ' ' + units;
    }

    function formattedCurrency(value, units) {

        if (!units) {

        }

        if (!value) {
            return '$0.00';
        }

        return '$' + value.toFixed(2);
    }


    function formattedAddress(address) {
        return address.address1 + ', ' + address.addressTown + ', ' + address.addressState + ' ' + address.addressPostalCode;
    }

    

}())
