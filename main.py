from survey import app, db
from survey.models import User, Image, Photoshopper, Preference

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Image': Image, 'Photoshopper': Photoshopper, 'Preference': Preference}
