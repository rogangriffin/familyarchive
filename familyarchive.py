import cgi
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import mail
from google.appengine.ext.webapp.util import run_wsgi_app
import datetime
import sys
import json
import time
import urllib
import templates
import api
import logging
from dbModels import *

def GetSingleEntry(entry, userPerson=None):
	outEntry = {}
	if entry.author:
		outEntry['author'] = entry.author.fullname
		if userPerson.key() == entry.author.key():
			outEntry['authoredit'] = 1
			if entry.ancestorlist:
				outEntry['ancestorlist'] = entry.ancestorlist					
	if entry.date:
		outEntry['date'] = str(entry.date.strftime("%m/%d/%Y"))
	if entry.content:
		outEntry['content'] = entry.content
	if entry.attachmentList:
		outAttachmentList = []
		#Iterate through attachment list
		for attachmentKey in entry.attachmentList:
			attachment = db.get(attachmentKey)
			outAttachment = []
			outAttachment.append(str(attachmentKey))
			outAttachment.append(attachment.filename)
			outAttachment.append(attachment.attachmentType)
			outAttachmentList.append(outAttachment)
		outEntry['attachments'] = outAttachmentList
	if entry.comments:
		outComments = []
		for commentKey in entry.comments:
			dbComment = db.get(commentKey)
			outComment = {}
			if dbComment.adddate:
				outComment['date'] = str(dbComment.adddate.strftime("%b %d, %Y"))
			outComment['author'] = dbComment.author.fullname
			outComment['content'] = dbComment.content
			outComments.append(outComment)
		outEntry['comments'] = outComments
	outEntry['key'] = str(entry.key())
	outEntry['tags'] = entry.tags
	return outEntry

def GetAncestorMarriages(marriage):
    outMarriages = []
    outMarriages.append(marriage)
    q = Person.all()
    q.filter("marriage =", marriage)
    for p in q.run(limit=4):
        if p.parentmarriage:
            outMarriages += GetAncestorMarriages(p.parentmarriage)
    return outMarriages
    
def GetEntryList(userPerson, startDate, tag="", offsetIndex=0):
    txtTags = ""
    txtOffset = ""
    if tag:
    	txtTags = "AND tags = '" + tag + "' "
    if offsetIndex>0:
    	txtOffset = "OFFSET " + str(offsetIndex) + " "
    outList = []
    ancestorList = []
    marriageList = GetAncestorMarriages(userPerson.marriage)
    for m in marriageList:
        if not "'" + str(m.key()) + "'" in ancestorList:
            ancestorList.append("'" + str(m.key()) + "'")
    
    logging.info(",".join(ancestorList))
    entries = db.GqlQuery("SELECT * FROM JournalEntry WHERE date >= :1 AND ancestorlist IN (" + ",".join(ancestorList) + ") AND deleted = False " + txtTags + "ORDER BY date LIMIT 20 " + txtOffset, startDate)
    for entry in entries:
    	outList.append(GetSingleEntry(entry,userPerson))
    return outList

def GetSingleAttachment(attachment):
	outAttachment = {}
	if attachment.date:
		outAttachment['date'] = str(attachment.date.strftime("%d %b, %Y"))
	if attachment.comments:
		outComments = []
		for commentKey in attachment.comments:
			dbComment = db.get(commentKey)
			outComment = {}
			if dbComment.adddate:
				outComment['date'] = str(dbComment.adddate.strftime("%d %b, %Y"))
			outComment['author'] = dbComment.author.fullname
			outComment['content'] = dbComment.content
			outComment['metaindex'] = dbComment.metaindex
			outComments.append(outComment)
		outAttachment['comments'] = outComments
	outAttachment['key'] = str(attachment.key())
	outAttachment['tags'] = attachment.tags
	outAttachment['filename'] = attachment.filename
	outAttachment['attachmenttype'] = attachment.attachmentType
	return outAttachment

