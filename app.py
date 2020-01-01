import gspread, os, json, datetime, re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from oauth2client.service_account import ServiceAccountCredentials
from SundaySchoolKid import SundaySchoolKid
from flask import Flask, request

app = Flask(__name__)

groupMeBOT_ID = os.getenv('GROUPME_BOT_ID')



@app.route('/', methods= ['POST'])
def webhook():
    #Grabs a message that was just sent to the group
    data = request.get_json()

    #checks if the message matches the form "Attendance digit"
    callbackRegex = re.compile(r'^Attendance \d+$')
    mo1 = callbackRegex.match(data['text'])

    if data['name'] != 'TestBot' and mo1 != None:
        date = getLastSatDate()
        listOfMissing = getAttendance(date)
        sendAttendance(listOfMissing, date, mo1.group()[-1])
    return "ok", 200



def send_message(msg):
    url = 'https://api.groupme.com/v3/bots/post'

    data = {
            'bot_id' : groupMeBOT_ID,
            'text' : msg
    }

    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()



def getAttendance(saturdayDate):

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']


    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    gc = gspread.authorize(credentials)


    sh = gc.open("Class of 2026 Master")

    wksMaster = sh.worksheet("Master List")
    wksAttend = sh.worksheet("Attendance")

    maxNum = len(wksMaster.col_values(1))-1

    kidFirstNames = wksMaster.col_values(2)[1:maxNum+1]
    kidLastNames = wksMaster.col_values(3)[1:maxNum+1]
    kidDad_num = wksMaster.col_values(10)[1:maxNum+1]
    kidMom_num = wksMaster.col_values(12)[1:maxNum+1]
    kidBday = wksMaster.col_values(8)[1:maxNum+1]
    kidAddress = [addr+' '+town for (addr,town) in zip(wksMaster.col_values(14)[1:maxNum+1], wksMaster.col_values(15)[1:maxNum+1])]


    kidNames = [(kidFirstNames[i], kidLastNames[i]) for i in range(0,maxNum) ]


    attendaceColumn = wksAttend.find(saturdayDate).col

    attendaceTotalInfo = wksAttend.col_values(attendaceColumn)
    attendace = attendaceTotalInfo[2:maxNum+2]
    numAttended = attendaceTotalInfo[2]

    SundaySchoolKid_data = []

    for (name, dad_Num, mom_Num, address, bday, attended) in zip(kidNames, kidDad_num, kidMom_num, kidAddress, kidBday, attendace):
        child = SundaySchoolKid(name, dad_Num, mom_Num, address, bday, attended)
        SundaySchoolKid_data.append(child)

    missingKidsThisWeek = [missing for missing in SundaySchoolKid_data if missing.attended == 'FALSE']

    return missingKidsThisWeek

def getLastSatDate():
    today = datetime.date.today()
    ## strftime is a method that formats datetime object into nice string more info here https://www.programiz.com/python-programming/datetime/strftime
    ##I use the nonzero padded month and day
    satString = today.strftime("%-m/%-d/%Y")
    if today.weekday() == 5:
        return satString
    else:
        idx = (today.weekday() + 1) % 7
        sat = today - datetime.timedelta(7+idx-6)
        satString = sat.strftime("%-m/%-d/%Y")
        return satString



def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

def sendAttendance(missingKidsThisWeek, saturdayDate, splitSize):
    splitCalls = chunkIt(missingKidsThisWeek, splitSize)

    i = 1
    for list in splitCalls:
        payload = 'Group {}\n'.format(i)
        i = i+1
        for missingChild in list:
            payload = payload + missingChild.name[0]+' '+missingChild.name[1]+' ,'  + 'Dad #: ' + str(missingChild.dadNum)+' ' + 'Mom #: ' + str(missingChild.momNum)+ '\n\n'
        send_message(payload)

