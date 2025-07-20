from . import db

class Designation(db.Model):
    __tablename__ = 'Designation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    name = db.Column(db.String(50), nullable=False, unique=True)  # Unique designation name

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Designation {self.name}>'
