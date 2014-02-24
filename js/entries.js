var entriesCtrl = mainApp.controller ( 'EntriesCtrl', function ( $scope, $http, $modal, entryProcessService ) {
    $scope.entries = [];
    
    $http.get ( 'entries.json' ).success( function ( data ) {
        $scope.entries = data;
        for ( var i = 0; i < $scope.entries.length; i++ ){
            entryProcessService.processEntry( $scope.entries [ i ] );
        }
    });
    
    $scope.addEntry = function ( ) {
        //Adds a new entry containing only the current date, adds it to the
        //entries list and processes it
        
        var date = new Date();
        var dateString = (date.getMonth() + 1) + "/" + date.getDate() + "/" + 
                         date.getFullYear();
        var entry = { date: dateString };
        $scope.entries.unshift ( entry );
        entryProcessService.processEntry( entry );
    }
  
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
        var confirmText = "Are you sure you want to delete the entry: '" +
                          entry.title + "'?"
        bootbox.confirm(confirmText, function(result) {
            if ( result === true ){
                
                //Remove the entry from the entries array and call scope
                //$apply to force a angularJS refresh
                $scope.entries.splice( $.inArray( entry, $scope.entries), 1 );
                $scope.$apply();
            }
        }); 

    }
    
});
