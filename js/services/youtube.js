var youtubeService = mainApp.service('youtubeAttachmentService', function() {

    this.getImages = function ( entry, attachment ) {
        var url = attachment [ 1 ];
        entry.images.push ({ thumbnailsrc: this.getYouTubeThumbnail ( url, "big" ),
                             attachment: attachment });
    }
    
    this.getYouTubeThumbnail = function ( url, size ){
        if(url === null){ return ""; }
        size = (size === null) ? "big" : size;
        var vid;
        var results;
        results = url.match("[\\?&]v=([^&#]*)");
        vid = ( results === null ) ? url : results[1];
        if (size == "small"){
            return "http://img.youtube.com/vi/"+vid+"/2.jpg";
        } else {
            return "http://img.youtube.com/vi/"+vid+"/0.jpg";
        }
    };

});
