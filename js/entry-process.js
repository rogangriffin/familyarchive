mainApp.factory('entryProcessService', function( $injector ) {
    var obj = {};
    
    //Inject our attachment services
    //var entryProcessService = $injector.get('entryProcessService')
    
    obj.formattedDate = function(dateStr){
        dateObj = new Date(dateStr);
        var month = dateObj.getMonth();
        var monthList = ['January','February','March','April','May','June','July','August','September','October','November','December']; 
        strOut = monthList[month] + " " + dateObj.getDate() + ", " + dateObj.getFullYear();
        return strOut;
    };
    
    obj.formatTitle = function(entry) {
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
    }
    
    obj.retrieveAttachments = function ( entry ) {
        for ( var i=0; i < entry.attachments.length; i++ ){
            var attachmentItem = entry.attachments [ i ];
            var attachmentKey = attachmentItem [ 0 ];
            var attachmentFile = attachmentItem [ 1 ];
            var attachmentType = attachmentItem [ 2 ];
            
            if ( attachmentType == "video" ){
                
                //Add the YouTube thumbnail to our image list
                image = { attachment: attachmentItem, 
                          thumbnailsrc: obj.getYouTubeThumbnail ( attachmentFile, "big" ) };
                entry.images.push ( image );
                
            } else if ( attachmentType == "picasa" ){
                
                //Format the URL to one for performing our API call
                var urlStart = attachmentFile.substring(0, attachmentFile.lastIndexOf('/'));
                var urlEnd = attachmentFile.split("/").pop();
                urlStart = urlStart.replace("https://picasaweb.google.com/", "http://picasaweb.google.com/data/feed/api/user/");
                var url = urlStart + "/album/" + urlEnd + "&alt=json";
                url = url.replace("#", "");
                
                /*
                //Make a call to the PicasaWeb API for album data
                $http.get(url).success(function(data) {
			        for ( var j = 0; j < data.feed.entry.length; j++ ){
				        var entry = data.feed.entry[j];
				        var thumbnail = entry['media$group']['media$thumbnail'][2]['url'];
                        var thumbnailWidth = entry['media$group']['media$thumbnail'][2]['width'];
                        var thumbnailHeight = entry['media$group']['media$thumbnail'][2]['height'];
                        var title = entry['title']['$t'];
                        var thumbnailDic = {"thumbnail": thumbnail,'attachmentType': attachmentType, 'attachmentKey': attachmentKey,'thumbnailwidth':thumbnailWidth,'thumbnailheight':thumbnailHeight,'metaindex':i}
                if(title.indexOf(".mp4") != -1){
                    //This is a Picasa Video
                    var contentList = entry['media$group']['media$content'];
                    var fmt = get_fmt(contentList);
                    thumbnailDic['large'] = "picasavideo";
                    thumbnailDic['fmt_list'] = encodeURIComponent(fmt.list.join())
                    thumbnailDic['fmt_stream_map'] = encodeURIComponent(fmt.stream_map.join())
                    attachmentThumbnails.push(thumbnailDic);
                } else {
                    //This is a Picasa photo
                    var large = entry['content']['src'];
                    var urlbef = large.substring(0, large.lastIndexOf('/'));
                    var urlaft = large.substring(large.lastIndexOf('/'));
                    thumbnailDic['large'] = urlbef + "/s600" + urlaft;
                    attachmentThumbnails.push(thumbnailDic);
                 }
                });
            */
            }
            
            
        }
    }
    
    obj.processEntry = function ( entry ) {
        entry.images = []; //We have a seperate image list to our attachments
                            //list because we could have multiple images per
                            //attachment
        entry.date = obj.formattedDate ( entry.date );
        obj.formatTitle ( entry );
        obj.retrieveAttachments ( entry );
    };
    
    obj.getYouTubeThumbnail = function ( url, size ){
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
    
    return obj;
});
