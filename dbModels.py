from google.appengine.ext import db

class Marriage(db.Model):
	pass

class Person(db.Model):
    username = db.UserProperty()
    fullname = db.StringProperty()
    marriage = db.ReferenceProperty(Marriage, collection_name="mymarriage")
    parentmarriage = db.ReferenceProperty(Marriage, collection_name="parentmarriage")
    email = db.StringProperty()

class Comment(db.Model):
	author = db.ReferenceProperty(Person)
	adddate = db.DateTimeProperty(auto_now_add=True)
	content = db.TextProperty()
	metaindex = db.IntegerProperty()

class Attachment(db.Model):
	filename = db.StringProperty()
	attachmentType = db.StringProperty()
	author = db.ReferenceProperty(Person)
	ancestorlist = db.StringListProperty()
	date = db.DateTimeProperty(auto_now_add=True)
	deleted = db.BooleanProperty(default=False)
	tags = db.StringListProperty()
	comments = db.ListProperty(db.Key)

class JournalEntry(db.Model):
	author = db.ReferenceProperty(Person)
	ancestorlist = db.StringListProperty()
	content = db.TextProperty()
	attachmentList = db.ListProperty(db.Key)
	date = db.DateTimeProperty(auto_now_add=True)
	adddate = db.DateTimeProperty(auto_now_add=True)
	deleted = db.BooleanProperty(default=False)
	tags = db.StringListProperty()
	comments = db.ListProperty(db.Key)
