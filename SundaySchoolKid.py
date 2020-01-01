class SundaySchoolKid:

    def __init__(self, kidName, dadNumber, momNumber, address, bday, attended):
        self.name = kidName
        self.dadNum = dadNumber
        self.momNum = momNumber
        self.address = address
        self.birth_day = bday
        self.attended = attended

    def __str__(self):
        return str(self.name)+'Dad Number:'+str(self.dadNum)+'Mom Number:'+ str(self.momNum)+ 'Address:' + str(self.address)+ 'Birthday:'+str(self.birth_day)+'Attended this Saturday:'+self.attended

    def __rep__(self):
        __str__(self)
