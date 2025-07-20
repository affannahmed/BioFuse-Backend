from . import db

class CameraMonitoringLogs(db.Model):
    __tablename__ = 'CameraMonitoringLogs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('UserDepartment.id'), nullable=False)
    camera_id = db.Column(db.Integer, db.ForeignKey('Camera.id', ondelete='CASCADE'), nullable=False)

    date_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    access_img = db.Column(db.String(255), nullable=False)
    destination = db.Column(db.Integer)
    # Relationships
    user = db.relationship('UserDepartment', backref='camera_logs')
    camera = db.relationship('Camera', backref=db.backref('monitoring_logs', cascade='all, delete-orphan', passive_deletes=True))


    def __init__(self, user_id, camera_id, access_img,destination):
        self.user_id = user_id
        self.camera_id = camera_id
        self.access_img = access_img
        self.destination = destination
