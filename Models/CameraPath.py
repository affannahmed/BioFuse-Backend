from . import db

class CameraPath(db.Model):
    __tablename__ = 'CameraPath'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    camera_path = db.Column(db.Integer, db.ForeignKey('Path.id', ondelete='CASCADE'), nullable=False)  # Foreign key to Path for camera_path
    camera_id = db.Column(db.Integer, db.ForeignKey('Camera.id', ondelete='CASCADE'), nullable=False)  # Foreign key to Camera
    sequence = db.Column(db.Integer, nullable=False)  # Sequence of the camera in the path

    camera = db.relationship('Camera', backref=db.backref('camera_paths', cascade='all, delete'))  # Relationship to Camera
    path = db.relationship('Path', backref=db.backref('camera_paths', cascade='all, delete'))  # Relationship to Path

    def __init__(self, camera_path, camera_id, sequence):
        self.camera_path = camera_path
        self.camera_id = camera_id
        self.sequence = sequence

    def __repr__(self):
        return f'<CameraPath id={self.id}, camera_path={self.camera_path}, camera_id={self.camera_id}, sequence={self.sequence}>'
