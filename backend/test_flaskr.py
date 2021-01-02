import os
import json
import unittest

from flaskr import create_app, setup_db, Book

class BookTestCAse(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "bookshelf_test"
        self.database_path = "postgresql://postgres:postgres@localhost:5432/" + self.database_name
        setup_db(self.app, self.database_path)

        self.new_book = {
            'title': 'Anansi Boys',
            'author': 'Neil Gaiman',
            'rating': 5
        }


    def tearDown(self):
        pass


    def test_get_paginated_books(self):
        res = self.client().get('/books')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/books?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_update_book_rating(self):
        res = self.client().patch('/books/2', json={'rating': 1})
        data = json.loads(res.data)
        book = Book.query.get(2)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(book.format()['rating'], 1)

    def test_400_for_failed_update(self):
        res = self.client().patch('books/2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_delete_book(self):
        res = self.client().delete('/books/1')
        data = json.loads(res.data)

        book = Book.query.get(1)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 1)
        self.assertTrue(data['total_books'])
        self.assertTrue(len(data['books']))
        self.assertEqual(book, None)

    def test_422_if_book_does_not_exist(self):
        res = self.client().delete('/books/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable') 

    def test_create_new_book(self):
        res = self.client().post('/books', json=self.new_book)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['books']))


    def test_405_if_book_creation_not_allowed(self):
        res = self.client().post('/books/45', json=self.new_book)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')



if __name__ == "__main__":
    unittest.main()