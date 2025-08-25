from flask_login import UserMixin

class Administrador(UserMixin):
    def __init__(self, agrupacion, email, psswd):
        self.id = str(agrupacion)
        self.email = email
        self.psswd = psswd

    def get_id(self):
        return self.id