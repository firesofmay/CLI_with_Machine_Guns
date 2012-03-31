import cmd2
import mechanize
import re
import webbrowser
import hashlib
import time
import string
import random

class ExploreSite(cmd2.Cmd):

    "\tAllows the user to explore the site in a loop"

    prompt = '>>> '
    #intro = "\tAllows you to explore a website and write a test script.\n\tUse Tab to see the commands. Auto Completion is Enabled. If not sure do \n\t>>> help <command>.\n\n"

    #Browser Object
    br = mechanize.Browser()
    
    #HTML Data for current site
    data = ""

    #Links in that page
    link = {}

    #Current URL
    url = ""
    base_url = ""

    def init(self):

        """ Initialize the br Object"""

        self.base_url = self.url
        self.br.set_handle_robots(False)
        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686; rv:6.0) Gecko/20100101 Firefox/6.0')]

        #This is to set the CSRF Token. Need to figure out a better way of setting CSRF Later.
        if 'https://dev2.learningu.org' in self.url:
            self.br.open('https://dev2.learningu.org/set_csrf_token')

    def open_link(self, url=""):

        if url == "":
            url = self.url

        try:
            resp = self.br.open(url)
            self.data = resp.read()
            print "Page Title : " + self.br.title()

        except:
            print "Invalid URL."

        self.update_links()

    def do_start(self, url):
    
        """\tTakes the URL of the website as input and fetches that page. Takes a default if not given.\n\t>>> start http://www.example.com\n"""

        if not url:
            print "Taking Default URL : https://dev2.learningu.org/\n"
            self.url = 'https://dev2.learningu.org/'

        else:
            self.url = url

        self.init()

        self.open_link()

    def update_links(self):

        """\tUpdates the Links dictionary of the current URL\n"""

        self.link = {}

        for l in self.br.links():
                    
            if l.text != "[IMG]":
                self.link[re.sub(' ', '_', l.text)]=l.url


    def do_show(self, line):

        """\tShows the HTML Data of the current URL\n\t>>> show\n"""

        if self.data:
            print self.data + "\n"
        else:
            print "Data is empty\n"

    def do_click(self, line):

        """\tFollows the Given Link.\n\t>>> click Text_Of_Link\n"""

        if line:

                print "URL : " + self.link[line] + "\n"
                print "Text : " + line + "\n"

                self.url = self.base_url + self.link[line]
                
                print self.url + "\n"

                self.open_link()


        else:
            for f in self.link:
                print f
    

    
    def complete_click(self, text, line, begidx, endidx):

        """\tAuto Completes the click command and shows all the Links it can click on.\n"""

        if not text:
            completions = self.link.keys()
        else:
            completions = [ f
                            for f in self.link.keys()
                            if f.lower().startswith(text.lower())
                            ]
        return completions

    def do_select_form(self, line):

        """\tShows the current page forms name. Passing the name of the form selects the form.\n\t>>> select_form\n\t>>> select_form formname1\n"""

        if line:
            self.br.select_form(name=line)
            print "Form Selected : " + line + "\n"

        else:
            for f in self.br.forms():
                print f.name

        print "\n"

    def complete_select_form(self, text, line, begidx, endidx):

        """\tAuto Completes the select_form command"""

        if not text:
            completions = [f.name for f in self.br.forms()]

        else:
            completions = [ f.name
                            for f in self.br.forms()
                            if f.name.lower().startswith(text.lower())
                            ]
        return completions

    def do_controls_show(self, line):

        """\tShows the currently selected forms attributes \n\t>>> select_controls_show\n"""

        try:
            for control in self.br.form.controls:
                print control.name

        except AttributeError:
            print "Select form first. Use \n\t>>> select_form formName"

    def do_controls_set(self, line):

        """\tSets the values of the form and submits.\n\t>>> controls_set\n"""

        filler = FormFiller()

        try:

            for control in self.br.form.controls:
    
                filler.id_generator(self.br, control)    
        except AttributeError:
            print "Select form first. Use \n\t>>> select_form formName. Returning." + "\n"
            return
        
        
        if self.br.form.name == 'newuser_form' or 'loginform':
            control = self.br.form.new_control('text', 'csrfmiddlewaretoken', {})
            cj = self.br._ua_handlers['_cookies'].cookiejar
            self.br['csrfmiddlewaretoken'] = cj._cookies.values()[0]['/']['csrftoken'].value

        for control in self.br.form.controls:            
            print control


        resp = self.br.submit()
        self.data = resp.read()

        print "Submitted"
        print "Title of the Current Page : " + self.br.title()

        self.update_links()        

    def do_back(self, line):

        self.br.back()
        self.update_links()        

    def do_EOF(self, line):
        return True

    def do_open_current_url(self, line):
        
        """\tStores the current URL's data in to the current directory of the script and saves it as debug.html.\n\tOpens it in your default browser for debugging.\n\t>>>> open_current_url\n"""

        print "Storing Debug.html in current directory"
        f = open("Debug.html", 'w')
        f.write(self.data)
        f.close()

        print "Opening the html file in your browser" + "\n"
        webbrowser.open("Debug.html")

    def do_quit (self, arg):

        """\tQuits the program\n"""

        print "\tYou are awesome! Cya Soon!\n"
        return True

###########################################################################

class FormFiller():
    
    def __init__(self):
        self.password = ""
    
    def randomValue(self, size=20, concat_str="Test"):
        chars = string.ascii_uppercase + string.digits    
        hash = hashlib.sha1()
        hash.update(str(time.time()))
            
        return concat_str + hash.hexdigest()[:5] +''.join(random.choice(chars) for x in range(size-9))


    def id_generator(self, br, control, size=20):
        
        if control.type == 'text' and control.name == 'email':
        
            br.form[control.name] = self.randomValue() + "@test.com"


        elif control.type == 'text' and (control.name == 'first_name' or control.name == 'last_name' or control.name == 'username'):
        
            br.form[control.name] = self.randomValue()
        
        elif control.type == 'password':

            if self.password == "":
                self.password = self.randomValue()
    
                br.form[control.name] = self.password

            else:
                br.form[control.name] = self.password
    
        elif control.type == 'select':

            #following filter removes all the blank values, if available
            val = filter(None, control.possible_items())
    
            #As of now the selection is random. Can be done on basis of some probability values. Need to Fix it for later. Check probability.py
            index = random.randrange(len(val))
            temp_list = [val[index]]
            br.form[control.name] = temp_list


        elif control.type == 'submit':
            pass

        else:
            #Fix This
            print "No match found for control.type!!! Exiting"
            exit(1)


###########################################################################

if __name__ == '__main__':
    ExploreSite().cmdloop()
