mainApp.service('entryProcessService', function( $injector ) {
    /*
    We call this service to process the json entries we get from the server.
    For each entry .processEntry is called, which in turn calls functions which
    format the text, retrieve attachments, etc.
    */

    //Hold a dictionary of attachments services that have already been injected
    //into this service so we don't inject twice
    var injectedAttachmentServices = {};

    this.processEntry = function ( entry ) {
        entry.images = []; //We have a seperate image list to our attachments
                            //list because we could have multiple images per
                            //attachment
        entry.date = this.formattedDate ( entry.date );
        this.formatTitle ( entry );
        this.retrieveAttachments ( entry );
    };

    this.formattedDate = function(dateStr){
        dateObj = new Date(dateStr);
        var month = dateObj.getMonth();
        var monthList = ['January','February','March','April','May','June','July','August','September','October','November','December']; 
        strOut = monthList[month] + " " + dateObj.getDate() + ", " + dateObj.getFullYear();
        return strOut;
    };
    
    this.formatTitle = function(entry) {
        //If the entry has no content use the entry's date as the title.
        var entryTitle = entry.date;
        var entryContent = "";
        var titleText = entry.content;
        if(titleText){
            //If the content has a line break use the first line as the title
            //as long as it is less than 100 characters
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
                //If the content has no line break but is less than 100 characters
                //then use it as the title
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

    this.addAttachment = function (entry, attachmentItem) {
        var attachmentType = attachmentItem [ 2 ];

        //Inject the attachment service as a dependency for this service
        //if it hasn't already been injected
        var serviceName = attachmentType + "AttachmentService";
        if ( injectedAttachmentServices.hasOwnProperty ( serviceName )) {
            var attachmentService = injectedAttachmentServices [ serviceName ];
        } else {
            var attachmentService = $injector.get ( serviceName );
            injectedAttachmentServices [ serviceName ] = attachmentService;
        }

        attachmentService.getImages ( entry, attachmentItem );

    }
    
    this.retrieveAttachments = function ( entry ) {
        //For each attachment use the attachment service for the given
        //attachment type and call its getImages function to get the image
        //list that the entry will use
        if(entry.attachments){
            for ( var i = 0; i < entry.attachments.length; i++ ){
                var attachmentItem = entry.attachments [ i ];
                this.addAttachment(entry, attachmentItem);
            }
        }
    }

});
