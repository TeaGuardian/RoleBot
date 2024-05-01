import sqlalchemy
from .db_pack import db_session
from .db_pack.users import User
from .db_pack.filters import Filter
from .db_pack.blanks import Blank
from .db_pack.pinned import Pin
from .db_pack.chats_membership import ChatMember
from .db_pack.chats import Chat
from .db_pack.message import Message
from json import dump, load, loads, dumps
from . import arpho
from . import const
from os.path import isfile
from os import listdir, remove
from datetime import datetime
import asyncio


db_session.global_init(const.ROUTE_TO_DB)
DB_SESSION = db_session.create_session()
USER_COUNTER = DB_SESSION.query(User).count()
print("count of users: ", USER_COUNTER)


def confirm_data_editing():
    DB_SESSION.commit()


def get_user_count() -> int:
    global USER_COUNTER
    return USER_COUNTER


def get_bot_backup() -> dict:
    ds = {"bl_last": None, "banned_ips": []}
    if not isfile(const.ROUTE_TO_BACKUP):
        return ds.copy()
    with open(const.ROUTE_TO_BACKUP, mode="r+", encoding=const.ENCODING) as fi:
        data = load(fi)
    for k, v in ds.items():
        if k not in data.keys():
            data[k] = v
    return data.copy()


def save_bot_backup(backup):
    with open(const.ROUTE_TO_BACKUP, mode="w+", encoding=const.ENCODING) as fi:
        dump(backup, fi)


"""____________________________________ USER DB METHODS ____________________________________"""


def reg_user(uid: int, name: str):
    global USER_COUNTER
    USER_COUNTER += 1
    user = User(uid=uid, username=name)
    DB_SESSION.add(user)
    DB_SESSION.commit()
    print("count of users: ", USER_COUNTER)


def delete_user(uid: int):
    global USER_COUNTER
    USER_COUNTER -= 1
    DB_SESSION.delete(DB_SESSION.query(User).filter(User.uid == uid).first())
    DB_SESSION.commit()
    for i in get_blanks(uid):
        if i.exist_to_user and not is_blank_pinned(i.bid):
            delete_blank(uid, i.bid)
    for i in get_filters(uid):
        delete_filter(uid, i.fid)
    for i in get_games(uid):
        del_member(uid, i.chid)
    print("count of users: ", USER_COUNTER)


def is_user_exist(uid: int) -> bool:
    return DB_SESSION.query(User).filter(User.uid == uid).count() > 0


def get_user_data(uid: int) -> User | None:
    return DB_SESSION.query(User).filter(User.uid == uid).first()


"""____________________________________ filter DB METHODS ____________________________________"""


def reg_filter(uid: int):
    filter = Filter(uid=uid)
    DB_SESSION.add(filter)
    DB_SESSION.commit()


def delete_filter(uid: int, fid: int):
    DB_SESSION.delete(DB_SESSION.query(Filter).filter(Filter.uid == uid, Filter.fid == fid).first())
    DB_SESSION.commit()


def is_filter_exist(uid: int, fid: int) -> bool:
    return DB_SESSION.query(Filter).filter(Filter.uid == uid, Filter.fid == fid).count() > 0


def get_filter_data(uid: int, fid: int) -> type[Filter]:
    return DB_SESSION.query(Filter).filter(Filter.uid == uid, Filter.fid == fid).first()


def get_filters(uid: int) -> list[type[Filter]]:
    return DB_SESSION.query(Filter).filter(Filter.uid == uid).all()


def count_filters(uid: int) -> int:
    return DB_SESSION.query(Filter).filter(Filter.uid == uid).count()


"""____________________________________ blank DB METHODS ____________________________________"""


def reg_blank(uid: int):
    blank = Blank(uid=uid)
    DB_SESSION.add(blank)
    DB_SESSION.commit()


def delete_blank(uid: int, bid: int):
    DB_SESSION.delete(DB_SESSION.query(Blank).filter(Blank.uid == uid, Blank.bid == bid, Blank.exist_to_user).first())
    DB_SESSION.commit()


def is_blank_exist(uid: int, bid: int) -> bool:
    return DB_SESSION.query(Blank).filter(Blank.uid == uid, Blank.bid == bid, Blank.exist_to_user).count() > 0


