# Flask - A backend framework for building web application in Python
flask is the main framework we implement in our project and it handles most of interaction in our project.

[Flask Documentation](https://flask.palletsprojects.com/en/1.1.x/)

[Flask Source](https://github.com/pallets/flask/)


## What does Flask accomplish for us?

We are using Flask in our test.mongo.py

### Flask initialization

```
from flask import Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
```
The code above is for Flask to receive the name we gave and begin
to find resources and generate features such as routing and render template.

### Flask Routing
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

### Flask render_template
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
to incorporate jinja expression.

### Flask url_for
```
<li><a href="{{ url_for('index') }}">Home</a>
```
This attribute helps to direct to a path in our code

### Flask redirect
```
@login_required
def logout():
    # Online_Users.remove(current_user.display)
    del Online_Users[current_user.display]

    # socketio.emit("user logout", Online_Users)
    logout_user()
    return redirect(url_for('index'))
```
Redirect function helps to redirect to a different path

### Flask request
```
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password').encode('utf-8')
        ...
```
The request library from Flask will parse the HTTP request and get the form data for us so we don't have to parse the form by ourself.

## How does this technology accomplish what it does?

### Flask initialization
According to [Object](https://flask.palletsprojects.com/en/1.1.x/api/#application-object),
This is intialization of a Flask instance. What it does is to implement a WSGI
(Web Server Gateaway Interface) application as the central object. The app.config['SecretKey']
is used to keep the data safe. With this Flask instance, it can find resource that handle
the feature like request,route, and render template,etc.

### Flask route
```
def index():
    pass
app.add_url_rule('/', 'index', index)

@app.route('/')
def index():
    pass
```    

The Flask route use the [add_url_rule](https://github.com/pallets/flask/blob/29d33203d0325f006c75fc88359872bd68c8bdf5/src/flask/app.py#L1178) function from Flask.
In this function, it assigns an endpoint to the function and this endpoint will be used for URL generation.

The route() invokes add_url_rule so def index() can be called and run.


### Flask render_template
```    
def render_template(template_name_or_list, **context):
    ctx = _app_ctx_stack.top
    ctx.app.update_template_context(context)
    return _render(
        ctx.app.jinja_env.get_or_select_template(template_name_or_list),
        context,
        ctx.app,
    )
```
[render_template](https://github.com/pallets/flask/blob/29d33203d0325f006c75fc88359872bd68c8bdf5/src/flask/templating.py)

With the existence of Flask instance, we can use render_template. From above code,
the render_template uses jinja environment to render the template. A jinja template is just a text file, with variables and/or expressions, and they can be replaced with values when rendered.

"
The default Jinja delimiters are configured as follows:

{% ... %} for Statements

{{ ... }} for Expressions to print to the template output

{# ... #} for Comments not included in the template output

"
[jinja](https://jinja.palletsprojects.com/en/2.11.x/templates/)

We also use these delimiters in our HTML function to replace variables to values.

### Flask url_for
```
url_for(endpoint, **values)
```
[url_for](https://github.com/pallets/flask/blob/29d33203d0325f006c75fc88359872bd68c8bdf5/src/flask/helpers.py)

This function generates a URL to the given endpoint. It can generate a 'relative' URL if request adaptor is available or it can generate an external URL with appctx adaptor.

### Flask redirect
```
from werkzeug.utils import redirect
```
[flask redirect](https://github.com/pallets/flask/blob/master/src/flask/__init__.py)

Flask uses werkzeug.utils for redirect.

```
def redirect(
    location: str, code: int = 302, Response: t.Optional[t.Type["Response"]] = None
) -> "Response":
    import html

    if Response is None:
        from .wrappers import Response  # type: ignore

    display_location = html.escape(location)
    if isinstance(location, str):
        from .urls import iri_to_uri

        location = iri_to_uri(location, safe_conversion=True)
    response = Response(  # type: ignore
        '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
        "<title>Redirecting...</title>\n"
        "<h1>Redirecting...</h1>\n"
        "<p>You should be redirected automatically to target URL: "
        f'<a href="{html.escape(location)}">{display_location}</a>. If'
        " not click the link.",
        code,
        mimetype="text/html",
    )
    response.headers["Location"] = location
    return response
```
[werkzeug redirect](https://github.com/pallets/werkzeug/blob/master/src/werkzeug/utils.py)

In here, the function writes the redirect response with location as the parameter. The response also includes a temporarily HTML template to display to the user while the page is being redirected. Then, the formatted response is returned and sent.

### Flask request
```
request = LocalProxy(partial(_lookup_req_object, "request"))
```
[request](https://github.com/pallets/flask/blob/29d33203d0325f006c75fc88359872bd68c8bdf5/src/flask/globals.py)

Flask uses wraps Werkzeug in its request. The request is a global variable and it is always the last request received by the server.
```
@cached_property
def form(self) -> "ImmutableMultiDict[str, str]":
    self._load_form_data()
    return self.form

    def _load_form_data(self) -> None:
        if "form" in self.__dict__:
            return

        if self.want_form_data_parsed:
            parser = self.make_form_data_parser()
            data = parser.parse(
                self._get_stream_for_parsing(),
                self.mimetype,
                self.content_length,
                self.mimetype_params,
            )
        else:
            data = (
                self.stream,
                self.parameter_storage_class(),
                self.parameter_storage_class(),
            )
        d = self.__dict__
        d["stream"], d["form"], d["files"] = data
```
[Wekzeug](https://github.com/pallets/werkzeug/blob/master/src/werkzeug/wrappers/request.py)

In this source code, request sent from the client can be parsed and its form data can be extracted from the request. Parsing HTTP headers and files are also done in this source code.


## License


Flask is licensed under a three clause BSD License. It basically means: do whatever you want with it as long as the copyright in Flask sticks around, the conditions are not modified and the disclaimer is present. Furthermore you must not use the names of the authors to promote derivatives of the software without written consent.
