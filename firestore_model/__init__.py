import uuid
import functools
from time import time
from dataclasses import dataclass, asdict

# --------------------------------------------
#
#  The main database client reference
#
# -------------------------------------------
db = None

# --------------------------------------------
#
#  Utils
#
# -------------------------------------------
def get_milliseconds():
  """
    @return Milliseconds since the epoch
  """
  return int(round(time() * 1000))

def require_database(f, *args, **kwargs):
  """ Decorator for methods that access the database
    @raises Exception
    @return Decorator for methods that require database access
  """
  @functools.wraps(f)
  def wrapper(*args, **kwargs):
    if db is None:
      raise Exception('Database is not defined.')
    else:
      return f(*args, **kwargs)
  return wrapper

# --------------------------------------------
#
#  Classes
#
# -------------------------------------------

class Query(object):
  """ A class representing a query on a collection
  """
  def __init__(self, cls, query_params):
    """
      @param cls The model class to run the query on
      @param A list of query params. The lists can be (key, value) or (key, operator, value)

      While possible, this method is not intended to be called by itself. The intended use
      is from within the Model.query method.

      Examples:
        # Get all users with first name Sonic
        q = User.query([('first_name', 'Sonic')])
        result = q.get()
        for r in result:
          # do something with r

        # Get 10 users created before a specific datetime
        query = User.query([('created', '<', 23409328408)])
        query.q.limit(10)
        result = query.get()
        for r in result:
          # do something with r

      References:
        https://googleapis.github.io/google-cloud-python/latest/firestore/query.html
    """
    self.cls = cls
    self.q = db.collection(cls.__name__)

    # parse the params
    for param in query_params:
      if len(param) == 2:
        self.q = self.q.where(param[0], '==', param[1])
      if len(param) == 3:
        self.q = self.q.where(*param)

  def get(self, limit=None):
    """ Executes the query
      @return Generator object that yields hydrated instances of the class supplied __init__
    """
    if limit:
      self.q.limit(limit)

    for doc in self.q.stream():
      doc_data = doc.get(field_path=None)
      if hasattr(self.cls, 'from_dict'):
        yield self.cls.from_dict(doc_data)
      else:
        yield self.cls(**doc_data)

@dataclass
class Model:
  """ Base class for all other model classes
  """
  # --------------------------------------------
  #
  #  static
  #
  # -------------------------------------------

  @classmethod
  @require_database
  def delete_doc(cls, doc_id):
    try:
      result = db.collection(cls.__name__).document(doc_id).delete()
    except Exception as e:
      print(e)

  @classmethod
  @require_database
  def get(cls, doc_id, raise_exception=False):
    """ Get a single model instance
      @param cls The class of the instance calling make
      @param doc_id The id of the document to get
      @return A model instance of type class hydrated w/ data from the database
    """
    try:
      doc_ref = db.collection(cls.__name__).document(doc_id).get()
      return cls(**doc_ref.to_dict())
    except Exception as e:
      if raise_exception:
        raise e
      return None

  @classmethod
  def make(cls, save=False, *args, **kwargs):
    """ Create a new instance of a model class
      @param cls The class of the instance calling make
      @param save A flag indicating the model should be saved immediately after creation
      @returns A new model instance of type cls

      Example:
        User.make(
            name = 'Sonic',
            location = 'Earth',
            save = True
          )
    """
    id_str = str(uuid.uuid4())
    created = get_milliseconds()
    m = cls(id_str, created, created, *args, **kwargs)
    if save: m.save()
    return m

  @classmethod
  @require_database
  def query(cls, q=()):
    """ Get a handle to a query object (see Query helper class above)
      @param cls The class of the instance calling make
      @param q A list of query key/value or key/operator/value pairs (
    """
    return Query(cls, q)

  # --------------------------------------------
  #
  #  instance
  #
  # -------------------------------------------

  id:str
  created:int
  modified:int

  @require_database
  def delete(self, raise_exception=False):
    """ Removes this model from Cloud Datastore

      @raises Exception indicating that deletion failed
    """
    collection_name = self.__class__.__name__
    try:
      db.collection(collection_name).document(self.id).delete()
      return True
    except Exception as e:
      if raise_exception:
        raise e
      print(e)
      return False

  @require_database
  def save(self):
    """ Saves this model to Cloud Firestore """
    return self.set(asdict(self))

  @require_database
  def set(self, kvs):
    """ Set values on this model
      @param kvs A dictionary containing key value pairs to set on this model.
      Unrecognized keys are ignored
    """
    collection_name = self.__class__.__name__
    for k, v in kvs.items():
      if hasattr(self, k):
        setattr(self, k, v)
    self.modified = get_milliseconds()
    db.collection(collection_name).document(self.id).set(asdict(self))

  def to_dict(self):
    """ A convenience function that converts this model into a dictionary representation

      @return Dictionary of key value pairs representing this model
    """
    return asdict(self)
