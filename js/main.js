var mainApp = angular.module('familyarchiveApp', ['firebase', 'ui.bootstrap','ngTagsInput']);

mainApp.run(function($rootScope) {
    $rootScope.attachmentServices = ["picasaweb","youtube"];
})

mainApp.directive('focusMe', function($timeout) {
    return {
        link: function(scope, element, attrs) {
            scope.$watch(attrs.focusMe, function(value) {
                if(value === true) {
                    console.log('value=',value);
                    $timeout(function() {
                        element[0].focus();
                        scope[attrs.focusMe] = false;
                    });
                }
            });
        }
    };
});