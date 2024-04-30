import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
import datetime


class Calls(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'calls'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True, nullable=False)
    datetime = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    phonea = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    phoneb = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    direction = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    billsec = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    linkedid = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    def __repr__(self):
        return f""
