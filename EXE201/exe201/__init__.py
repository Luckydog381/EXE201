from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

'''
from pyngrok import ngrok

# Open a HTTP tunnel on the default port 80
# <NgrokTunnel: "http://<public_sub>.ngrok.io" -> "http://localhost:80">
http_tunnel = ngrok.connect()
# Open a SSH tunnel
# <NgrokTunnel: "tcp://0.tcp.ngrok.io:12345" -> "localhost:22">
ssh_tunnel = ngrok.connect(22, "tcp")
'''

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'b792e5cc62b978eb7e9052dc'
app.config['UPLOAD_FOLDER'] = '/static'
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

from exe201 import routes
from exe201 import error_handlers