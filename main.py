from survey import set_config, app
from config import Config 
from survey import db

def main():
    set_config(Config)
    
    with app.app_context():
       db.create_all()

    app.run(host='0.0.0.0', port=5300)

if __name__ == "__main__":
    main()

