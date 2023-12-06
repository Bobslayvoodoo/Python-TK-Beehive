import tkinter as tk
from tkinter import ttk
import os
from datetime import date
import time
import json
import os.path
import requests
import base64

LoginTokenURL = f'https://beehiveapi.lionhearttrust.org.uk/token'
AssignmentsURL = 'f"https://beehiveapi.lionhearttrust.org.uk/v3.5/planner/students/{UID}/assignmentstiny?"'
DetailedAssigmentURL = 'f"https://beehiveapi.lionhearttrust.org.uk/v3.5/planner/users/{UID}/assignments/{AID}"'

proxies = { 'http' : None, 'https' : None }

SelectedButtonColour = "yellow"
UnselectedButtonColour = "light gray"
CompleteColour = "green"
TextColour = "black"

root = tk.Tk()




## login
class CustomSort():
    def SortByDeadline(Items):
        def GetDeadline(item):
            item = item["deadline"]
            Deadline = item.split("T")[0].split("-")
            return date(int(Deadline[0]),int(Deadline[1]),int(Deadline[2]))
        Items.sort(key=GetDeadline)
        return Items

Sorts = [CustomSort.SortByDeadline]


class AssignmentClass():
    def __init__(self,BH,Data):
        self.BH = BH
        self.ID = Data["id"]
        self.Title = Data["title"]
        self.Deadline = Data["deadline"]
        self.SetOn = Data["setOn"]
        self.ReadOn = Data["readOn"]
        self.CompletedOn = Data["completedOn"]
        self.SetBy = Data["setBy"]
        self.Expired = Data["isExpired"]
        self.Read = Data["isRead"]
        self.Complete = Data["isComplete"]
        self.Overdue = Data["isOverdue"]

    def DisplaySelf(self,*args):
        for widget in AssignmentsBigFrame.winfo_children():
            widget.destroy()
        Frame = self.GetFrame()
        if Frame:
            Frame.grid(sticky=tk.EW)
        else:
            print("error")
            
        
        
    def GetFrame(self):
        UID = self.BH.UserId
        AID = self.ID
        URL = eval(DetailedAssigmentURL)
        Headers = {"Authorization":self.BH.Auth}
        try:
            Response = requests.get(URL,headers=Headers,proxies=proxies)
            if Response.status_code < 400:
                ResponseJson = Response.json()
                print(ResponseJson)
        except:
            return 
        MainFrame = ttk.Frame(AssignmentsBigFrame)
        TitleFrame = ttk.Frame(MainFrame)
        TitleFrame.grid(row=0,column=0,sticky=tk.EW)
        TitleLabel = ttk.Label(TitleFrame,text=self.Title)
        TitleLabel.grid(row=0,column=0)
        SubjectLabel = ttk.Label(TitleFrame,text=ResponseJson["groups"][0]["friendlyName"])
        SubjectLabel.grid(row=1,column=0)
        
        InfoFrame = ttk.Frame(MainFrame)
        InfoFrame.grid(row=1,column=0,sticky=tk.EW)
        DeadlineFrame = ttk.Label(InfoFrame)
        DeadlineFrame.grid(row=0,column=0,sticky=tk.EW)
        DeadlineTextLabel = ttk.Label(DeadlineFrame,text="Deadline: ")
        DeadlineTextLabel.grid(row=0,column=0)

        SetByFrame = ttk.Frame(InfoFrame)
        SetByFrame.grid(row=1,column=0,sticky=tk.EW)

        SpacerFrame = ttk.Frame(MainFrame)
        SpacerFrame.grid(row=0,rowspan=10,column=0,columnspan=10,padx=400)

        DetailsFrame = ttk.Frame(MainFrame)
        DetailsFrame.grid(row=2,column=0,sticky=tk.EW)

        DetailTextLabel = ttk.Label(DetailsFrame,text="Description: ")
        DetailTextLabel.grid(row=0,column=0,sticky=tk.N)

        print(MainFrame.winfo_width())
        DescriptionLabel = ttk.Label(DetailsFrame,text=ResponseJson["details"],wraplength=600,justify = "left")
        DescriptionLabel.grid(row=0,column=1)
        
        return MainFrame
        