def GetAttachmentList(userPerson, startDate, tag="", attachmentType="", offsetIndex=0):
    txtTags = ""
    txtAttachmentType = ""
    txtOffset = ""
    if tag:
    	txtTags = "AND tags = '" + tag + "' "
    if attachmentType:
    	txtAttachmentType = "AND attachmentType = '" + attachmentType + "' "
    if offsetIndex>0:
    	txtOffset = "OFFSET " + str(offsetIndex) + " "
    outList = []
    if userPerson.parentmarriage:
        ancestorList = str(userPerson.marriage.key()) + "', '" + str(userPerson.parentmarriage.key())
    else:
        ancestorList = str(userPerson.marriage.key())
    entries = db.GqlQuery("SELECT * FROM Attachment WHERE date >= :1 AND ancestorlist IN ('" + ancestorList + "') AND deleted = False " + txtTags + txtAttachmentType + "ORDER BY date LIMIT 20 " + txtOffset, startDate)
    for entry in entries:
    	outList.append(GetSingleAttachment(entry))
    return outList

def CreateParents(fatherKey, fatherName, motherKey, motherName):
	if fatherKey and motherKey:
		father = Person.get(fatherKey)
		parentMarriage = father.marriage
	if motherKey and fatherKey=="":
		mother = Person.get(motherKey)
		parentMarriage = mother.marriage
		father = Person()
		father.fullname = fatherName
		father.marriage = parentMarriage
		father.put()
	if fatherKey and motherKey=="":
		father = Person.get(fatherKey)
		parentMarriage = father.marriage
		mother = Person()
		mother.fullname = motherName
		mother.marriage = parentMarriage
		mother.put()
	if fatherKey=="" and motherKey=="":
		parentMarriage = Marriage()
		parentMarriage.put()
		father = Person()
		father.fullname = fatherName
		father.marriage = parentMarriage
		father.put()
		mother = Person()
		mother.fullname = motherName
		mother.marriage = parentMarriage
		mother.put()
	return parentMarriage

class MainPage(webapp.RequestHandler):
    def get(self):
        postid = self.request.get('postid')
        viewas = self.request.get('viewas')
        pageHTML = templates.GeneratePage("entries", self, postid, viewas)
        self.response.out.write(pageHTML)

class Videos(webapp.RequestHandler):
	def get(self):
		pageHTML = templates.GeneratePage("videos", self) 
		self.response.out.write(pageHTML)

class RequestEntries(webapp.RequestHandler):
    def post(self):
        fromDate = self.request.get('fromdate')
        searchTag = self.request.get('tag')
        postid = self.request.get('postid')
        offsetIndex = int(self.request.get('offset'))
        userPerson = templates.GetUser(self)
        
        if not fromDate:
            fromDate = "01/01/1900"
        someDate = datetime.datetime.strptime(fromDate,"%m/%d/%Y")
        if postid:
            entryID = self.request.get('postid')
            entry = JournalEntry.get(entryID)
            someDate = entry.date
            myEntry = GetSingleEntry(entry, userPerson)
        else:
            myEntry = None
        outList = GetEntryList(userPerson, someDate, searchTag, offsetIndex)
        if myEntry in outList:
            outList.pop(outList.index(myEntry))
        if myEntry:
            outList.insert(0, myEntry)
        self.response.out.write(json.dumps(outList))

class RequestAttachments(webapp.RequestHandler):
    def post(self):
        userPerson = templates.GetUser(self)
        fromDate = self.request.get('fromdate')
        searchTag = self.request.get('tag')
        attachmentType = self.request.get('attachmenttype')
        offsetIndex = int(self.request.get('offset'))
        if not fromDate:
            fromDate = "01/01/1900"
        someDate = datetime.datetime.strptime(fromDate,"%m/%d/%Y")
        outList = GetAttachmentList(userPerson, someDate, searchTag, attachmentType, offsetIndex)
        self.response.out.write(json.dumps(outList))

class RequestAttachment(webapp.RequestHandler):
    def post(self):
        key = self.request.get('key')
        attachment = Attachment.get(key)
        attachmentDic = GetSingleAttachment(attachment)
        self.response.out.write(json.dumps(attachmentDic))
        
class AddEntry(webapp.RequestHandler):
    def post(self):
        myPerson = templates.GetUser(self)
        entry = JournalEntry()
        entry.author = myPerson
        convertedDate = datetime.datetime.today()
        ancestorList = []
        ancestorList.append(str(myPerson.marriage.key()))
        entry.ancestorlist = ancestorList
        entry.put()
        outEntry = GetSingleEntry(entry,myPerson)
        self.response.out.write(json.dumps(outEntry))

