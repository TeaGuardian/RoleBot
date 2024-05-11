import sqlalchemy
from .db_session import SqlAlchemyBase


class Filter(SqlAlchemyBase):
    __tablename__ = 'filters'
    fid = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    uid = sqlalchemy.Column(sqlalchemy.Integer, index=True)

    fil_ypol = sqlalchemy.Column(sqlalchemy.String)
    fil_fand = sqlalchemy.Column(sqlalchemy.String)
    fil_typ_ff = sqlalchemy.Column(sqlalchemy.String)
    fil_typ_dc = sqlalchemy.Column(sqlalchemy.String)      # полное включение
    fil_blacklist = sqlalchemy.Column(sqlalchemy.String)   # полное исключение
    fil_rate = sqlalchemy.Column(sqlalchemy.String)

    finished = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    notify = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    notified = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    state = sqlalchemy.Column(sqlalchemy.Integer, default=0)
