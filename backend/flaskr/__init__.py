import os
import json
from flask import Flask, render_template, request, Response, flash, redirect, abort, make_response, jsonify
from flask_moment import Moment
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from models import setup_db, Book

BOOKS_PER_SHELF = 8

def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF

    books = [book.format() for book in selection]
    current_books = books[start:end]

    return current_books

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)
    CORS(app)


    # # CORS Headers
    @app.after_request
    def after_request(response):
        # response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow_Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/books')
    def retrieve_books():
        selection = Book.query.order_by('id').all()
        current_books = paginate(request, selection)

        if not current_books:
            abort(404)

        return jsonify({
            'success': True,
            'books': current_books,
            'books_on_page': len(current_books),
            'total_books': len(Book.query.all())
        })

    @app.route('/books/<int:book_id>', methods=['PATCH'])
    def update_book(book_id):
        body = request.get_json()

        try:
            book = Book.query.get(book_id)

            if not book:
                abort(404)
            
            if 'rating' in body:
                book.rating = int(body.get('rating'))

            book.update()

            return jsonify({
                'success': True
            })

        except:
            abort(400)

    @app.route('/books', methods=['POST'])
    def create_book():
        body = request.get_json()

        new_id = body.get('id', None)
        new_title = body.get('title', None)
        new_author = body.get('author', None)
        new_rating = body.get('rating', None)

        try:
            if new_id:
                book = Book(id=new_id, title=new_title, author=new_author, rating=new_rating)
            else:
                book = Book(title=new_title, author=new_author, rating=new_rating)

            book.insert()

            selection = Book.query.order_by('id').all()
            current_books = paginate(request, selection)

            return jsonify({
                'success': True,
                'created': book.id,
                'books': current_books,
                'total_books': len(selection)
            })
        except:
            abort(422)

    @app.route('/books/<int:book_id>', methods=["DELETE"])
    def delete_book(book_id):
        try:
            book = Book.query.get(book_id)

            # print('delete function')
            # print(book)
            # print(book.id, book.title)

            if not book:
                abort(404)
        
            book.delete()

            selection = Book.query.order_by('id').all()
            current_books = paginate(request,selection)

            return jsonify({
                'success': True,
                'deleted': book_id,
                'books': current_books,
                'total_books': len(selection)
            })
        
        except:
            abort(422)
    
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(400)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(405)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405


    return app