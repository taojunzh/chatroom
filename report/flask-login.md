# Flask Login
[Flask-login](https://flask-login.readthedocs.io/en/latest/)

## Flask Login(Server side)

### what does this technology accomplish for you ?
    
This library helps us to manager the users who logged in. We are able to create a
user with User class to create a user object. Thus, we can use this user object to 
check if the user is authenticated, logined and logout the user.

### How does this technology accomplish what it does?

```
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
```    
The above code is to configurate the flask application to work with flask login
source code: [Login-manager](https://flask-login.readthedocs.io/en/latest/_modules/flask_login/login_manager.html#LoginManager)
This login-manager is an instance that holds the setting for logged in. It will bind
to the application by calling .init_app(app)
The login_manager.login_view works when a user access the [login_required](https://flask-login.readthedocs.io/en/latest/#flask_login.login_required)
view without begin logged in or authenticated. The user will redirect to the path login

``` 
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
``` 
source:[user loader](https://flask-login.readthedocs.io/en/latest/_modules/flask_login/login_manager.html#LoginManager.user_loader)
``` 
login_user(user)
``` 
source:[login_user](https://flask-login.readthedocs.io/en/latest/_modules/flask_login/utils.html#login_user)
The login_user function takes a User class and it has three properties like below. Once a user is logged in
by this function, we are able to use current_user which is a proxy that monitors current user. For example,
we called current_user.display will obtain the display name of the current user.
``` 
class User:
    def __init__(self,display,username,password):
        self.username = username
        self.display = display
        self.password = password

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    def get_id(self):
        return self.username
``` 
In order to use the login functionality, we need to parse a User class to login_user
function from flask-login. This User class need to have above properties: is_authenticated(),
is_active() and get_id(). Having is_authenticated function make sure the users who is authenticated can be recognized 
by the [login_required](https://flask-login.readthedocs.io/en/latest/_modules/flask_login/utils.html#login_required) 
which is a function to verify if a user is logged in. Thus, if a user wants to log
out, it needs to fulfill login_required first.

``` 
@app.route("/logout/")
@login_required
def logout():
    # Online_Users.remove(current_user.display)
    del Online_Users[current_user.display]

    # socketio.emit("user logout", Online_Users)
    logout_user()
    return redirect(url_for('index'))
``` 
On above code, we called [logout_user()](https://flask-login.readthedocs.io/en/latest/_modules/flask_login/utils.html#logout_user)
so we can remove the user and clean the remember me cookie if it exists. This logout_user function pop out
any id exist in the session and remove the remember me cookie in the request.cookie. It sends the updated user information
to the login manager so it can update users in the application.

### What license(s) or terms of service apply to this technology?
Copyright (c) 2011 Matthew Frazier

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The license is [MIT](https://github.com/maxcountryman/flask-login/blob/main/LICENSE) so we are able to read,write, modify the code for free and
we can also use this technology for commercial purpose.