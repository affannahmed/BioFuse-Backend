from . import db

class Department(db.Model):
    __tablename__ = 'Department'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    name = db.Column(db.String(40), nullable=False, unique=True)  # Unique department name

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Department {self.name}>'
