
from . import db

class Camera(db.Model):
    __tablename__ = 'Camera'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key with auto-increment
    camera_model = db.Column(db.String(50), nullable=False)  # Camera model name
    location_id = db.Column(db.Integer, db.ForeignKey('Location.id', ondelete='CASCADE'), nullable=True)  # Foreign key to Location

    location = db.relationship('Location', backref=db.backref('cameras', cascade='all, delete'))  # Relationship to Location

    def __init__(self, camera_model, location_id=None):
        self.camera_model = camera_model
        self.location_id = location_id

    def __repr__(self):
        return f'<Camera id={self.id}, model={self.camera_model}, location_id={self.location_id}>'
