# firestore-model

Quickly and simply create model classes for Google's Cloud Firestore schemaless database. 


## Overview
This project seeks to provide a similar convenience and utility for using Cloud Firestore with the newly available Python 3.7 App Engine Envinronment as the NDB client library does for using Cloud Datastore with Python 2.7 App Engine.

[Blog post describing motivation and further usage](https://medium.com/@jeremy.from.earth/using-dataclasses-firestore-to-replace-ndb-datastore-on-python-3-7-app-engine-e21199b58ef2)

## Example

```
import firestore_model
from google.firestore import firestore
from filestore_model import Model, Query

# initialize the database connection globally for Firestore Model 
firestore_model.db = firestore.Client()

# Define a data structure for a User
@dataclass
class User(Model):
  first_name:str
  last_name:str
  occupation:str

# Create a new user, pass save = True to automagically save the model object
u1 = User.make(
    first_name='Sonic',
    last_name='Brown',
    occupation='circus dog'
    save=True
  )

# Fetch all users that match a given query
users = User.query([
    ('occupation', 'circus dog'), 
    ('created', '>', 1540776978)
  ]
).get()

# Iterate through the results of the query
for u in users:
  print(u.id, u.created, u.first_name, u.last_name, u.occupation)
```

