var mainApp = angular.module('familyarchiveApp', []);

mainApp.factory('entryProcessService', function() {
    var obj = {};
    
    obj.formattedDate = function(dateStr){
        dateObj = new Date(dateStr);
        var month = dateObj.getMonth();
        var monthList = ['January','February','March','April','May','June','July','August','September','October','November','December']; 
        strOut = monthList[month] + " " + dateObj.getDate() + ", " + dateObj.getFullYear();
        return strOut;
    };
        
    obj.processEntry = function(entry) {
        entry.date = obj.formattedDate(entry.date);
        
        var entryTitle = entry.date;
        var entryContent = "";
        var titleText = entry.content;
        if(titleText){
            var firstSplit = titleText.indexOf('\n');
            if(firstSplit != -1){
                var contentSplit = titleText.split("\n");
                if(contentSplit[0].length<100){
                    entryTitle = contentSplit[0];
                    entryContent = titleText.slice(firstSplit+1).replace(/\n/g, '<br />');
                } else {
                    entryContent = titleText.replace(/\n/g, '<br />');
                }
            } else {
                if (titleText.length<100){
                    entryTitle = titleText;
                } else {
                    entryContent = titleText;
                }
            }
        }
        entry['title'] = entryTitle;
        entry['content'] = entryContent;
        return(entry);
    };
    
    return obj;
});

var entriesCtrl = mainApp.controller('EntriesCtrl', function ($scope, $http, entryProcessService) {
    $scope.entries = [];
    $http.get('entries.json').success(function(data) {
        for(var i=0;i<data.length;i++){
            $scope.entries.push(entryProcessService.processEntry(data[i]));
        }
  });
});
