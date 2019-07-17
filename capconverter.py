class convert:
    
    def __init__(self, value):
        self.value = value
            
    def bytestoTB(self):
        newvalue = round(self/1099511627776, 2)
        return newvalue