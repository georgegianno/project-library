I run this project using the following steps:
  --> Set python version to 3.8.6 (pyenv local 3.8.6)
  --> git clone https://github.com/georgegianno/project-library.git
  --> python -m venv venv
  --> source venv/bin/activate
  --> pip install -r requirements.txt
  --> python manage.migrate
  --> python manage.py runserver

There is a superuser with username: superuser, password: testing

There are two commands, to import books and authors:
  --> python manage.py import_authors <path_to_authors.json_file>
  --> python manage.py import_books <path_to_books.json_file>

  Authorization method is JWT to obtain bearer token

Requests:

  --> POST /library/register/ with body {"username": <value>, "password": <value>} to get access bearer token
  --> POST /library/login/ with body {"username": <value>, "password": <value>} to get access bearer token
  --> GET /library/users/ is only for admin users. Shows all the system users
  --> GET /library/books/ is allowed to everyone to fetch all books
  --> GET /library/books/<value> is allowed to everyone to fetch the book with the book_id in the books.json file
  --> GET /library/books?search=<value>/ searches books by title or author name 
  --> POST, PUT, DELETE /library/books/<value> is protected, requires admin permissions and a body with the book_id as required field (i.e. {"book_id": <value>, "title": <value>})
  --> Requests to /library/authors/ work the same way (without the search option)
  --> GET /library/favorites/ is only for authenticated users
  --> POST, DELETE /library/books/<value> is only for authenticated users and requires {"book_id": <value>} in body for the desired book
  --> GET /library/recommendations/ is only for authenticated users

  Specifications:
    --> I have set as required field the 'book_id' and 'author_id' for Book and Author models as it is in the json files of the dataset. I use this as a lookup field for queries
      as it seems more proper
    --> The recommendations are explained in library/views.py


  


 
