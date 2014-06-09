from google.appengine.api import users
from dbModels import *

def GetUser(webApp):
    user = users.get_current_user()
    if not user:
        webApp.redirect(users.create_login_url(webApp.request.uri))
    
    #Check for invitation
    invite = webApp.request.get('invite')
    if invite:
        try:
            invitePerson = Person.get(invite)
        except:
            invitePerson = None
        if invitePerson:
            if not invitePerson.username:
                invitePerson.username = user
                invitePerson.put()
        else:
            return False
    
    viewas = webApp.request.get('viewas')
    if viewas:
        userPerson = Person.get(viewas)
    else:
        #Check if the user has a Person entry
        query = db.GqlQuery("SELECT * FROM Person WHERE username = :1", user)
        totalRows = query.count()
        if totalRows<1:
            return False
        userPerson = query.fetch(1)[0]
        
    return userPerson

def GeneratePage(pageType, webApp, postID="", viewas=""):
    userPerson = GetUser(webApp)
    if not userPerson:
        return("<html>\n<body>\nYou do not exist in the system. Ask Rogan for an invitation.<br>\n</body>\n</html>\n")
    
    javascripts = []
    stylesheet = "main.css"
    if pageType=="entries":
        javascripts = ["entryobj.js", "tagobj.js", "main.js"]
    elif pageType=="videos":
        javascripts = ["videos.js"]
        stylesheet = "videos.css"
    
    outHTML = '<html>\n<head>\n<script src="js/prototype.js"></script>\n'
    outHTML += '<script src="js/jsonp.js"></script>\n'
    outHTML += '<script src="js/jquery.js"></script>\n'
    outHTML += '<script src="js/swfobject.js"></script>\n'
    outHTML += '<script src="js/helper.js"></script>\n'
    for javascript in javascripts:
        outHTML += '<script src="js/' + javascript + '"></script>\n'
        
    if postID:
        outHTML += '<script>var postid="' + postID + '"</script>\n'
    else:
        outHTML += '<script>var postid=""</script>\n'
        
    if viewas:
        outHTML += '<script>var viewas="' + viewas + '"</script>\n'
    else:
        outHTML += '<script>var viewas=""</script>\n'

    outHTML += '<link rel="stylesheet" type="text/css" href="stylesheets/' + stylesheet + '" />\n'
    outHTML += '</head>\n'
    outHTML += "<body onload='javascript:BodyLoaded();' onresize='javascript:BodyResize()'>"
    
    outHTML += "<div id='headerdiv' class='headerdiv'>"
    outHTML += "<input size=10 type='text' id='txtSearchDate' value='01/01/1900' />&nbsp;tags:<input size=10 type='text' id='txtSearchTag' value='' /><input type='button' value='Go' onclick='ChangeDate();' class='button' />"
    
    if pageType=="entries":
        outHTML += "<input type='button' value='Add Entry' onclick='javascript:AddEntry();' class='button' style='float:right;' />"
    
    outHTML += "</div>"
    outHTML += "<div id='containerdiv' class='containerdiv' onscroll='OnContainerScroll()'></div>"
    
    if pageType=="entries":
        outHTML += GenerateMarriageKeys(userPerson)
        
        #Delete Form
        outHTML += """
                    <form action="/delete" method="post" name='frmDelete'>
                    <input type='hidden' id='frmdelete_postid' name='postid' />
                    </form>"""
    
    outHTML += "</body>\n</html>\n"
    	
    return outHTML

def GenerateMarriageKeys(userPerson):
    #Marriage Keys
    outHTML = """
    <script>
    	var UserAncestors = [];
    		"""
    spousePerson = None
    userMarriage = userPerson.marriage
    for marriagePeople in userMarriage.mymarriage:
        if marriagePeople.key() != userPerson.key():
            spousePerson = marriagePeople
    parentMarriage = userPerson.parentmarriage
    if parentMarriage:
        outHTML += "AddAncestor('My parents and siblings', '" + str(parentMarriage.key()) + "');\n"
        for marriagePeople in parentMarriage.mymarriage:
            if marriagePeople.parentmarriage:
                parentName = marriagePeople.fullname.split(" ")[-1]
                outHTML += "AddAncestor('" + parentName + " extended family', '" + str(marriagePeople.parentmarriage.key()) + "');\n"
    if spousePerson:
        parentMarriage = spousePerson.parentmarriage
        if parentMarriage:
            spouseName = spousePerson.fullname.split(" ",1)[0]
            outHTML += "AddAncestor('" + spouseName + "\\'s parents and siblings','" + str(parentMarriage.key()) + "');\n"
            for marriagePeople in parentMarriage.mymarriage:
                if marriagePeople.parentmarriage:
                    parentName = marriagePeople.fullname.split(" ")[-1]
                    outHTML += "AddAncestor('" + parentName + " extended family', '" + str(marriagePeople.parentmarriage.key()) + "');\n"
    
    outHTML += "\n</script>\n"
    return outHTML
	
def GenerateCreatePersonPage(webApp):
    GetUser(webApp)
    
    outHTML = '<html>\n<head>\n<script src="js/prototype.js"></script>\n'
    outHTML += '<script src="js/createperson.js"></script>\n'
    outHTML += "<script>\n"
    outHTML += "var personList = ["
    people = db.GqlQuery("SELECT * FROM Person")
    for person in people:
        outHTML += "{'key': '" + str(person.key()) + "', 'name': '" + person.fullname + "'},"
    outHTML = outHTML[:-1]
    outHTML += "];\n"
    outHTML += "</script>\n"
    outHTML += "</head><body onload='javascript:BodyLoaded();'></body></html>\n"
    return outHTML

def GenerateInvitePersonPage(webApp):
    GetUser(webApp)
    outHTML = '<html>\n<head>\n<script src="js/prototype.js"></script>\n'
    outHTML += "<script src='js/jsonp.js'></script>"
    outHTML += "<script>\n"
    outHTML += "var personList = ["
    outHTML += "];\n"
    outHTML += "</script>\n"
    outHTML += "</head><body>\n"
    outHTML += "<form action='/invite' method='post'>\n"
    outHTML += "<table><tr><td>User:"
    outHTML += "<select name='user'>\n"
    people = db.GqlQuery("SELECT * FROM Person WHERE username < ''")
    for person in people:
        outHTML += "<option value='" + str(person.key()) + "'>" + person.fullname + "</option>\n"
    outHTML += "</select></td>\n"
    outHTML += "<td>email:<input type='text' name='email'></input></td>\n"
    outHTML += "<td><input type='submit'></input></td></tr></table>\n"
    outHTML += "</form>\n"
    outHTML += "</body></html>\n"
    return outHTML
	
