var youtubeService = mainApp.service('youtubeAttachmentService', function ($sce, $rootScope) {

    this.getImages = function (entry, attachment) {
        var url = attachment [ 1 ];
        entry.images.push({ thumbnailsrc: this.getYouTubeThumbnail(url, "big"),
            attachment: attachment,
            large: $sce.trustAsResourceUrl('http://www.youtube.com/embed/' + this.getYouTubeID(url) + '?autoplay=1'),
            service: angular.bind(this, this)
        });
    }

    this.getYouTubeThumbnail = function (url, size) {
        if (url === null) {
            return "";
        }
        size = (size === null) ? "big" : size;
        var vid;
        var results;
        results = url.match("[\\?&]v=([^&#]*)");
        vid = ( results === null ) ? url : results[1];
        if (size == "small") {
            return "http://img.youtube.com/vi/" + vid + "/2.jpg";
        } else {
            return "http://img.youtube.com/vi/" + vid + "/0.jpg";
        }
    };

    this.getYouTubeID = function (url) {
        if (url === null) {
            return "";
        }
        var vid;
        var results;
        results = url.match("[\\?&]v=([^&#]*)");
        vid = ( results === null ) ? url : results[1];
        return vid
    };

    this.getModalHTMLTemplate = function () {
        return "js/services/youtube-modal.html"
    };

});

mainApp.directive('youtubeAddDirective', function () {
    return {
        template: '<div><h5>URL of unlisted/public YouTube Video:</h5><input type="text" class="form-control" ng-model="attachment.url"/><button class="btn btn-primary pull-right" ng-click="addAttachment(attachment)">Submit</button><div class="clear"></div></div>',
        restrict: 'E'
    };
});
