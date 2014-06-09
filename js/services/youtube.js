var youtubeService = mainApp.service('youtubeAttachmentService', function( $sce ) {

    this.getImages = function ( entry, attachment ) {
        var url = attachment [ 1 ];
        entry.images.push ({ thumbnailsrc: this.getYouTubeThumbnail ( url, "big" ),
                             attachment: attachment,
                             large: $sce.trustAsResourceUrl('http://www.youtube.com/embed/' + this.getYouTubeID( url ) + '?autoplay=1'),
                             service: angular.bind(this, this)
                            });
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
    
    this.getYouTubeID = function ( url ){
    	if(url === null){ return ""; }
    	var vid;
    	var results;
    	results = url.match("[\\?&]v=([^&#]*)");
    	vid = ( results === null ) ? url : results[1];
    	return vid
    }
    
    this.getModalHTMLTemplate = function (){
        return "js/services/youtube-modal.html"
    }

});
