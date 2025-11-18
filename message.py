class MessageType:
    TEXT = 1
    IMAGE = 2
    FILE = 3

class Message:
    def __init__(self, msg_type, content):
        self.msg_type = msg_type
        self.content = content
