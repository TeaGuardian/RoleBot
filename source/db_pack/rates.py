import sqlalchemy
from .db_session import SqlAlchemyBase


class Rate(SqlAlchemyBase):
    __tablename__ = 'rates'
    rid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    uid = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    ruid = sqlalchemy.Column(sqlalchemy.Integer)
    rbid = sqlalchemy.Column(sqlalchemy.Integer)
    rate = sqlalchemy.Column(sqlalchemy.Integer)
