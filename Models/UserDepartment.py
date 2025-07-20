from . import db

class UserDepartment(db.Model):
    __tablename__ = 'UserDepartment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    user_id = db.Column(db.Integer, db.ForeignKey('User.id', ondelete='CASCADE'), nullable=False)  # Foreign key to User
    department_id = db.Column(db.Integer, db.ForeignKey('Department.id', ondelete='CASCADE'), nullable=False)  # Foreign key to Department
    role_id = db.Column(db.Integer, db.ForeignKey('Role.id', ondelete='CASCADE'), nullable=False)  # Foreign key to Role
    date_assigned = db.Column(db.DateTime, default=db.func.current_timestamp())  # Date assigned, defaults to current timestamp
    is_valid = db.Column(db.Boolean, default=True)  # Indicates if the user currently works in that department

    user = db.relationship('User', backref=db.backref('departments', cascade='all, delete'))  # Relationship to User
    department = db.relationship('Department', backref=db.backref('users', cascade='all, delete'))  # Relationship to Department
    role = db.relationship('Role', backref=db.backref('user_departments', cascade='all, delete'))  # Relationship to Role

    def __init__(self, user_id, department_id, role_id):
        self.user_id = user_id
        self.department_id = department_id
        self.role_id = role_id

    def __repr__(self):
        return f'<UserDepartment user_id={self.user_id}, department_id={self.department_id}, role_id={self.role_id}>'
