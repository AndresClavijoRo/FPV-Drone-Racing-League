import enum
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """Users table."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True, nullable=False)
    hashed_password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    tasks = db.relationship("Task", backref="created_by", lazy=True)


class FileValidFormats(enum.Enum):
    """File valid formats."""
    MP4 = "mp4"

    @classmethod
    def is_valid_format( cls,extension: str) -> bool:
        """Check if the extension is valid."""
        return extension in [a.value for a in cls]

class TaskStatus(enum.Enum):
    """Task status."""
    UPLOADED = "uploaded"
    PROCESSED = "processed"


class Task(db.Model):
    """Tasks table."""
    id = db.Column(db.Integer, primary_key=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    file_name = db.Column(db.String, nullable=False)
    video_path = db.Column(db.String, nullable=False)
    processed_video_path = db.Column(db.String, nullable=True)
    status = db.Column(db.Enum(TaskStatus), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    processing_started_at = db.Column(db.DateTime, nullable=True)
    processing_ended_at = db.Column(db.DateTime, nullable=True)

