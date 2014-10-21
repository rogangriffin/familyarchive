from google.appengine.ext import webapp
from google.appengine.ext import db
from dbModels import *

class RequestHandler(webapp.RequestHandler):
    def get(self):
        self.processRequest()

    def post(self):
        self.processRequest()

    def processRequest(self):
        self.user = False
        userid = self.request.get('userid')
        query = db.GqlQuery("SELECT * FROM Person WHERE userid = :1", userid)
        totalRows = query.count()
        if(totalRows):
            self.user = query.fetch(1)[0]
            self.completeRequest()
        else:
            self.error(501)

def GetAncestorMarriages(marriage):
    outMarriages = []
    outMarriages.append(marriage)
    q = Person.all()
    q.filter("marriage =", marriage)
    for p in q.run(limit=4):
        if p.parentmarriage:
            outMarriages += GetAncestorMarriages(p.parentmarriage)
    return outMarriages

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

class AddAncestor(RequestHandler):
    def completeRequest(self):
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

class RemoveAncestor(RequestHandler):
    def completeRequest(self):
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

class SendEmail(RequestHandler):
    def completeRequest(self):
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
        senderEmail = str(self.user.username)
        if not "@" in senderEmail:
            senderEmail = senderEmail + "@gmail.com"
        message = mail.EmailMessage(sender=self.user.fullname + " <" + senderEmail + ">", subject=entryTitle)
        message.to = ", ".join(personList)
        message.body = entryTitle + "\n\n" + entryContent + "\n\nGo to http://myfamilyrecord.appspot.com/?postid=" + entryID + " to view the pictures"
        message.html = outHTML
        message.send()

        self.response.out.write("Emails sent to: " + ", ".join(personList))

class CreateRogan(webapp.RequestHandler):
    def get(self):
        createPerson = Person()
        createPerson.fullname = "Rogan Griffin"
        createPerson.inviteid = "rogan"
        myMarriage = Marriage()
        myMarriage.put()
        createPerson.marriage = myMarriage
        createPerson.put()
        self.response.out.write("Invitation: rogan")

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

class InvitePerson(RequestHandler):
    def completeRequest(self):
        invite = self.request.get('invite')
        email = self.request.get('email')
        fullname = self.request.get('fullname')

        createPerson = Person()
        createPerson.fullname = fullname
        createPerson.inviteid = invite
        myMarriage = Marriage()
        myMarriage.put()
        createPerson.marriage = myMarriage
        createPerson.put()

        msgBody = "You have been invited to view family home videos on My Family Record.\n"
        msgBody += "Just click on the following link to activate your account: http://localhost:8080/?invite=" + invite
        msgBody += "\n"
        mail.send_mail(sender="rogangriffin@gmail.com", to="rogangriffin@gmail.com", subject="Family Record Invitation", body=msgBody)
        self.response.out.write(msgBody)

class SignupPerson(webapp.RequestHandler):
    def post(self):
        invite = self.request.get('invite')
        email = self.request.get('email')
        userid = self.request.get('userid')

        query = db.GqlQuery("SELECT * FROM Person WHERE inviteid = :1", invite)
        inviteperson = query.fetch(1)[0]

        inviteperson.email = email
        inviteperson.userid = userid
        inviteperson.put()

        self.response.out.write("success")

class SetEmail(RequestHandler):
    def completeRequest(self):
        email = self.request.get('email')
        self.user.email = email
        self.user.put()
        self.response.out.write("Set user: " + self.user.fullname + "'s email to: " + self.user.email)
