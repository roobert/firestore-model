# firestore-model

A small lib for creating model classes using Google's Cloud Firestore schemaless database. 


## Overview
With the release of the of Google's Python 3.7 App Engine came a handful of new libraries for interacting with GCP. The new libs provide a more idiomatic Python development experience. As a part of this upgrade the NDB client library is not compatible with Python 3.7. This small project seeks to replace some of the convenience of the NDB library. Based on the new Dataclasses data structure, it enables you to write useful model classes quickly and simply. 

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

