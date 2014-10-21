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
from person import *

def GetSingleComment(dbComment):
    outComment = {}
    if dbComment.adddate:
        outComment['date'] = str(dbComment.adddate.strftime("%b %d, %Y"))
    outComment['author'] = dbComment.author.fullname
    outComment['content'] = dbComment.content
    return outComment

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
			outAttachment.append(attachment.url)
			outAttachment.append(attachment.attachmentType)
			outAttachmentList.append(outAttachment)
		outEntry['attachments'] = outAttachmentList
	if entry.comments:
		outComments = []
		for commentKey in entry.comments:
			dbComment = db.get(commentKey)
			outComments.append(GetSingleComment(dbComment))
		outEntry['comments'] = outComments
	outEntry['key'] = str(entry.key())
	outEntry['tags'] = entry.tags
	return outEntry

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
	outAttachment['url'] = attachment.url
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

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.out.write("")

class Videos(webapp.RequestHandler):
	def get(self):
		self.response.out.write("")

class RequestEntries(RequestHandler):
    def completeRequest(self):
        fromDate = self.request.get('fromdate')
        searchTag = self.request.get('tag')
        postid = self.request.get('postid')
        if(self.request.get('offset')):
            offsetIndex = int(self.request.get('offset'))
        else:
            offsetIndex = 0

        if not fromDate:
            fromDate = "01/01/1900"
        someDate = datetime.datetime.strptime(fromDate,"%m/%d/%Y")
        if postid:
            entryID = self.request.get('postid')
            entry = JournalEntry.get(entryID)
            someDate = entry.date
            myEntry = GetSingleEntry(entry, self.user)
        else:
            myEntry = None
        outList = GetEntryList(self.user, someDate, searchTag, offsetIndex)
        if myEntry in outList:
            outList.pop(outList.index(myEntry))
        if myEntry:
            outList.insert(0, myEntry)
        self.response.out.write(json.dumps(outList))

class RequestAttachments(RequestHandler):
    def completeRequest(self):
        fromDate = self.request.get('fromdate')
        searchTag = self.request.get('tag')
        attachmentType = self.request.get('attachmenttype')
        offsetIndex = int(self.request.get('offset'))
        if not fromDate:
            fromDate = "01/01/1900"
        someDate = datetime.datetime.strptime(fromDate,"%m/%d/%Y")
        outList = GetAttachmentList(self.user, someDate, searchTag, attachmentType, offsetIndex)
        self.response.out.write(json.dumps(outList))

class RequestAttachment(RequestHandler):
    def completeRequest(self):
        key = self.request.get('key')
        attachment = Attachment.get(key)
        attachmentDic = GetSingleAttachment(attachment)
        self.response.out.write(json.dumps(attachmentDic))
        
class AddEntry(RequestHandler):
    def completeRequest(self):
        entry = JournalEntry()
        entry.author = self.user
        convertedDate = datetime.datetime.today()
        ancestorList = []
        ancestorList.append(str(self.user.marriage.key()))
        entry.ancestorlist = ancestorList
        entry.put()
        outEntry = GetSingleEntry(entry,self.user)
        self.response.out.write(json.dumps(outEntry))

class AddComment(RequestHandler):
    def completeRequest(self):
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
                newComment.author = self.user
                newComment.content = commentText
                newComment.metaindex = metaIndex
                newComment.put()
                entry.comments.append(newComment.key())
                entry.put()
                self.response.out.write(json.dumps(GetSingleComment(newComment)))

class AddTag(RequestHandler):
	def completeRequest(self):
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

class DeleteTag(RequestHandler):
	def completeRequest(self):
		entryKey = self.request.get('entrykey')
		entryType = self.request.get('entrytype')
		newTag = self.request.get('tag')
		if newTag:
			if entryType=="entry":
				entry = JournalEntry.get(entryKey)
				entry.tags.remove(newTag)
				entry.put()
				if entry.attachmentList:
					for attachmentKey in entry.attachmentList:
						attachment = db.get(attachmentKey)
						attachment.tags.append(newTag)
						attachment.put()
			elif entryType=="attachment":
				entry = Attachment.get(entryKey)
				entry.tags.remove(newTag)
				entry.put()
			self.response.out.write("success")

class AddAttachment(RequestHandler):
    def completeRequest(self):
        entryKey = self.request.get('entrykey')
        attachmentFile = self.request.get('url')
        attachmentType = self.request.get('attachmenttype')
        entry = JournalEntry.get(entryKey)
        if attachmentFile:
            tempAttachment = Attachment()
            tempAttachment.url = attachmentFile
            tempAttachment.author = self.user
            tempAttachment.date = entry.date
            tempAttachment.ancestorlist = entry.ancestorlist
            tempAttachment.tags = entry.tags
            tempAttachment.attachmentType = attachmentType
            tempAttachment.put()
            entry.attachmentList.append(tempAttachment.key())
            entry.put()
            self.response.out.write(str(tempAttachment.key()))

class DeleteAttachment(RequestHandler):
	def completeRequest(self):
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
		
class EditDate(RequestHandler):
	def completeRequest(self):
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

class EditContent(RequestHandler):
	def completeRequest(self):
		entryKey = self.request.get('entrykey')
		newContent = self.request.get('content')
		entry = JournalEntry.get(entryKey)
		if newContent:
			entry.content = newContent
			entry.put()
			self.response.out.write("success")
			
class DeleteEntry(RequestHandler):
	def completeRequest(self):
		entryID = self.request.get('postid')
		entry = JournalEntry.get(entryID)
		entry.deleted = True
		entry.put()
		self.response.out.write("success")

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
        ('/deletetag', DeleteTag),
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
    