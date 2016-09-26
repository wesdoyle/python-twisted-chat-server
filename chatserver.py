from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from clint.textui import colored
import sys

port = 8000


class ChatProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.name = None
        self.state = "REGISTER"

    def connectionMade(self):
        banner = ("""
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #### Successfully Connected to the Chat Server ####
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        """)
        
        self.sendLine(banner)
        self.sendLine("Choose a username:")

    def connectionLost(self, reason):
        leftMsg = colored.red('%s has left the channel.' % (self.name,))
        if self.name in self.factory.users:
            del self.factory.users[self.name]
            self.broadcastMessage(leftMsg)
        self.updateSessionInfo(leftMsg)
 
    def lineReceived(self, line):
        if self.state == "REGISTER":
            self.handle_REGISTER(line)
        else:
            self.handle_CHAT(line)

    def handle_REGISTER(self, name):
       if name in self.factory.users:
           self.sendLine("Sorry, %r is taken. Try something else." % name)
           return
       
       welcomeMsg = ('Welcome to the chat, %s.' % (name,))

       joinedMsg = colored.green('%s has joined the chanel.' % (name,))
       self.sendLine(welcomeMsg)
       self.broadcastMessage(joinedMsg)
       self.name = name
       self.factory.users[name] = self
       self.state = "CHAT"
       self.updateSessionInfo(name + ' registered.')
       
       if len(self.factory.users) > 1:
           self.sendLine('Participants in chat: %s ' % (", ".join(self.factory.users)))
       else: 
           self.sendLine("You're the only one here, %r" % name)



    def handle_CHAT(self, message):
       message = "<%s> %s" % (self.name, message)
       self.broadcastMessage(colored.magenta(message))
       self.updateSessionInfo(message)

    # change this to write out chat log for last 100 messages
    # with timestamp, while refreshing the current users in chat
    def broadcastMessage(self, message):
       for name, protocol in self.factory.users.iteritems():
           if protocol != self:
               protocol.sendLine(colored.white(message))
               self.updateSessionInfo(message)

    def updateSessionInfo(self, message):
        print(chr(27) + "[2J")
        print('Users in chat: %s ' % (", ".join(self.factory.users)))
        print('Latest message: %s ' % (message))

class ChatFactory(Factory):
    def __init__(self):
        self.users = {}

    def buildProtocol(self, addr):
        return ChatProtocol(self)

reactor.listenTCP(port, ChatFactory())
print("Chat Server started on port %s" % (port,))
reactor.run()



