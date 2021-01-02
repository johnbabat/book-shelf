import os
import json
from sqlalchemy import Column, String, Integer, Boolean, create_engine
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

database_name = "books"
database_path = "postgresql://postgres:postgres@localhost:5432/" + database_name

db = SQLAlchemy()

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app=app
    db.init_app(app)
    db.create_all()


class Book(db.Model):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    rating = Column(Integer)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'rating': self.rating
        }