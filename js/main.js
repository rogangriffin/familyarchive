var mainApp = angular.module('familyarchiveApp', ['firebase', 'ui.bootstrap','ngTagsInput']);

mainApp.run(function($rootScope) {
    $rootScope.attachmentServices = [];
})
