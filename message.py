class MessageType:
    TEXT = 1
    IMAGE = 2
    FILE = 3

class Message:
    def __init__(self, msg_type, content):
        self.msg_type = msg_type
        self.content = content
context = []

def limit_context_size(context, max_size=5):
    """限制上下文大小"""
    while len(context) > max_size:
        context.pop(0)
        