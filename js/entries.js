var entriesCtrl = mainApp.controller ( 'EntriesCtrl', function ( $scope, $http, $modal, $firebaseSimpleLogin, entryProcessService ) {
    $scope.entries = [];

    $http.get ( 'js/entries.json' ).success( function ( data ) {
        $scope.entries = data;
        for ( var i = 0; i < $scope.entries.length; i++ ){
            entryProcessService.processEntry( $scope.entries [ i ] );
        }
    });

    $scope.loginScreen = function(){
        var modalInstance = $modal.open({
            templateUrl: "views/modal-login.html",
            controller: function ($scope, $modalInstance, loginObj) {
                $scope.selectLoginService = function(service){
                    loginObj.$login(service, {
                        scope: 'email',
                        rememberMe: true
                    }).then(function(user) {
                        console.log('Logged in as: ', user.uid);
                        console.log(user);
                        $modalInstance.close();
                    }, function(error) {
                        console.error('Login failed: ', error);
                    });
                }
            },
            resolve: {
                loginObj: function () {
                    return $scope.loginObj;
                }
            }
        });
    }
    
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
    
    $scope.clickAddAttachment = function( entry ){
        var modalInstance = $modal.open({
            templateUrl: "views/modal-addattachment.html",
            controller: function ($scope, $compile, $timeout, $rootScope, $modalInstance) {

                $scope.tabs = $rootScope.attachmentServices;

                $timeout(function(){
                    $scope.currentTab = $scope.tabs[0];
                    for(var i = 0; i < $scope.tabs.length; i++){
                        var tabName = $scope.tabs[i];
                        var chart = angular.element(document.createElement(tabName + '-add-directive'));
                        var el = $compile( chart )( $scope );
                        angular.element( document.querySelector( '#inject-' + tabName )).append(chart);
                    }
                },0);

                $scope.selectTab = function(tabName){
                    $scope.currentTab = tabName;
                }

                $scope.addAttachment = function(attachment){
                    var attachmentArray = ["", attachment.url, $scope.currentTab];
                    entryProcessService.addAttachment(entry, attachmentArray);
                    $modalInstance.close();
                }

            }
        });
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

    var dataRef = new Firebase("https://familyarchive.firebaseio.com");
    $scope.loginObj = $firebaseSimpleLogin(dataRef);
    console.log($scope.loginObj.user);
    if(!$scope.loginObj.user){
        $scope.loginScreen();
        /*
         $scope.loginObj.$login('google', {
         scope: 'email'
         }).then(function(user) {
         console.log('Logged in as: ', user.uid);
         console.log(user);
         }, function(error) {
         console.error('Login failed: ', error);
         });
         */
    }
    
});
