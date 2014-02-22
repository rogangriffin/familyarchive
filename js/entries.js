var entriesCtrl = mainApp.controller ( 'EntriesCtrl', function ( $scope, $http, $modal, entryProcessService ) {
    $scope.entries = [];
    
    $http.get ( 'entries.json' ).success( function ( data ) {
        $scope.entries = data;
        for ( var i = 0; i < $scope.entries.length; i++ ){
            entryProcessService.processEntry( $scope.entries [ i ] );
        }
    });
  
    $scope.clickImage = function ( image ) {
        //Modal dialog that pops up when the user clicks an attachment thumbnail.
        //We get the html template from the attachment service
        var modalInstance = $modal.open({
            templateUrl: image.service.getModalHTMLTemplate(),
            controller: function ($scope, $modalInstance, image) {
                $scope.image = image;
                $scope.ok = function () {
                    $modalInstance.close();
                };
            },
            windowClass: 'modal-image',
            resolve: {
                image: function () {
                    return image;
                }
            }
        });
    }
    
});
