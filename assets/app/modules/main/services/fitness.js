"use strict";


//@todo Check it this belongs to this main modules
angular.module('app.main').factory('fitnessService', function ($http, $q) {

    var fitnessService = {};
    var weightMeasurements = {};


    fitnessService.getUserWeightMeasurements = function (userId) {
        var deffered = $q.defer();
        // Get some weight
        $http.get('/metrics/runkeeper/' + userId + '/weight')
            .success(function (data, status, headers, config) {
                debugger;
                if (status !== 200) {
                    deffered.resolve(data.status);
                    return;
                }

                var weight;
                var fatPercent;
                for (var weightMeasurement in data.items) {
                    if (!weight && data.items[weightMeasurement].weight) {
                        weight = data.items[weightMeasurement].weight;
                    }
                    if (!fatPercent && data.items[weightMeasurement].fat_percent) {
                        fatPercent = data.items[weightMeasurement].fat_percent;
                    }
                }
                weightMeasurements.weight = weight + 'Kg';
                weightMeasurements.fatPercent = fatPercent + '%';

                deffered.resolve(status);
            })
            .error(function (data, status, headers, config) {
                deffered.reject(status);
                console.log(data, status, headers, config);
            });
        return deffered.promise;
    };

    fitnessService.weightMeasurements = function(){
        return weightMeasurements;
    };

    return fitnessService;

});