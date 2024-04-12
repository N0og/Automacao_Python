class BrowserNotFoundError(Exception):
    def __init__(self, message):
        self.message = message

class BadConection(Exception):
    def __init__(self, message):
        self.message = message

class UserOrPasswordWrong(Exception):
    def __init__(self, message):
        self.message = message

class DriverInterrupted(Exception):
    def __init__(self, message):
        self.message = message

class UnauthorizedXML(Exception):
    def __init__(self, message):
        self.message = message