import sqlalchemy
import datetime
from .db_session import SqlAlchemyBase
from source.arpho import grate_similarity, desea
from source.const import WORD_THRESHOLD_LIMIT, INSEPTION_TEG_LIMIT


class Blank(SqlAlchemyBase):
    __tablename__ = 'blanks'
    bid = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    uid = sqlalchemy.Column(sqlalchemy.Integer, index=True)
    chid = sqlalchemy.Column(sqlalchemy.Integer)
    reg_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    fil_name = sqlalchemy.Column(sqlalchemy.String)
    fil_ypol = sqlalchemy.Column(sqlalchemy.String)
    fil_fand = sqlalchemy.Column(sqlalchemy.String)
    fil_typ = sqlalchemy.Column(sqlalchemy.String)
    fil_tmp = sqlalchemy.Column(sqlalchemy.String)
    fil_des = sqlalchemy.Column(sqlalchemy.String)
    fil_rate = sqlalchemy.Column(sqlalchemy.String)
    fil_chat = sqlalchemy.Column(sqlalchemy.String)

    publ = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    exist_to_user = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    finished = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    state = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    views = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    score_mi = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    score_pl = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    def search_grate(self, blacklist, whitelist, search, limited=False):
        bl = [] if blacklist is None else map(lambda g: g.rstrip(" ").lstrip(" "), blacklist.split(","))
        wl = [] if whitelist is None else list(map(lambda g: g.rstrip(" ").lstrip(" "), whitelist.split(",")))
        se = [] if search is None else list(map(lambda g: g.rstrip(" ").lstrip(" "), search.split(",")))
        rez, count = 0, 0
        for word in map(lambda g: g.rstrip(" ").lstrip(" "), self.fil_typ.__str__().split(",")):
            if any(map(lambda g: grate_similarity(g, word) >= WORD_THRESHOLD_LIMIT, bl)):
                return 0
            if wl:
                wl, ad = desea(word, wl.copy())
                if ad < WORD_THRESHOLD_LIMIT:
                    return 0
            if se:
                al, ad = desea(word, se.copy())
                if ad >= INSEPTION_TEG_LIMIT:
                    rez += ad
                    count += 1
                    se = al.copy()
        if limited and count > 0:
            return round(rez / count, 6)
        return rez


