from . import orm

import sqlalchemy

BaseModel = orm.declarative_base()

class Bucket(BaseModel):
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    creation_date = sqlalchemy.Column(sqlalchemy.DateTime)
