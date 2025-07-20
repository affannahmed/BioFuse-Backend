from . import db

class EmployeeDesignation(db.Model):
    __tablename__ = 'EmployeeDesignation'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    user_id = db.Column(db.Integer, db.ForeignKey('UserDepartment.id', ondelete='CASCADE'), nullable=False)  # Foreign key to UserDepartment
    designation_id = db.Column(db.Integer, db.ForeignKey('Designation.id', ondelete='CASCADE'), nullable=False)  # Foreign key to Designation

    user_department = db.relationship('UserDepartment', backref=db.backref('designations', cascade='all, delete'))  # Relationship to UserDepartment
    designation = db.relationship('Designation', backref=db.backref('employees', cascade='all, delete'))  # Relationship to Designation

    def __init__(self, user_id, designation_id):
        self.user_id = user_id
        self.designation_id = designation_id

    def __repr__(self):
        return f'<EmployeeDesignation user_id={self.user_id}, designation_id={self.designation_id}>'
