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
    
    $scope.deleteEntry = function ( entry ) {
        
        //Pop up a dialog confirming that the user wants to delete this entry
        bootbox.confirm("Are you sure you want to delete this entry?", function(result) {
            if ( result === true ){
                
                //Remove the entry from the entries array and call scope
                //$apply to force a angularJS refresh
                $scope.entries.splice( $.inArray( entry, $scope.entries), 1 );
                $scope.$apply();
            }
        }); 

    }
    
});
