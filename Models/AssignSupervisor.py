from . import db

class AssignSupervisor(db.Model):
    __tablename__ = 'AssignSupervisor'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    supervisor_id = db.Column(db.Integer, db.ForeignKey('UserDepartment.id', ondelete='CASCADE'), nullable=False)  # Foreign key to UserDepartment
    department_id = db.Column(db.Integer, db.ForeignKey('Department.id', ondelete='CASCADE'), nullable=False)  # Foreign key to Department

    supervisor = db.relationship('UserDepartment', backref=db.backref('supervised_departments', cascade='all, delete'))  # Relationship to UserDepartment
    department = db.relationship('Department', backref=db.backref('supervisors', cascade='all, delete'))  # Relationship to Department

    def __init__(self, supervisor_id, department_id):
        self.supervisor_id = supervisor_id
        self.department_id = department_id

    def __repr__(self):
        return f'<AssignSupervisor supervisor_id={self.supervisor_id}, department_id={self.department_id}>'
