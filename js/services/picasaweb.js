var picasawebService = mainApp.service('picasawebAttachmentService', function( $http, $rootScope ) {
    
    var that = this;

    this.getImages = function ( entry, attachment ) {
        
        var attachmentURL = attachment [ 1 ];
        
        //Format the URL to one for performing our API call
        var urlStart = attachmentURL.substring(0, attachmentURL.lastIndexOf('/'));
        var urlEnd = attachmentURL.split("/").pop();
        urlStart = urlStart.replace("https://picasaweb.google.com/", "http://picasaweb.google.com/data/feed/api/user/");
        var url = urlStart + "/album/" + urlEnd + "&alt=json";
        url = url.replace("#", "");
        
        //Make a call to the PicasaWeb API for album data
        $http.get( url ).success ( function ( data ) {
            for ( var j = 0; j < data.feed.entry.length; j++ ){
                var dataentry = data.feed.entry[j];
                var thumbnail = dataentry['media$group']['media$thumbnail'][2]['url'];
                var thumbnailWidth = dataentry['media$group']['media$thumbnail'][2]['width'];
                var thumbnailHeight = dataentry['media$group']['media$thumbnail'][2]['height'];
                var title = dataentry['title']['$t'];
                var image = { attachment: attachment,
                              thumbnailsrc: thumbnail,
                              thumbnailwidth: thumbnailWidth,
                              thumbnailheight: thumbnailHeight,
                              orderindex: j,
                              service: that
                            };
                if(title.indexOf(".mp4") != -1){
                    //This is a Picasa Video
                    var contentList = dataentry['media$group']['media$content'];
                    var fmt = get_fmt(contentList);
                    image['large'] = "picasavideo";
                    image['fmt_list'] = encodeURIComponent(fmt.list.join())
                    image['fmt_stream_map'] = encodeURIComponent(fmt.stream_map.join())
                } else {
                    //This is a Picasa photo
                    var large = dataentry['content']['src'];
                    var urlbef = large.substring(0, large.lastIndexOf('/'));
                    var urlaft = large.substring(large.lastIndexOf('/'));
                    image['large'] = urlbef + "/s600" + urlaft;
                }
                entry.images.push ( image );
            }
        });

    }
    
    this.getModalHTMLTemplate = function (){
        return "js/services/picasaweb-modal.html"
    }

    $rootScope.attachmentServices.push("picasaweb");


});

mainApp.directive('picasawebAddDirective', function () {
    return {
        template: '<div><h5>URL of unlisted/public PicasaWeb Album:</h5><p class="small">(Copy from address bar at the top of the page when on the album in PicasaWeb, not in Google+ photos)</p><input type="text" class="form-control" ng-model="attachment.url"/><button class="btn btn-primary pull-right" ng-click="addAttachment(attachment)">Submit</button><div class="clear"></div></div>',
        restrict: 'E'
    };
});