class Beehive():
    def __init__(self):
        LoginFrame.grid()
        self.CurrentFrame = LoginFrame
        self.AssignmentsFilterCode = 0
        LogInButton.config(command=self.MakeToken)
        self.Token = None
        self.UserId = None
        self.MakeToken()
        self.Auth = "Bearer "+self.Token
        
        
        
        for Button in FilterLabels:
            Button.bind("<Button-1>",self.ChangeFilter)
        
        if self.Token:
            self.RefreshAssignments()


    def GetAssignments(self,SortCode=0,PageIndex=0,FilterCode=0,PageSize=10):
        Parameters = {"pageIndex":PageIndex,
                 "filter":FilterCode,
                 "pageSize":PageSize}
        Headers = {"Authorization":self.Auth}
        UID = self.UserId
        URL = eval(AssignmentsURL)
        try:
            Response = requests.get(URL,params=Parameters,headers=Headers,proxies=proxies)
            if Response.status_code < 400:
                ResponseJson = Response.json()
                SortedAssignments = Sorts[SortCode](ResponseJson["items"])
                return SortedAssignments
        except:
            return []
        return []

    def RefreshAssignments(self):
        self.Assignments = {}
        for Assignment in self.GetAssignments(FilterCode=self.AssignmentsFilterCode):
            self.Assignments[Assignment["id"]] = AssignmentClass(self,Assignment)
        self.DisplayAssignments()

    def ForgetCurrentFrame(self):
        self.CurrentFrame.grid_forget()

    def ChangeFilter(self,Event):
        self.AssignmentsFilterCode = Filters[Event.widget["text"]]
        for Button in FilterLabels:
            Colour = UnselectedButtonColour
            if Button == Event.widget:
                Colour = SelectedButtonColour

            Button["background"] = Colour
        root.update()
        self.RefreshAssignments()
        
    def DisplayAssignments(self):
        self.ForgetCurrentFrame()
        AssignmentsMainFrame.grid()
        for widget in AssignmentsSmallFrame.winfo_children():
            widget.destroy()

        for n,Assignment in enumerate(self.Assignments.values()):
            colour = TextColour
            if Assignment.Complete:
                colour = CompleteColour
            
            NewFrame = ttk.Frame(AssignmentsSmallFrame,borderwidth=2,relief="groove")
            NewFrame.grid(sticky=tk.EW,row=n,pady=2)
            NewFrame.bind("<Button-1>",Assignment.DisplaySelf)
            
            TitleLabel = ttk.Label(NewFrame,text=Assignment.Title,foreground=colour)
            TitleLabel.grid(row=0,column=0,sticky=tk.W)
            TitleLabel.bind("<Button-1>",Assignment.DisplaySelf)

            Teacher = Assignment.SetBy
            TeacherLabel = ttk.Label(NewFrame,text=(Teacher["title"]+" "+ Teacher["lastName"]))
            TeacherLabel.grid(row=1,column=0,sticky=tk.W)
            TeacherLabel.bind("<Button-1>",Assignment.DisplaySelf)

            SpacerFrame = ttk.Frame(NewFrame)
            SpacerFrame.grid(column=0,padx=200)

            DueDate = Assignment.Deadline.split("T")[0]
            DeadlineLabel = ttk.Label(NewFrame,text=DueDate)
            DeadlineLabel.grid(row=0,rowspan=2,column=2,sticky=tk.E,padx=3)
            DeadlineLabel.bind("<Button-1>",Assignment.DisplaySelf)
        

    def GetUserName():
        return EnteredUserName.get()
    
    def GetPassword():
        return EnteredPassword.get()

    def DecodeToken(self):
        Payload = self.Token.split(".")[1]
        Padded = Payload + "="*divmod(len(Payload),4)[1]
        Decoded = json.loads(base64.urlsafe_b64decode(Padded))
        self.UserId = Decoded["id"]

    def MakeToken(self,*args):
        if os.path.exists("Token.txt"):
            with open("Token.txt","r") as file:
                Token, Expiry = file.readline().strip().split("#")
                
            if time.time() <= float(Expiry)-1000:
                self.Token = Token
                self.DecodeToken()
                return
        
        Username = Beehive.GetUserName()
        Password = Beehive.GetPassword()
        data = {"grant_type":"password",
                "username":Username,
                "password":Password,
                "client_id":"web"}
        try:
            Response = requests.post(LoginTokenURL,data=data,proxies=proxies)
            print(Response.json())
            if Response.status_code < 400:
                
                ResponseJson = Response.json()
                with open("Token.txt","w") as file:
                    file.write(ResponseJson["access_token"] + "#" + str(time.time()+ResponseJson["expires_in"]))
                self.Token = ResponseJson["access_token"]
                self.DecodeToken()
                return
            else:
                return
        except:
            return
            

    def SaveToken(Token):
        with open("Token.txt","w") as file:
            file.write(Token)

        



