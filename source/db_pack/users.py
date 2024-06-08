import datetime
from json import dumps
import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    iid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    uid = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    username = sqlalchemy.Column(sqlalchemy.String)
    nickname = sqlalchemy.Column(sqlalchemy.String, default=f"unknown")
    reg_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    last_active = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    notify_a = sqlalchemy.Column(sqlalchemy.Boolean, default=True)   # уведомления рекламы
    notify_c = sqlalchemy.Column(sqlalchemy.Boolean, default=True)   # уведомления принятия рп
    notify_i = sqlalchemy.Column(sqlalchemy.Boolean, default=False)   # уведомления от администрации
    delete_p = sqlalchemy.Column(sqlalchemy.Boolean, default=False)   # удаление аккаунта
    role = sqlalchemy.Column(sqlalchemy.String, default="user")
    gram_su = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    gram_co = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    rate_su = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    rate_co = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    last_message = sqlalchemy.Column(sqlalchemy.String)
    last_call = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    mmid = sqlalchemy.Column(sqlalchemy.Integer, default=0)   # id сообщения-меню
    mbid = sqlalchemy.Column(sqlalchemy.Integer, default=0)   # id бланка
    mfid = sqlalchemy.Column(sqlalchemy.Integer, default=0)   # id фильтра
    mpid = sqlalchemy.Column(sqlalchemy.Integer, default=0)   # id закрепа
    mrid = sqlalchemy.Column(sqlalchemy.Integer, default=0)   # id оценки
    beid_f = sqlalchemy.Column(sqlalchemy.Boolean, default=False)   # флаг редактирования бланка
    feid_f = sqlalchemy.Column(sqlalchemy.Boolean, default=False)   # флаг редактирования фильтра
    gfid = sqlalchemy.Column(sqlalchemy.Integer, default=0)   # номер фильтра в поиске
    gbid = sqlalchemy.Column(sqlalchemy.Integer, default=0)   # номер записи в поиске
    gsel = sqlalchemy.Column(sqlalchemy.Integer, default=0)   # селектор игры
    game = sqlalchemy.Column(sqlalchemy.Integer, default=0)   # открытая игра
    game_f = sqlalchemy.Column(sqlalchemy.Boolean, default=False)   # флаг открытой игры
    state = sqlalchemy.Column(sqlalchemy.String)   # поле состояния пользователя

    sp_dat = sqlalchemy.Column(sqlalchemy.JSON, default=dumps({"search": {"query": []}, "time": 0}))
