import functools
import uuid
from dataclasses import asdict, dataclass
from time import time

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
            raise Exception("Database is not defined.")
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

    def __init__(self, cls, query_params, collection_path: str = None):
        """
        @param cls
            The model class to run the query on
        @param query_params
            A list of query params. The lists can be (key, value) or (key, operator,
            value)
        @param collection_path
            Override default collection

        While possible, this method is not intended to be called by itself. The intended
        use is from within the Model.query method.

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
        self.result = None

        self.q = (
            db.collection(collection_path)
            if collection_path
            else db.collection(cls.__name__)
        )

        # parse the params
        for param in query_params:
            if len(param) == 2:
                self.q = self.q.where(param[0], "==", param[1])
            if len(param) == 3:
                self.q = self.q.where(*param)

    def get(self):
        """ Executes the query
        @return Generator
            Generator object that yields hydrated instances of the class supplied
        __init__
        """
        self.result = self.q.get()
        for r in self.result:
            if hasattr(self.cls, "from_dict"):
                yield self.cls.from_dict(r.to_dict())
            else:
                yield self.cls(**r.to_dict())


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
    def delete_doc(cls, doc_id, collection_path: str = None):
        try:
            _collection_path = collection_path if collection_path else cls.__name__
            result = db.collection(_collection_path).document(doc_id).delete()
        except Exception as e:
            print(e)
        return result

    @classmethod
    @require_database
    def get(cls, doc_id, collection_path: str = None, raise_exception=False):
        """ Get a single model instance
        @param cls
            The class of the instance calling make
        @param doc_id
            The id of the document to get
        @param collection_path
            Override the default collection path
        @return model
            A model instance of type class hydrated w/ data from the database
        """
        try:
            _collection_path = collection_path if collection_path else cls.__name__
            doc_ref = db.collection(_collection_path).document(doc_id).get()
            return cls(**doc_ref.to_dict())
        except Exception as e:
            if raise_exception:
                raise e
            return None

    @classmethod
    def make(
        cls,
        doc_id: str = None,
        collection_path: str = None,
        save=False,
        *args,
        **kwargs
    ):
        """ Create a new instance of a model class
        @param cls
            The class of the instance calling make
        @param doc_id
            Allow create document with a custom id
        @param collection_path
            Override collection path
        @param save
            A flag indicating the model should be saved immediately after creation
        @returns cls
            A new model instance of type cls

        Examples:
            User.make(
                name = 'Sonic',
                location = 'Earth',
                save = True
              )

            User.make(
                doc_id = 'custom_id'
                name = 'Sonic',
                location = 'Earth',
                collection_path = 'parent_collection',
                save = True
              )
        """
        id_str = doc_id if doc_id else str(uuid.uuid4())
        created = get_milliseconds()
        modified = created
        _collection_path = collection_path if collection_path else cls.__name__

        model = cls(id_str, created, modified, _collection_path, *args, **kwargs)

        if save:
            model.save()

        return model

    @classmethod
    @require_database
    def query(cls, q=(), collection_path: str = None):
        """ Get a handle to a query object (see Query helper class above)
        @param cls
            The class of the instance calling make
        @param q
            A list of query key/value or key/operator/value pairs
        @param collection_path
            Override collection path
        """
        return Query(cls, q, collection_path=collection_path)

    # --------------------------------------------
    #
    #  instance
    #
    # -------------------------------------------

    id: str
    created: int
    modified: int
    collection_path: str

    @require_database
    def delete(self, raise_exception=False):
        """ Removes this model from Cloud Datastore
        @param raise_exception
            whether to raise exception or boolean
        @raises Exception or boolean
            indicating that deletion failed
        """
        try:
            db.collection(self.collection_path).document(self.id).delete()
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
        @param kvs
            A dictionary containing key value pairs to set on this model.

        Unrecognized keys are ignored
        """
        for k, v in kvs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        self.modified = get_milliseconds()
        db.collection(self.collection_path).document(self.id).set(asdict(self))

    def to_dict(self):
        """ A convenience function that converts this model into a dictionary
        representation

        @return Dict
            A Dictionary of key value pairs representing this model
        """
        return asdict(self)

    @require_database
    def doc(self):
        return db.collection(self.collection_path).document(self.id)

    @require_database
    def collection(self, collection_path):
        return db.collection(collection_path)
