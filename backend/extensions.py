from flask_sqlalchemy import SQLAlchemy

# Keep extension instances in a dedicated module so all imports share one object.
db = SQLAlchemy()
