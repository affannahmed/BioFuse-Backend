from . import db

class User(db.Model):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    name = db.Column(db.String(100), nullable=False)  # Name is required
    email = db.Column(db.String(100), nullable=True, unique=True)  # Email can be null and must be unique if provided
    password = db.Column(db.String(255), nullable=True)  # Password can be null
    profile_img = db.Column(db.String(500), nullable=True)  # Profile image can be null
    cnic = db.Column(db.String(18), nullable=True)  # CNIC is and must be unique
    contact = db.Column(db.String(15), nullable=False)  # Contact is required

    def __init__(self, name, cnic, contact, email=None, password=None, profile_img=None):
        self.name = name
        self.cnic = cnic
        self.contact = contact
        self.email = email
        self.password = password
        self.profile_img = profile_img

    def __repr__(self):
        return f'<User {self.name}>'
