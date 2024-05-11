import sqlalchemy
from .db_session import SqlAlchemyBase


class ChatMember(SqlAlchemyBase):
    __tablename__ = 'chats_membership'
    lid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    uid = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    cursor = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    chid = sqlalchemy.Column(sqlalchemy.Integer)
    nickname = sqlalchemy.Column(sqlalchemy.String)
    accepted = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    notify = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    notified = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    is_owner = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
