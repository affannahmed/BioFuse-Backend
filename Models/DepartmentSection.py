from . import db  # Ensure that you have imported your SQLAlchemy instance

class DepartmentSection(db.Model):
    __tablename__ = 'DepartmentSection'  # Matches table name in DB

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('Department.id', ondelete='CASCADE'), nullable=True)
    camera_id = db.Column(db.Integer, db.ForeignKey('Camera.id'))  # ✅ New foreign key, nullable by default

    department = db.relationship('Department', backref=db.backref('sections', cascade='all, delete'))

    def __init__(self, name, department_id=None, camera_id=None):
        self.name = name
        self.department_id = department_id
        self.camera_id = camera_id

    def __repr__(self):
        return f'<DepartmentSection {self.name}>'
