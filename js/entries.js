var entriesCtrl = mainApp.controller ( 'EntriesCtrl', function ( $scope, $http, $modal, $timeout, $firebaseSimpleLogin, entryProcessService ) {
    $scope.entries = [];
    $scope.entryProcessService = entryProcessService;
    $scope.hasLoggedIn = false;

    $scope.getEntries = function(){
        $http({method: 'POST', url: '/entries', params: {userid: $scope.loginObj.user.uid}}).success( function ( data ) {
            $scope.entries = data;
            for ( var i = 0; i < $scope.entries.length; i++ ){
                entryProcessService.processEntry( $scope.entries [ i ] );
            }
        }).error(function(data, status, headers, config){
            if(status==501){
                $("#main-container").text("Sorry, your account doesn't exist. Email rogangriffin@gmail.com for an invitation.");
            }
        });
    };

    $scope.loggedIn = function(){
        $scope.hasLoggedIn = true;
        console.log('Logged in as: ', $scope.loginObj.user.uid);
        console.log($scope.loginObj.user.email);

        if(getParameterByName("invite")){

            $http({method: 'GET', url: '/signup', params: {userid: $scope.loginObj.user.uid, email: $scope.loginObj.user.email, invite: getParameterByName("invite")}}).
                success(function(data) {
                    $scope.getEntries();
                }).
                error(function(data) {
                    console.log(data);
                });
        } else if(getParameterByName("createrogan")){
            console.log("create rogan");
            $http({method: 'GET', url: '/createrogan'}).
                success(function(data) {
                    alert(data);
                })
        } else {
            $scope.getEntries();
        }

    };

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
                        loginObj.loggedIn();
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
    };
    
    $scope.addEntry = function ( ) {
        //Adds a new entry containing only the current date, adds it to the
        //entries list and processes it

        $http({method: 'POST', url: '/add', params: {userid: $scope.loginObj.user.uid}}).success( function ( entry ) {
            console.log(entry);
            $scope.entries.unshift ( entry );
            entryProcessService.processEntry( entry );
        });

    };

    $scope.addComment = function (entry, commentText) {
        //var comment = {author: $scope.loginObj.user.displayName, date: new Date()}
        $http({method: 'POST', url: '/addcomment', params: {entrykey: entry.key, type: "entry", comment: commentText, userid: $scope.loginObj.user.uid}}).success( function ( comment ) {
            if(!entry.hasOwnProperty("comments")){
                entry.comments = [];
            }
            entry.comments.push ( comment );
        });

        entry.txtComment = "";
        entry.addingComment = false;
    };
    
    $scope.clickAddAttachment = function( entry ){

        var modalInstance = $modal.open({
            templateUrl: "views/modal-addattachment.html",
            scope: $scope,
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
                };

                $scope.addAttachment = function(attachment){

                    $http({method: 'POST', url: '/addattachment', params: {entrykey: entry.key, url: attachment.url, userid: $scope.$parent.loginObj.user.uid, attachmenttype: $scope.currentTab}}).success( function ( data ) {
                        console.log(data);
                        var attachmentArray = [data, attachment.url, $scope.currentTab];
                        entryProcessService.addAttachment(entry, attachmentArray);
                    });

                    $modalInstance.close();
                }

            }
        });
    };
  
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
    };
    
    $scope.deleteEntry = function ( entry ) {
        
        //Pop up a dialog confirming that the user wants to delete this entry
        var confirmText = "Are you sure you want to delete the entry: '" +
                          entry.title + "'?"
        bootbox.confirm(confirmText, function(result) {
            if ( result === true ){

                $http({method: 'POST', url: '/delete', params: {postid: entry.key, userid: $scope.loginObj.user.uid}}).success( function ( data ) {
                    //Remove the entry from the entries array and call scope
                    //$apply to force a angularJS refresh
                    $timeout(function(){
                        $scope.entries.splice( $.inArray( entry, $scope.entries), 1 );
                        $scope.$apply();
                    });
                });

            }
        }); 

    };

    $scope.editEntryDate = function ( entry ){
        var newDate = prompt("Enty date: (format MM/DD/YYYY");
        if(newDate){
            $http({method: 'POST', url: '/editdate', params: {entrykey: entry.key, date: newDate, userid: $scope.loginObj.user.uid}}).success( function ( data ) {
                console.log(data);
            });

            entry.date = entryProcessService.formattedDate( newDate );

        }
    };

    $scope.editEntryContent = function ( entry ){

        $http({method: 'POST', url: '/editcontent', params: {entrykey: entry.key, content: entry.content, userid: $scope.loginObj.user.uid}}).success( function ( data ) {
            console.log(data);
        });

        entryProcessService.formatTitle(entry);
        entry.editcontent = false;

    };

    $scope.tagAdded = function ( entry, tag ){
        $http({method: 'POST', url: '/addtag', params: {entrykey: entry.key, entrytype: "entry", tag: tag, userid: $scope.loginObj.user.uid}}).success( function ( data ) {
            console.log(data);
        });
    };

    $scope.tagRemoved = function ( entry, tag ){
        $http({method: 'POST', url: '/deletetag', params: {entrykey: entry.key, entrytype: "entry", tag: tag, userid: $scope.loginObj.user.uid}}).success( function ( data ) {
            console.log(data);
        });
    };

    $scope.newLineBreak = function ( str ){
        return str.replace(/(?:\r\n|\r|\n)/g, '<br />');
    };

    var dataRef = new Firebase("https://familyarchive.firebaseio.com");
    $scope.loginObj = $firebaseSimpleLogin(dataRef);

    $scope.loginObj.$getCurrentUser().then(function (user) {
            if (!$scope.loginObj.user) {
                $scope.loginScreen($scope);
            } else {
                //Successfully logged in
                if(!$scope.hasLoggedIn) {
                    console.log("Already logged in");
                    $scope.loggedIn();
                }
            }
        }
    );

    $scope.loginObj.loggedIn = $scope.loggedIn;

});
