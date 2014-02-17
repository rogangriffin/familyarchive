var entriesCtrl = mainApp.controller ( 'EntriesCtrl', function ( $scope, $http, entryProcessService ) {
    $scope.entries = [];
    
    $http.get ( 'entries.json' ).success( function ( data ) {
        $scope.entries = data;
        for ( var i = 0; i < $scope.entries.length; i++ ){
            entryProcessService.processEntry( $scope.entries [ i ] );
        }
  });
});