## Login GUI ##
LoginFrame = ttk.LabelFrame(root,text="Login to Beehive")


UserNameLabel = ttk.Label(LoginFrame,text="Username:")
UserNameLabel.grid()

EnteredUserName = tk.StringVar()
UserNameEntry = ttk.Entry(LoginFrame,textvariable=EnteredUserName)
UserNameEntry.grid(row=0,column=1)


PasswordLabel = ttk.Label(LoginFrame,text="Password:")
PasswordLabel.grid(row=1)

EnteredPassword = tk.StringVar()
PasswordEntry = ttk.Entry(LoginFrame,show="*",textvariable=EnteredPassword)
PasswordEntry.grid(row=1,column=1)

LogInButton = ttk.Button(LoginFrame,text="Log in")
LogInButton.grid(row=0,column=2,rowspan=2,sticky=tk.EW)


            
## Assignments GUI ##
AssignmentsMainFrame = ttk.Frame(root)
#AssignmentsMainFrame.grid(sticky=tk.EW)

AssignmentsLeftFrame = ttk.Frame(AssignmentsMainFrame)
AssignmentsLeftFrame.grid(row=0,sticky=tk.N)

AssignmentsFilterFrame = ttk.Frame(AssignmentsLeftFrame)
AssignmentsFilterFrame.grid(row =0,sticky=tk.N)

Filters = {
    "All":0,
    "Current":1,
    "Unread":8,
    "Complete":4,
    "Due Today":5,
    "Due Tomorrow":6,
    "Late":7}

FilterLabels = []

for FilterName,x in Filters.items():
    colour = UnselectedButtonColour
    if x == 0:
        colour = SelectedButtonColour
    NewLabel = ttk.Label(AssignmentsFilterFrame,text=FilterName,borderwidth=2,relief="groove",background=colour)
    FilterLabels.append(NewLabel)
    NewLabel.grid(row=0,column=x,padx=5,ipadx=2,sticky=tk.EW)

AssignmentsCanvas = tk.Canvas(AssignmentsLeftFrame,width=500,height=500)
AssignmentsCanvas.grid(row=1,sticky=tk.N)

SpaceFrame = ttk.Frame(AssignmentsMainFrame)
SpaceFrame.grid(pady=300,row=1,column=0,sticky=tk.S)

AssignmentsSmallFrame = ttk.Frame(AssignmentsCanvas)
AssignmentsSmallFrame.grid(sticky=tk.NSEW)

AssignmentsBigFrame = ttk.Frame(AssignmentsMainFrame,borderwidth=2,relief="groove")
AssignmentsBigFrame.grid(sticky=tk.NSEW,column=1,row=0,rowspan=2,padx=2)
SpaceFrame = ttk.Frame(AssignmentsMainFrame)
SpaceFrame.grid(padx=300,pady=300,row = 0, rowspan=2,column = 1)
########################

Hive = Beehive()
root.mainloop()
