from . import db

class Path(db.Model):
    __tablename__ = 'Path'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source = db.Column(db.Integer, db.ForeignKey('Location.id', ondelete='CASCADE'), nullable=False)
    destination = db.Column(db.Integer, db.ForeignKey('Location.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.Integer, default=1, nullable=False)  # ✅ New column added here

    source_location = db.relationship('Location', foreign_keys=[source], backref=db.backref('paths_from', cascade='all, delete'))
    destination_location = db.relationship('Location', foreign_keys=[destination], backref=db.backref('paths_to', cascade='all, delete'))

    def __init__(self, source, destination, status=1):  # Optionally allow setting status
        self.source = source
        self.destination = destination
        self.status = status

    def __repr__(self):
        return f'<Path id={self.id}, source={self.source}, destination={self.destination}, status={self.status}>'
