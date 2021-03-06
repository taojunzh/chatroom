# Flask SocketIO

[Flask-SocketIO Documentations](https://flask-socketio.readthedocs.io/en/latest/)
[Flask-SocketIO Source Code](https://github.com/miguelgrinberg/Flask-SocketIO)

## What does this technology (library/framework/service) accomplish for you?
Flask-SocketIO gives Flask applications access to low latency bi-directional communications between the clients and the server.

```
@socketio.on('vote')
def voting(input):
    storevote(input)

    result1 = countvote(1)
    result2 = countvote(2)
    # print(result1,result2)
    socketio.emit('voting bar',(result1,result2),broadcast =True)
```
When using SocketIO, events are received by both parties through WebSockets. Our code use @socketio.on("vote") to create a server-side event handler for “string” event. Once we are done with the data, we can use socketio.emit to notify the clients.

## How does the code do what it does?
[code source](https://github.com/miguelgrinberg/Flask-SocketIO/blob/master/flask_socketio/__init__.py)
```
def emit(event, *args, **kwargs):
    if 'namespace' in kwargs:
        namespace = kwargs['namespace']
    else:
        namespace = flask.request.namespace
    callback = kwargs.get('callback')
    broadcast = kwargs.get('broadcast')
    to = kwargs.pop('to', kwargs.pop('room', None))
    if to is None and not broadcast:
        to = flask.request.sid
    include_self = kwargs.get('include_self', True)
    skip_sid = kwargs.get('skip_sid')
    ignore_queue = kwargs.get('ignore_queue', False)

    socketio = flask.current_app.extensions['socketio']
    return socketio.emit(event, *args, namespace=namespace, to=to,
                         include_self=include_self, skip_sid=skip_sid,
                         callback=callback, ignore_queue=ignore_queue)


def send(message, **kwargs):
    json = kwargs.get('json', False)
    if 'namespace' in kwargs:
        namespace = kwargs['namespace']
    else:
        namespace = flask.request.namespace
    callback = kwargs.get('callback')
    broadcast = kwargs.get('broadcast')
    to = kwargs.pop('to', kwargs.pop('room', None))
    if to is None and not broadcast:
        to = flask.request.sid
    include_self = kwargs.get('include_self', True)
    skip_sid = kwargs.get('skip_sid')
    ignore_queue = kwargs.get('ignore_queue', False)

    socketio = flask.current_app.extensions['socketio']
    return socketio.send(message, json=json, namespace=namespace, to=to,
                         include_self=include_self, skip_sid=skip_sid,
                         callback=callback, ignore_queue=ignore_queue)
```

When we use socketio.send or socketio.emit, it is going to send the event and data to the clients. We can also specify whether we want to send the event to a specific room. If room is not specified, it will be a broadcast.

```
def on(self, message, namespace=None):
       namespace = namespace or '/'

       def decorator(handler):
           @wraps(handler)
           def _handler(sid, *args):
               return self._handle_event(handler, message, namespace, sid,
                                         *args)

           if self.server:
               self.server.on(message, _handler, namespace=namespace)
           else:
               self.handlers.append((message, _handler, namespace))
           return handler
       return decorator

def _handle_event(self, handler, message, namespace, sid, *args):
           environ = self.server.get_environ(sid, namespace=namespace)
           if not environ:
               return '', 400
           app = environ['flask.app']
           with app.request_context(environ):
               if self.manage_session:
                   if 'saved_session' not in environ:
                       environ['saved_session'] = _ManagedSession(flask.session)
                   session_obj = environ['saved_session']
               else:
                   session_obj = flask.session._get_current_object()
               _request_ctx_stack.top.session = session_obj
               flask.request.sid = sid
               flask.request.namespace = namespace
               flask.request.event = {'message': message, 'args': args}
               try:
                   if message == 'connect':
                       ret = handler()
                   else:
                       ret = handler(*args)
               except:
                   err_handler = self.exception_handlers.get(
                       namespace, self.default_exception_handler)
                   if err_handler is None:
                       raise
                   type, value, traceback = sys.exc_info()
                   return err_handler(value)
               if not self.manage_session:
                   if not hasattr(session_obj, 'modified') or \
                           session_obj.modified:
                       resp = app.response_class()
                       app.session_interface.save_session(app, session_obj, resp)
               return ret
```

Socketio.on is a decorator. It is going to trigger an event handler to properly handle the event whenever we call socketio.on. If the event is from a client that is not recorded, the event will be ignored.

When socketio.on('connect') is triggered, it means that the web browser wants to establish a WebSocket connection. Flask-socketio will handle the connection and save the session of the browser.

## What license(s) or terms of service apply to this technology?
License: MIT License (MIT)