class AddComment(webapp.RequestHandler):
    def post(self):
        myPerson = templates.GetUser(self)
        entryKey = self.request.get('entrykey')
        commentText = self.request.get('comment')
        commentType = self.request.get('type')
        if self.request.get('metaindex'):
            metaIndex = int(self.request.get('metaindex'))
        else:
            metaIndex = 0
        if commentType:
            if commentType=="entry":
                entry = JournalEntry.get(entryKey)
            if commentType=="attachment":
                entry = Attachment.get(entryKey)
            if commentText:
                newComment = Comment()
                newComment.author = myPerson
                newComment.content = commentText
                newComment.metaindex = metaIndex
                newComment.put()
                entry.comments.append(newComment.key())
                entry.put()
                self.response.out.write("success")

class AddAncestor(webapp.RequestHandler):
    def post(self):
        entryKey = self.request.get('entrykey')
        newMarriage = self.request.get('marriage')
        entry = JournalEntry.get(entryKey)
        if newMarriage:
            if not newMarriage in entry.ancestorlist:
                entry.ancestorlist.append(newMarriage)
                entry.put()
                for attachmentKey in entry.attachmentList:
                    attachment = db.get(attachmentKey)
                    attachment.ancestorlist = entry.ancestorlist
                    attachment.put()
            self.response.out.write("success")
            
class RemoveAncestor(webapp.RequestHandler):
    def post(self):
        entryKey = self.request.get('entrykey')
        newMarriage = self.request.get('marriage')
        entry = JournalEntry.get(entryKey)
        self.response.out.write("success")
        if newMarriage:            
            if newMarriage in entry.ancestorlist:
                entry.ancestorlist.remove(newMarriage)
                entry.put()
                for attachmentKey in entry.attachmentList:
                    attachment = db.get(attachmentKey)
                    attachment.ancestorlist = entry.ancestorlist
                    attachment.put()
            self.response.out.write("success")
		
class AddTag(webapp.RequestHandler):
	def post(self):
		entryKey = self.request.get('entrykey')
		entryType = self.request.get('entrytype')
		newTag = self.request.get('tag')
		if newTag:
			if entryType=="entry":
				entry = JournalEntry.get(entryKey)
				entry.tags.append(newTag)
				entry.put()
				if entry.attachmentList:
					for attachmentKey in entry.attachmentList:
						attachment = db.get(attachmentKey)
						attachment.tags.append(newTag)
						attachment.put()
			elif entryType=="attachment":
				entry = Attachment.get(entryKey)
				entry.tags.append(newTag)
				entry.put()
			self.response.out.write("success")

class AddAttachment(webapp.RequestHandler):
    def post(self):
        myPerson = templates.GetUser(self)
        entryKey = self.request.get('entrykey')
        attachmentFile = self.request.get('attachmentfile')
        attachmentType = self.request.get('attachmenttype')
        entry = JournalEntry.get(entryKey)
        if attachmentFile:
            tempAttachment = Attachment()
            tempAttachment.filename = attachmentFile
            tempAttachment.author = myPerson
            tempAttachment.date = entry.date
            tempAttachment.ancestorlist = entry.ancestorlist
            tempAttachment.tags = entry.tags
            tempAttachment.attachmentType = attachmentType
            tempAttachment.put()
            entry.attachmentList.append(tempAttachment.key())
            entry.put()
            self.response.out.write(str(tempAttachment.key()))

class DeleteAttachment(webapp.RequestHandler):
	def post(self):
		entryID = self.request.get('attachmentid')
		attachmententry = Attachment.get(entryID)
		attachmententry.deleted = True
		attachmententry.put()
		query = db.Query(JournalEntry)
		query.filter('attachmentList =', attachmententry.key())
		entries = query.fetch(limit=5)
		for entry in entries:
			entry.attachmentList.remove(attachmententry.key())
			entry.put()
		self.response.out.write("success")
		
class EditDate(webapp.RequestHandler):
	def post(self):
		entryKey = self.request.get('entrykey')
		newDate = self.request.get('date')
		entry = JournalEntry.get(entryKey)
		if newDate:
			convertedDate = datetime.datetime.strptime(newDate,"%m/%d/%Y")
			entry.date = convertedDate
			entry.put()
			if entry.attachmentList:
				for attachmentKey in entry.attachmentList:
					attachment = db.get(attachmentKey)
					attachment.date = convertedDate
					attachment.put()
			self.response.out.write("success")

