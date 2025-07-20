from . import db

class EmployeeViolations(db.Model):
    __tablename__ = 'EmployeeViolations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('UserDepartment.id', ondelete='CASCADE'), nullable=False)
    camera_id = db.Column(db.Integer, db.ForeignKey('Camera.id', ondelete='CASCADE'), nullable=False)
    violation_time = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    user = db.relationship('UserDepartment', backref='violations')
    camera = db.relationship('Camera', backref=db.backref('employee_violations', cascade='all, delete-orphan', passive_deletes=True))

    def __init__(self, user_id, camera_id):
        self.user_id = user_id
        self.camera_id = camera_id
