#Flask Login
[Flask-login](https://flask-login.readthedocs.io/en/latest/)

##Flask Login(Server side)

###what does this technology accomplish for you ?
    
This library helps us to manager the users who logged in. We are able to create a
user with User class to 
```
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
```    