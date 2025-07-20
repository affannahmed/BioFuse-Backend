from . import db

class Role(db.Model):
    __tablename__ = 'Role'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Role {self.name}>'
