from survey import app, db
from survey.models import User, Test, TestPreference, Question, Answer

@app.shell_context_processor
def make_shell_context():
   return {'db': db,
           'User': User,
           'Test':Test,
           'TestPreference':TestPreference,
           'Question':Question,
           'Answer':Answer}
