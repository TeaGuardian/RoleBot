import sqlalchemy
from datetime import datetime
from .db_session import SqlAlchemyBase


class Chat(SqlAlchemyBase):
    __tablename__ = 'chats'
    chid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    last_sended = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.now())
    members_co = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    messages_co = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_writable = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
