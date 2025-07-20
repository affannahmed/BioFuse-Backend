from . import db

class AccessControl(db.Model):
    __tablename__ = 'AccessControl'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('UserDepartment.id', ondelete='CASCADE'), nullable=False)  # Foreign key to UserDepartment
    subsection_id = db.Column(db.Integer, db.ForeignKey('DepartmentSection.id', ondelete='CASCADE'), nullable=False)  # Foreign key to DepartmentSection

    employee = db.relationship('UserDepartment', foreign_keys=[employee_id], backref=db.backref('access_controls', cascade='all, delete'))  # Relationship to UserDepartment for employee
    subsection = db.relationship('DepartmentSection', backref=db.backref('access_controls', cascade='all, delete'))  # Relationship to DepartmentSection

    def __init__(self, employee_id, subsection_id):
        self.employee_id = employee_id
        self.subsection_id = subsection_id

    def __repr__(self):
        return f'<AccessControl employee_id={self.employee_id}, subsection_id={self.subsection_id}>'