def is_blank_exist_sp(bid: int) -> bool:
    return DB_SESSION.query(Blank).filter(Blank.bid == bid, Blank.exist_to_user).count() > 0


def count_blanks(uid: int) -> int:
    return DB_SESSION.query(Blank).filter(Blank.uid == uid, Blank.exist_to_user).count()


def get_blanks(uid: int) -> list[type[Blank]]:
    return DB_SESSION.query(Blank).filter(Blank.uid == uid, Blank.exist_to_user).all()


def get_blank(bid: int) -> type[Blank]:
    return DB_SESSION.query(Blank).filter(Blank.bid == bid, Blank.exist_to_user).first()


def count_lasts_blanks(uid: int) -> int:
    return DB_SESSION.query(Blank).filter(Blank.uid == uid, Blank.exist_to_user, Blank.finished == False).count()


"""____________________________________ pin DB METHODS ____________________________________"""


def is_blank_pinned(bid: int) -> bool:
    return DB_SESSION.query(Pin).filter(Pin.bid == bid).count() > 0


def is_blank_pinned_for_user(uid: int, bid: int) -> bool:
    return DB_SESSION.query(Pin).filter(Pin.bid == bid, Pin.uid == uid).count() > 0


def pin(uid: int, bid: int):
    pin = Pin(uid=uid, bid=bid)
    DB_SESSION.add(pin)
    DB_SESSION.commit()


def delete_pin(uid: int, pid: int):
    DB_SESSION.delete(DB_SESSION.query(Pin).filter(Pin.uid == uid, Pin.pid == pid).first())
    DB_SESSION.commit()


def get_pins(uid: int) -> list[type[Pin]]:
    return DB_SESSION.query(Pin).filter(Pin.uid == uid).all()


def count_pins(uid: int) -> int:
    return DB_SESSION.query(Pin).filter(Pin.uid == uid).count()


"""____________________________________ search _DB METHODS ____________________________________"""


async def sp_find_blanks(uid: int, fid: int, enc: list):
    start = datetime.now()
    ub, fi = get_user_data(uid), get_filter_data(uid, fid)
    if fi.fil_rate is None and fi.fil_ypol is None:
        bl = DB_SESSION.query(Blank).filter(Blank.exist_to_user, Blank.finished, Blank.publ,
                                            Blank.bid not in enc).limit(const.SEARCH_SP_LIMIT).all()
    elif fi.fil_rate is not None:
        bl = DB_SESSION.query(Blank).filter(Blank.exist_to_user, Blank.finished, Blank.publ,
                                            Blank.bid not in enc, Blank.fil_rate == fi.fil_rate).all()
    elif fi.fil_ypol is not None:
        bl = DB_SESSION.query(Blank).filter(Blank.exist_to_user, Blank.finished, Blank.publ,
                                            Blank.bid not in enc, Blank.fil_ypol == fi.fil_ypol).all()
    else:
        bl = DB_SESSION.query(Blank).filter(Blank.exist_to_user, Blank.finished, Blank.publ,
                                            Blank.bid not in enc, Blank.fil_rate == fi.fil_rate,
                                            Blank.fil_ypol == fi.fil_ypol).all()
    ssl = loads(ub.sp_dat)
    ssl["search"]["query"] = list(map(lambda g: g.bid, sorted(list(bl), key=lambda g: (arpho.grate_similarity(g.fil_fand, fi.fil_fand), g.search_grate(fi.fil_blacklist, fi.fil_typ_dc, fi.fil_typ_ff)), reverse=True)))
    end = datetime.now()
    ssl["search"]["time"] = round((end - start).total_seconds() * 1000 + (end - start).microseconds / 1000, 4)
    ub.sp_dat = dumps(ssl)
    DB_SESSION.commit()


