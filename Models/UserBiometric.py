from . import db

class UserBiometric(db.Model):
    __tablename__ = 'UserBiometric'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    user_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'), nullable=False)  # Foreign key to User
    review_id = db.Column(db.Integer, db.ForeignKey('UserDepartment.id', ondelete='SET NULL'), nullable=True)  # Foreign key to UserDepartment
    biometric_type = db.Column(db.String(50), nullable=False)  # Type of biometric
    biometric_path = db.Column(db.String(500), nullable=False)  # Path to biometric data
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')  # Status of the biometric

    user = db.relationship('User', backref=db.backref('biometrics', cascade='all, delete'))  # Relationship to User
    reviewer = db.relationship('UserDepartment', backref=db.backref('reviewed_biometrics', cascade='all, delete'))  # Relationship to UserDepartment

    def __init__(self, user_id, biometric_type, biometric_path, review_id=None, status='pending'):
        self.user_id = user_id
        self.biometric_type = biometric_type
        self.biometric_path = biometric_path
        self.review_id = review_id
        self.status = status

    def __repr__(self):
        return f'<UserBiometric user_id={self.user_id}, biometric_type={self.biometric_type}, status={self.status}>'
