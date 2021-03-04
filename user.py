### DISTRIBUTED SYSTEMS | Assignment 1 ### Anette Sarivuo | 0544022 ###

# USER OBJECT FILE

class User:  
    def __init__(self, nickname, channel):  
        self.nickname = nickname  
        self.channel = channel
        
    def switchChannel(self, newChannel):
        self.channel = newChannel
