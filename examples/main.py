import firestore_model
from dataclasses import dataclass
from firestore_model import Model
from google.cloud import firestore

# Initialize connection to the database
firestore_model.db = firestore.Client()

# Create a model class
@dataclass
class Book(Model):
  title:str
  author:str
  publisher:str
  year:int
  pages:int

if __name__ == '__main__':
  book_id = '100800604002'

  b = Book.make(
    title='Sirens of Titan',
    author='Kurt Vonnegut',
    publisher='Delacorte',
    year=1959,
    pages=319
  )

  b.id = book_id
  print(b.to_dict())
  b.save()

  b = Book.get(book_id)
  print(b)

  query = Book.query([
    ('author', 'Kurt Vonnegut'),
  ])

  for b in query.get():
    print(b.to_dict())

  b.delete()
  print(Book.get(book_id))
