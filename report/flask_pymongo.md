# flask_pymongo - A bridge that connects Flask and PyMongo


[flask_pymongo Documentation](https://flask-pymongo.readthedocs.io/en/latest/)

[flask_pymongo Source](https://github.com/dcrosta/flask-pymongo)




## What does flask_pymongo PyMongo accomplish for us?


We used the PyMongo helper module to save the image file to GridFS(a specification for storing and retrieving files that exceed the BSON-document size limit of 16 MB in MongoDB) and to get the image file from GridFS


## How does this technology accomplish what it does?
[send_file and save_file Source Code](https://github.com/dcrosta/flask-pymongo/blob/master/flask_pymongo/__init__.py)




flask_pymongo PyMongo - save_file
First, it determines the name for GridFS collections to be used and if the image file has read() method so the file is in the right format. Then, it determines the mimeType of the file(image for our case). It saves the image object to GridFS with the image file, filename, contentType, and some extra attributes to be stored in GridFS.






flask_pymongo PyMongo - send_file
First, it determines if the used collection name is in the right format, it checks for the corresponding version or revision of the file, and it instructs the number of seconds the browser should use to cache the response. Then it obtains the collection from the GridFS, and searches and gets for the image file with corresponding filename. Finally, save everything to a response and send it to the client.


## What license(s) or terms of service apply to this technology?
Copyright (c) 2011-2017, Dan Crosta
All rights reserved.


Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:


* Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.


* Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.


We can redistribute and use the source with or without modification when we retain the copyright notice