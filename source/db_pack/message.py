import sqlalchemy
from .db_session import SqlAlchemyBase


class Message(SqlAlchemyBase):
    __tablename__ = 'messages'
    mid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    chid = sqlalchemy.Column(sqlalchemy.Integer)
    uid = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, default="unknown")
    text = sqlalchemy.Column(sqlalchemy.String, default="")