class EditContent(webapp.RequestHandler):
	def post(self):
		entryKey = self.request.get('entrykey')
		newContent = self.request.get('content')
		entry = JournalEntry.get(entryKey)
		if newContent:
			entry.content = newContent
			entry.put()
			self.response.out.write("success")
			
class DeleteEntry(webapp.RequestHandler):
	def post(self):
		entryID = self.request.get('postid')
		entry = JournalEntry.get(entryID)
		entry.deleted = True
		entry.put()
		self.response.out.write("success")

def GetAllDescendants(marriage):
    outPeople = []
    q = Person.all()
    q.filter("marriage =", marriage)
    for p in q.run(limit=4):
        outPeople.append(p)
    
    q = Person.all()
    q.filter("parentmarriage =", marriage)
    for p in q.run(limit=50):
        outPeople += GetAllDescendants(p.marriage)
    return outPeople

class SendEmail(webapp.RequestHandler):
    def get(self):
        self.post()

    def post(self):
        userPerson = templates.GetUser(self)
        entryID = self.request.get('postid')
        entry = JournalEntry.get(entryID)
        titleText = entry.content
        entryTitle = str(entry.date.strftime("%B %d, %Y"))
        entryContent = ""
        if titleText:
            if "\n" in titleText:
                contentSplit = titleText.split("\n", 1)
                if len(contentSplit[0]) < 100:
                    entryTitle = contentSplit[0]
                    entryContent = contentSplit[1].replace('\n', '<br />')
                else:
                    entryContent = titleText.replace('\n', '<br />')
            else:
                if len(titleText) <100:
                    entryTitle = titleText
                else:
                    entryContent = titleText

        outHTML = "<span style='font-size:20px;color:#888;font-family: arial'>" + entryTitle + "</span><br />"
        outHTML += "<span style='font-size:12px;color:#AAA;font-family: arial'>" + str(entry.date.strftime("%B %d, %Y")) + "</span><br /><br />"
        outHTML += "<span style='font-size:12px;color:#888;font-family: arial'>" + entryContent + "</span><br /><br />"
        outHTML += "<span style='font-size:10px;color:#AAA;font-family: arial'>You may need to click Display Images in your email client to see the pictures in this email</span><br />"

        personDBList = []
        personKeyList = []
        marriageList = []
        for marriageKey in entry.ancestorlist:
            marriage = Marriage.get(marriageKey)
            for p in GetAllDescendants(marriage):
                if not str(p.key()) in personKeyList:
                    personDBList.append(p)
                    personKeyList.append(str(p.key()))

        personList = []
        for p in personDBList:
            userName = ""
            if p.username:
                userName = str(p.username)
                if not "@" in userName:
                    userName = userName + "@gmail.com"
            elif p.email:
                userName = p.email
            if userName:
                userName = p.fullname + " <" + userName + ">"
                if not userName in personList:
                    personList.append(userName)
        
        if entry.attachmentList:
            #Iterate through attachment list
            for attachmentKey in entry.attachmentList:
                attachment = db.get(attachmentKey)
                attachmentFilename =  attachment.filename
                attachmentType = attachment.attachmentType
                if attachmentType=="video":
                    import urlparse
                    url_data = urlparse.urlparse(attachmentFilename)
                    query = urlparse.parse_qs(url_data.query)
                    videoId = query["v"][0]
                    attachmentImg =  "http://img.youtube.com/vi/"+videoId+"/0.jpg"
                    outHTML += "<a href='" + attachmentFilename + "'><img height=175 src='" + attachmentImg + "' /></a>"
                elif attachmentType=="picasa":
                    import gdata.photos.service
                    gd_client = gdata.photos.service.PhotosService()
                    urlSplit = attachmentFilename.rsplit("/",1)
                    urlStart = urlSplit[0]
                    urlEnd = urlSplit[1]
                    urlStart = urlStart.replace("https://picasaweb.google.com/", "/data/feed/api/user/")
                    url = urlStart + "/album/" + urlEnd
                    photos = gd_client.GetFeed(url)
                    for photo in photos.entry:
                        if ".mp4" in photo.title.text.lower():
                            largeURL = "$TARGETURL$"
                        else:
                            large = photo.content.src
                            urlSplit = large.rsplit("/",1)
                            largeURL = urlSplit[0] + "/s1000/" + urlSplit[1]
                        outHTML += "<a href='" + largeURL + "'><img height=175 src='" + photo.media.thumbnail[2].url + "' /></a>"
        outHTML += "<br /><br /><table width='100%' style='border-width:1px;border-style:solid;border-color:#666;' align='center' cellpadding=10><tr><td align=center><font size='4' face='arial'><a href='$TARGETURL$' style='text-decoration:none;'>Share your memories of this event at myfamilyrecord.appspot.com</a><br />or by simply replying-all to this message</font></td></tr></table>"

        outHTML = outHTML.replace("$TARGETURL$", "http://myfamilyrecord.appspot.com/?postid=" + entryID)
        senderEmail = str(userPerson.username)
        if not "@" in senderEmail:
            senderEmail = senderEmail + "@gmail.com"
        message = mail.EmailMessage(sender=userPerson.fullname + " <" + senderEmail + ">", subject=entryTitle)
        message.to = ", ".join(personList)
        message.body = entryTitle + "\n\n" + entryContent + "\n\nGo to http://myfamilyrecord.appspot.com/?postid=" + entryID + " to view the pictures"
        message.html = outHTML
        message.send()
        
        self.response.out.write("Emails sent to: " + ", ".join(personList))
                            

        
