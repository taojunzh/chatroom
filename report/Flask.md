# Flask - A backend framework for building web application in Python
flask is the main framework we implement in our project and it handles most of interaction in our project.

[Flask Documentation](https://flask.palletsprojects.com/en/1.1.x/)

[Flask Source](https://github.com/pallets/flask/)


**What does Flask accomplish for us?**

We are using Flask in our test.mongo.py

Flask initialization

```
from flask import Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
```
The code above is for Flask to receive the name we gave and begin
to find resources. 

Flask Routing
```
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatroom')
def chatroom():
    return render_template('chatroom.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template('login.html')
```

The flask routing helps to keep track of request path. From the code above,
if the path is / which is the root path, it will call def index() function.

Flask render_template
```
test_mongo.py
def register():
    
    message= "User or displayname existed"
    return render_template('register.html', msg = message)

chatroom.html
<h2>{{msg}}</h2>
```
The render_template are able to accomplish a lot of things for us 
We are able to respond the users' request with the html and we are able 
to incorporate jinja experssion.

Flask url_for

This attribute helps to redirect to another path

**License**

Copyright 2010 Pallets

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.