async def find_blanks(uid: int, fid: int, enc: list):
    start = datetime.now()
    ub, fi = get_user_data(uid), get_filter_data(uid, fid)
    if fi.fil_rate is None and fi.fil_ypol is None:
        bl = DB_SESSION.query(Blank).filter(Blank.exist_to_user, Blank.finished, Blank.publ,
                                            Blank.bid not in enc).limit(const.SEARCH_SP_LIMIT).all()
    elif fi.fil_rate is not None:
        bl = DB_SESSION.query(Blank).filter(Blank.exist_to_user, Blank.finished, Blank.publ,
                                            Blank.bid not in enc, Blank.fil_rate == fi.fil_rate).all()
    elif fi.fil_ypol is not None:
        bl = DB_SESSION.query(Blank).filter(Blank.exist_to_user, Blank.finished, Blank.publ,
                                            Blank.bid not in enc, Blank.fil_ypol == fi.fil_ypol).all()
    else:
        bl = DB_SESSION.query(Blank).filter(Blank.exist_to_user, Blank.finished, Blank.publ,
                                            Blank.bid not in enc, Blank.fil_rate == fi.fil_rate,
                                            Blank.fil_ypol == fi.fil_ypol).all()
    ssl = loads(ub.sp_dat)
    ssl["search"]["query"][ub.gbid:ub.gbid] = list(filter(lambda sd: sd not in ssl["search"]["query"], map(lambda g: g.bid, sorted(list(bl), key=lambda g: (arpho.grate_similarity(g.fil_fand, fi.fil_fand), g.search_grate(fi.fil_blacklist, fi.fil_typ_dc, fi.fil_typ_ff)), reverse=True))))
    end = datetime.now()
    ssl["search"]["time"] = round((end - start).total_seconds() * 1000 + (end - start).microseconds / 1000, 4)
    ub.sp_dat = dumps(ssl)
    DB_SESSION.commit()


def get_se_rez(ub: User, n: int) -> int | None:
    ssl = loads(ub.sp_dat)
    return ssl["search"]["query"][ub.gbid] if 0 <= n < len(ssl["search"]["query"]) else None


def clear_sl(ub: User):
    ssl = loads(ub.sp_dat)
    ssl["search"]["query"] = []
    ub.sp_dat = dumps(ssl)
    DB_SESSION.commit()


"""____________________________________ membership + chat DB METHODS ____________________________________"""


def reg_membership(uid: int, chid: int, owner=False):
    ch = ChatMember(uid=uid, chid=chid, is_owner=owner, nickname=get_user_data(uid).nickname)
    DB_SESSION.query(Chat).filter(Chat.chid == chid).first().members_co += 1
    DB_SESSION.add(ch)
    DB_SESSION.commit()


def reg_chat(uid: int, name: str) -> int:
    c = Chat(title=name.lstrip("$"), is_writable=name.startswith("$"))
    DB_SESSION.add(c)
    DB_SESSION.commit()
    if not name.startswith("$"):
        reg_message(c.chid, uid, name)
    reg_membership(uid, c.chid, True)
    return c.chid


def get_games(uid: int) -> list[type[ChatMember]]:
    return DB_SESSION.query(ChatMember).filter(ChatMember.uid == uid).all()


def count_games(uid: int) -> int:
    return DB_SESSION.query(ChatMember).filter(ChatMember.uid == uid).count()


def get_membership(uid: int, chid: int) -> type[ChatMember]:
    return DB_SESSION.query(ChatMember).filter(ChatMember.uid == uid, ChatMember.chid == chid).first()


def get_chat_data(chid: int) -> type[Chat]:
    return DB_SESSION.query(Chat).filter(Chat.chid == chid).first()


def get_waitingers(chid: int) -> list[type[ChatMember]]:
    return DB_SESSION.query(ChatMember).filter(ChatMember.chid == chid, ChatMember.accepted != True, ChatMember.is_owner != True).all()


async def clear_messages(chid: int):
    for i in DB_SESSION.query(Message).filter(Message.chid == chid).all():
        DB_SESSION.delete(i)
    DB_SESSION.commit()


def del_chat(chid: int):
    DB_SESSION.delete(DB_SESSION.query(Chat).filter(Chat.chid == chid).first())
    DB_SESSION.commit()
    asyncio.create_task(clear_messages(chid))


def del_member(uid: int, chid: int):
    chat = get_chat_data(chid)
    chat.members_co -= 1
    if chat.members_co < 1:
        del_chat(chid)
    DB_SESSION.delete(DB_SESSION.query(ChatMember).filter(ChatMember.uid == uid, ChatMember.chid == chid).first())
    DB_SESSION.commit()


def is_membership_exist(uid: int, chid: int) -> bool:
    return DB_SESSION.query(ChatMember).filter(ChatMember.uid == uid, ChatMember.chid == chid).count() > 0


