import sqlalchemy
from .db_session import SqlAlchemyBase


class Pin(SqlAlchemyBase):
    __tablename__ = 'pinned'
    pid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    bid = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    uid = sqlalchemy.Column(sqlalchemy.Integer)