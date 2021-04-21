class User:
    def __init__(self,display,username,password):
        self.username =username
        self.display = display
        self.password = password

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    def get_id(self):
        return self.username