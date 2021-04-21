Bcrypt Official [Bcrypt] (https://github.com/pyca/bcrypt)

Code used in database.py and test_mongo.py
```
password = request.form.get('password').encode('utf-8')
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password, salt)
```
Why we need this library?

We dont want to store our users' password in plain text.

For bcrypt.gensalt()

This generates a random salt for later hashing of a password

For bcrypt.hashpw(password,salt)

We are able to generate a hashed password with salt
generated from bcrypt.gensalt(). This hashed password in
encrypted, so hackers are not able to find out the real 
password of our users if they break in the database.

License apply to this library:
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/