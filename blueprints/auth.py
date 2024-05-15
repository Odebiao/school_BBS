from flask import Blueprint, render_template, redirect, url_for, session
from exts import db,mail
from flask import request
from models import UserModel
from .forms import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
import string,random
from models import EmailCaptchaModel
from datetime import datetime
from flask import  jsonify
# from .forms import RegisterForm, LoginForm, EmailCaptchaForm
bp = Blueprint("auth", __name__, url_prefix='/auth')
from flask import flash



# 默认get请求
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        form = LoginForm(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data
            user = UserModel.query.filter_by(username=username).first()
            if not user:
                print('此邮箱在数据库中不存在')
                return redirect(url_for('auth.login'))
            if check_password_hash(user.password, password):
                # flask中的session，是经过加密后存储在cookie中的
                # 常用于标识登录用户身份
                session['user_id'] = user.id
                return redirect('/')
            else:
                print('密码错误')
                return redirect(url_for('auth.login'))
        else:
            print(form.errors)
            return redirect(url_for('auth.login'))


@bp.route('/captcha', methods=['GET'])
# @bp.route('/auth/captcha/email', methods=['GET'])
def get_captcha():
    # 生成验证码
    email = request.args.get("email")
    letters = string.ascii_letters + string.digits
    captcha = ''.join(random.sample(letters, 4))
    if email:
        message = Message(
            subject="邮箱测试",
            recipients=[email],
            body=f"牛爷爷【测试邮件】您的注册验证码为：{captcha}"
        )
        mail.send(message)
        captcha_model = EmailCaptchaModel.query.filter_by(email=email).first()
        if captcha_model:
            captcha_model.captcha = captcha
            captcha_model.create_time = datetime.now()
            db.session.commit()
        else:
            captcha_model = EmailCaptchaModel(email=email, captcha=captcha)
            db.session.add(captcha_model)
            db.session.commit()
        print("验证码", captcha)
        return jsonify({"code":200,"message":"邮件发送成功"})
    else:
        return jsonify({"code":400,"message":"请先输入邮箱"})


# @bp.route('/mail')
#
# def send_mail():
#     message = Message(
#         subject="邮箱测试",
#         recipients=["485913317@qq.com"],
#         body=f"【邮箱测试】您的验证码为123456"
#     )
#     mail.send(message)
#     return "测试邮件发送成功"

@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# GET：从服务器上获取数据
# POST：将客户端的数据提交给服务器
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        form = RegisterForm(request.form)
        if form.validate():
            username = form.username.data
            password = form.password.data
            user = UserModel(username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        else:
            print(form.errors)
            return redirect(url_for('auth.register'))