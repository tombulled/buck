from . import orm

import sqlalchemy
import sqlalchemy.orm

BaseModel = orm.declarative_base()

class Bucket(BaseModel):
    id            = sqlalchemy.Column(sqlalchemy.Integer,  index=True,  nullable=False, primary_key=True)
    name          = sqlalchemy.Column(sqlalchemy.String,   index=True,  nullable=False, unique=True)
    creation_date = sqlalchemy.Column(sqlalchemy.DateTime, index=True,  nullable=False, unique=False)
    owner_id      = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))#, index=False, nullable=False, unique=False)

    owner = sqlalchemy.orm.relationship('User', back_populates='buckets')

class User(BaseModel):
    id         = sqlalchemy.Column(sqlalchemy.Integer, index=True, nullable=False, primary_key=True)
    name       = sqlalchemy.Column(sqlalchemy.String,  index=True, nullable=False, unique=False)
    access_key = sqlalchemy.Column(sqlalchemy.String,  index=True, nullable=False, unique=True)
    secret_key = sqlalchemy.Column(sqlalchemy.String,  index=True, nullable=False, unique=False)

    buckets = sqlalchemy.orm.relationship('Bucket', back_populates='owner')
