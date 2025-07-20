from . import db

class Location(db.Model):
    __tablename__ = 'Location'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    name = db.Column(db.String(100), nullable=False, unique=True)  # Unique location name

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Location id={self.id}, name={self.name}>'
