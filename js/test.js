mainApp.controller ( 'TestCtrl', function ( $scope, entryProcessService ) {
    $scope.tests = [];

    $scope.addTest = function( input, bindClass, callFunc, expectedOutput, testDescription ){
        /* We can test our functions by passing them some input, a class and
        function to call with that input, and compare that with the output
        we expect to see */
        var testObj = {};
        
        var testfunc = angular.bind( bindClass, callFunc, input );
        testfunc();
        
        testObj.testSucceeded = function(){
            
            //Use Lo-Dash to perform an object value comparison to see if
            //the result of our function matched our expected output
            return _.isEqual( input, expectedOutput );
        }
        
        testObj.getStatus = function(){
            if ( testObj.testSucceeded() ){
                return testDescription + " passed successfully";
            } else {
                return testDescription + " failed - expected: " +
                       JSON.stringify(expectedOutput) + " - got: " +
                       JSON.stringify(input);
            }
        }
        
        testObj.getClass = function(){
            return testObj.testSucceeded() ? "test-pass" : "test-fail";
        }
        
        $scope.tests.push ( testObj );
    }

    //Add all our tests
    $scope.addTest ( { date: "01/01/1981" }, 
                     entryProcessService,
                     entryProcessService.processEntry,
                     { date: "January 1, 1981", images:[], title: "January 1, 1981", content: ""},
                     "entryProcessService.formattedDate" );

    $scope.addTest ( { date: "01/01/1981", content: "title" }, 
                     entryProcessService,
                     entryProcessService.processEntry,
                     { date: "January 1, 1981", images:[], title: "title", content: ""},
                     "entryProcessService.formatTitle with no line break" );

    $scope.addTest ( { date: "01/01/1981", content: "title\ncontent" }, 
                     entryProcessService,
                     entryProcessService.processEntry,
                     { date: "January 1, 1981", images:[], title: "title", content: "content"},
                     "entryProcessService.formatTitle with line break" );

    $scope.addTest ( { date: "01/01/1981", attachments: [["","http://www.youtube.com/watch?v=VzzLngXfCcI","youtube"]] }, 
                     entryProcessService,
                     entryProcessService.processEntry,
                     {"date":"January 1, 1981","attachments":[["","http://www.youtube.com/watch?v=VzzLngXfCcI","youtube"]],"images":[{"thumbnailsrc":"http://img.youtube.com/vi/VzzLngXfCcI/0.jpg","attachment":["","http://www.youtube.com/watch?v=VzzLngXfCcI","youtube"]}],"title":"January 1, 1981","content":""},
                     "youtubeAttachmentService" );

    $scope.addTest ( { date: "01/01/1981", attachments: [["","https://picasaweb.google.com/112347770428957375603/RandburgWinter1982?authkey=Gv1sRgCN35tv3w442JWA","picasaweb"]] }, 
                     entryProcessService,
                     entryProcessService.processEntry,
                     {"date":"January 1, 1981","attachments":[["","https://picasaweb.google.com/112347770428957375603/RandburgWinter1982?authkey=Gv1sRgCN35tv3w442JWA","picasaweb"]],"images":[{"attachment":["","https://picasaweb.google.com/112347770428957375603/RandburgWinter1982?authkey=Gv1sRgCN35tv3w442JWA","picasaweb"],"thumbnailsrc":"http://lh3.ggpht.com/-keHOfWufPOU/UmF36FVt3LI/AAAAAAAACzM/73mM5KJNq6c/s288/photo%252520%2525284%252529.JPG","thumbnailwidth":225,"thumbnailheight":288,"orderindex":0,"large":"http://lh3.ggpht.com/-keHOfWufPOU/UmF36FVt3LI/AAAAAAAACzM/73mM5KJNq6c/s600/photo%252520%2525284%252529.JPG"}],"title":"January 1, 1981","content":""},
                     "picasawebAttachmentService" );




});
