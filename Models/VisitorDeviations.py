from . import db


class VisitorDeviations(db.Model):
    __tablename__ = 'VisitorDeviations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    visitor_id = db.Column(db.Integer, db.ForeignKey('UserDepartment.id'), nullable=False)
    deviated_camera_id = db.Column(db.Integer, db.ForeignKey('Camera.id'), nullable=False)

    last_location = db.Column(db.String(255))
    destination = db.Column(db.String(100))

    date_time = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    visitor = db.relationship('UserDepartment', backref='visitor_deviations')
    deviated_camera = db.relationship('Camera', backref='deviation_records')

    def __init__(self, visitor_id, deviated_camera_id, last_location=None, destination=None):
        self.visitor_id = visitor_id
        self.deviated_camera_id = deviated_camera_id
        self.last_location = last_location
        self.destination = destination
