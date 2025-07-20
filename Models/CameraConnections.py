from . import db

class CameraConnections(db.Model):
    __tablename__ = 'CameraConnections'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    camera_id_1 = db.Column(db.Integer, db.ForeignKey('Camera.id', ondelete='CASCADE'), nullable=False)  # Foreign key to Camera
    camera_id_2 = db.Column(db.Integer, db.ForeignKey('Camera.id', ondelete='CASCADE'), nullable=False)  # Foreign key to Camera
    delay = db.Column(db.Integer, nullable=True)  # Delay in milliseconds or appropriate unit

    camera_1 = db.relationship('Camera', foreign_keys=[camera_id_1], backref=db.backref('connections_from', cascade='all, delete'))  # Relationship for camera_id_1
    camera_2 = db.relationship('Camera', foreign_keys=[camera_id_2], backref=db.backref('connections_to', cascade='all, delete'))  # Relationship for camera_id_2

    def __init__(self, camera_id_1, camera_id_2, delay=None):
        self.camera_id_1 = camera_id_1
        self.camera_id_2 = camera_id_2
        self.delay = delay

    def __repr__(self):
        return f'<CameraConnections id={self.id}, camera_id_1={self.camera_id_1}, camera_id_2={self.camera_id_2}, delay={self.delay}>'
