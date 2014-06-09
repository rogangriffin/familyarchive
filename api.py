from google.appengine.ext import webapp
from dbModels import *

class PostAttachmentEntry(webapp.RequestHandler):
	def post(self):
		userkey = self.request.get('apikey')
		attachmentFile = self.request.get('attachmentfile')
		attachmentType = self.request.get('attachmenttype')
		myPerson = Person.get(userkey)
		entry = JournalEntry()
		entry.author = myPerson
		ancestorList = []
		ancestorList.append(str(myPerson.marriage.key()))
		entry.ancestorlist = ancestorList
		if attachmentFile:
			tempAttachment = Attachment()
			tempAttachment.filename = attachmentFile
			tempAttachment.author = myPerson
			tempAttachment.ancestorlist = ancestorList
			tempAttachment.attachmentType = attachmentType
			tempAttachment.put()
			entry.attachmentList.append(tempAttachment.key())
			entry.put()
			self.response.out.write("added")
