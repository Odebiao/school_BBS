# 解决循环引用问题
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
mail = Mail()
db = SQLAlchemy()