def get_memberships(chid: int) -> list[type[ChatMember]]:
    return DB_SESSION.query(ChatMember).filter(ChatMember.chid == chid).all()


def is_chat_exist(chid: int) -> bool:
    return DB_SESSION.query(Chat).filter(Chat.chid == chid).count() > 0


def is_message_exist(chid: int, mid: int) -> bool:
    return DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid == mid).count() > 0


def is_messages_exist(chid: int) -> bool:
    return DB_SESSION.query(Message).filter(Message.chid == chid).count() > 0


def count_messages(chid: int) -> int:
    return DB_SESSION.query(Message).filter(Message.chid == chid).count()


def is_next_message_exist(chid: int, mid: int) -> bool:
    return DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid > mid).count() > 0


def is_before_message_exist(chid: int, mid: int) -> bool:
    return DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid < mid).count() > 0


def get_next_message_id(chid: int, mid: int) -> int:
    return DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid > mid).first().mid


def get_before_message_id(chid: int, mid: int) -> int:
    return DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid < mid).all()[-1].mid


def get_all_messages(chid: int) -> list[type[Message]]:
    return DB_SESSION.query(Message).filter(Message.chid == chid).all()


def get_first_message_id(chid: int) -> int:
    return DB_SESSION.query(Message).filter(Message.chid == chid).first().mid


def reg_message(chid: int, uid: int, text: str):
    chat = get_chat_data(chid)
    chat.last_sended = datetime.now()
    for mt in arpho.split_string(text, const.MAX_MESSAGE_LEN):
        ms = Message(chid=chid, uid=uid, text=mt)
        chat.messages_co += 1
        DB_SESSION.add(ms)
    DB_SESSION.commit()


def del_message(chid: int, mid: int):
    DB_SESSION.delete(DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid == mid).first())
    get_chat_data(chid).messages_co -= 1
    DB_SESSION.commit()


def get_message(chid: int, mid: int) -> type[Message]:
    return DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid == mid).first()


def should_notify_user(uid: int) -> bool:
    ub = get_user_data(uid)
    da = loads(ub.sp_dat)
    rez = False
    if "chat_notify_flag" not in da.keys() or da["chat_notify_flag"]:
        da["chat_notify_flag"] = False
        rez = True
    ub.sp_dat = dumps(da)
    DB_SESSION.commit()
    return rez


def clear_should_notify_user(uid: int):
    ub = get_user_data(uid)
    da = loads(ub.sp_dat)
    da["chat_notify_flag"] = True
    ub.sp_dat = dumps(da)
    DB_SESSION.commit()


def chat_binded_count(chid: int) -> int:
    return DB_SESSION.query(Blank).filter(Blank.chid == chid, Blank.exist_to_user, Blank.finished, Blank.publ).count()


async def _manage_atc():
    ldd = listdir(const.ROUTE_TO_CHAT_BUILD)
    while len(ldd) > const.CLEAN_LIMIT:
        remove(f"{const.ROUTE_TO_CHAT_BUILD}/{ldd.pop(0)}")


async def build_story(chid: int) -> str:
    ch = get_chat_data(chid)
    path = f"{const.ROUTE_TO_CHAT_BUILD}/chat_rv1_{chid}_{ch.messages_co}.txt"
    if isfile(path):
        return path
    memb = get_memberships(chid)
    msgs = get_all_messages(chid)
    with open(file=path, encoding=const.ENCODING, mode="w+") as file:
        topik = f"[сгенерировано на основе чата '{ch.title}' ({chid})]\n" \
                f"в ролях: {list(map(lambda g: g.nickname, memb))}\n" \
                f"постов: {ch.messages_co}\n" \
                f"отображение форматирования: html\n\n\n\n"
        file.write(topik)
    memb = dict(map(lambda obj: (obj.uid, obj.nickname), memb))
    able = memb.keys()
    with open(file=path, encoding=const.ENCODING, mode="a+") as file:
        for msg in msgs:
            file.writelines(f"\n\n==> {memb[msg.uid] if msg.uid in able else msg.nickname}:\n{msg.text}")
    if len(listdir(const.ROUTE_TO_CHAT_BUILD)) > const.CLEAN_LIMIT:
        asyncio.create_task(_manage_atc())
    return path