class CreateRogan(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user:
			webApp.redirect(users.create_login_url(webApp.request.uri))
			
		if user.nickname()=="rogangriffin":
			createPerson = Person()
			createPerson.username = user
			createPerson.fullname = "Rogan Griffin"
			myMarriage = Marriage()
			myMarriage.put()
			createPerson.marriage = myMarriage
			createPerson.put()
			self.response.out.write("Invitation: " + str(createPerson.key()))
		else:
			self.response.out.write("username: " + user.nickname())

class CreatePerson(webapp.RequestHandler):
	def get(self):
		pageHTML = templates.GenerateCreatePersonPage(self)
		self.response.out.write(pageHTML)
		
	def post(self):
		spouse = None
		myMarriage = None
		cmbMain = self.request.get('cmbMain')
		cmbSpouse = self.request.get('cmbSpouse')
		
		#main person		
		if cmbMain:
			myPerson = Person.get(cmbMain)
			myMarriage = myPerson.marriage
		else:
			myPerson = Person()
			myPerson.fullname = self.request.get('txtMain')
		
		#parents
		parentMarriage = CreateParents(self.request.get('cmbFather'), self.request.get('txtFather'), self.request.get('cmbMother'), self.request.get('txtMother'))
		myPerson.parentmarriage = parentMarriage
		
		#Marriage
		if cmbSpouse:
			spouse = Person.get(cmbSpouse)
			myMarriage = spouse.marriage
		else:
			if not myMarriage:
				myMarriage = Marriage()
				myMarriage.put()
		myPerson.marriage = myMarriage
		
		myPerson.put()
		
		#Spouse
		txtSpouse = self.request.get('txtSpouse')
		if spouse or txtSpouse:
			if not spouse:
				spouse = Person()
				spouse.fullname = txtSpouse
				spouse.marriage = myMarriage
		
			#parents-in-law
			inlawMarriage = CreateParents(self.request.get('cmbFatherInLaw'), self.request.get('txtFatherInLaw'), self.request.get('cmbMotherInLaw'), self.request.get('txtMotherInLaw'))
			spouse.parentmarriage = inlawMarriage
			spouse.put()
		self.response.out.write("success")

class InvitePerson(webapp.RequestHandler):
	def get(self):
		pageHTML = templates.GenerateInvitePersonPage(self)
		self.response.out.write(pageHTML)
	
	def post(self):
		userkey = self.request.get('user')
		email = self.request.get('email')
		msgBody = "You have been invited to view family home videos on My Family Record.\n"
		msgBody += "Just click on the following link to activate your account: http://myfamilyrecord.appspot.com/videos?invite=" + userkey
		msgBody += "\n"
		mail.send_mail(sender="rogangriffin@gmail.com", to=email, subject="Family Record Invitation", body=msgBody)
		self.response.out.write(msgBody)

class SignupPerson(webapp.RequestHandler):
    def post(self):
        pass
        
class SetEmail(webapp.RequestHandler):
    def get(self):
        userkey = self.request.get('user')
        email = self.request.get('email')
        person = Person.get(userkey)
        person.email = email
        person.put()
        self.response.out.write("Set user: " + person.fullname + "'s email to: " + person.email)
        
class TestFunc(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        self.response.out.write("username: " + user.nickname())
        query = db.GqlQuery("SELECT * FROM Person WHERE username = :1", user)
        totalRows = query.count()
        if totalRows<1:
            self.response.out.write("Username not in the database");
        else:
            userPerson = query.fetch(1)[0]
            self.response.out.write("<br>user: " + str(userPerson.key()))
            userMarriage = userPerson.marriage
            entries = db.GqlQuery("SELECT * FROM JournalEntry WHERE ancestorlist = 'ag5teWZhbWlseXJlY29yZHIPCxIITWFycmlhZ2UYgn0M'")
            updatedNumber = 0
            for entry in entries:
                ancestorList = []
                ancestorList.append(str(userMarriage.key()))
                entry.ancestorlist = ancestorList
                updatedNumber = updatedNumber + 1
                entry.put()
            self.response.out.write("<br>updated " + str(updatedNumber) + " journal records")
            entries = db.GqlQuery("SELECT * FROM Attachment WHERE ancestorlist = 'ag5teWZhbWlseXJlY29yZHIPCxIITWFycmlhZ2UYgn0M'")
            updatedNumber = 0
            for entry in entries:
                ancestorList = []
                ancestorList.append(str(userMarriage.key()))
                entry.ancestorlist = ancestorList
                updatedNumber = updatedNumber + 1
                entry.put()
            self.response.out.write("<br>updated " + str(updatedNumber) + " attachment records")
            


class Diagnostics(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        self.response.out.write("username: " + user.nickname())
        query = db.GqlQuery("SELECT * FROM Person WHERE username = :1", user)
        totalRows = query.count()
        if totalRows<1:
            self.response.out.write("Username not in the database");
        else:
            userPerson = query.fetch(1)[0]
            self.response.out.write("<br>user: " + str(userPerson.key()))
            userMarriage = userPerson.marriage
            self.response.out.write("<br>marriage: " + str(userMarriage.key()))
            for marriagePeople in userMarriage.mymarriage:
                if marriagePeople.key() != userPerson.key():
                    spousePerson = marriagePeople
                    self.response.out.write("<br>spouse: " + str(spousePerson.key()))
            parentMarriage = userPerson.parentmarriage
            self.response.out.write("<br>parent marriage: " + str(parentMarriage.key()))
            offsetIndex = 0
            fromDate = "01/01/1900"
            startDate = datetime.datetime.strptime(fromDate,"%m/%d/%Y")
            if userPerson.parentmarriage:
                ancestorList = str(userPerson.marriage.key()) + "', '" + str(userPerson.parentmarriage.key())
            else:
                ancestorList = str(userPerson.marriage.key())
            sql = "SELECT * FROM JournalEntry WHERE date >= " + str(startDate) + " AND ancestorlist IN ('" + ancestorList + "') AND deleted = False ORDER BY date LIMIT 20 "
            self.response.out.write("<br>sql: " + sql)
            entries = db.GqlQuery("SELECT * FROM JournalEntry WHERE date >= :1 AND ancestorlist IN ('" + ancestorList + "') AND deleted = False ORDER BY date LIMIT 20 ", startDate)
            for entry in entries:
                self.response.out.write("<br>entry key: " + str(entry.key()))

application = webapp.WSGIApplication(
        [('/', MainPage),
        ('/entries', RequestEntries),
        ('/attachments', RequestAttachments),
        ('/attachment', RequestAttachment),
        ('/add', AddEntry),
        ('/addattachment', AddAttachment),
        ('/deleteattachment', DeleteAttachment),
        ('/addcomment', AddComment),
        ('/addtag', AddTag),
        ('/addancestor', AddAncestor),
        ('/removeancestor', RemoveAncestor),
        ('/editdate', EditDate),
        ('/editcontent', EditContent),
        ('/invite', InvitePerson),
        ('/create', CreatePerson),
        ('/createrogan', CreateRogan),
        ('/setemail', SetEmail),
        ('/signup', SignupPerson),
        ('/delete', DeleteEntry),
        ('/sendemail', SendEmail),
        ('/videos', Videos),
        ('/apipostattachmententry', api.PostAttachmentEntry),
        ('/test', TestFunc),
        ('/diag', Diagnostics)],
        debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
    