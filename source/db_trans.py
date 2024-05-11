import source.builders
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
from typing import List


db_session.global_init(const.ROUTE_TO_DB)
DB_SESSION = db_session.create_session()
USER_COUNTER = DB_SESSION.query(User).count()
print("count of users: ", USER_COUNTER)


def confirm_data_editing():
    """сохранить изменения в базу данных"""
    DB_SESSION.commit()


def get_user_count() -> int:
    """сообщить число пользователей бота"""
    global USER_COUNTER
    return USER_COUNTER


def get_bot_backup() -> dict:
    """восстановить данные бота"""
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
    """сохранить данные бота"""
    with open(const.ROUTE_TO_BACKUP, mode="w+", encoding=const.ENCODING) as fi:
        dump(backup, fi)


"""____________________________________ USER DB METHODS ____________________________________"""


def reg_user(uid: int, name: str):   # зарегестрировать пользователя
    global USER_COUNTER
    USER_COUNTER += 1
    user = User(uid=uid, username=name)
    DB_SESSION.add(user)
    DB_SESSION.commit()
    print("count of users: ", USER_COUNTER)


async def clear_user_data(uid: int):   # очистить данные пользователя
    for i in get_pins(uid):
        delete_pin(uid, i.pid)
    for i in get_blanks(uid):
        if i.exist_to_user and not is_blank_pinned(i.bid):
            delete_blank(uid, i.bid)
    for i in get_filters(uid):
        delete_filter(uid, i.fid)
    for i in get_games(uid):
        del_member(uid, i.chid)


def delete_user(uid: int):   # удалить пользователя
    global USER_COUNTER
    USER_COUNTER -= 1
    DB_SESSION.delete(DB_SESSION.query(User).filter(User.uid == uid).first())
    DB_SESSION.commit()
    asyncio.create_task(clear_user_data(uid))
    print("count of users: ", USER_COUNTER)


def is_user_exist(uid: int) -> bool:   # проверить существование пользователя
    return DB_SESSION.query(User).filter(User.uid == uid).count() > 0


def get_user_data(uid: int) -> User | None:   # получить данные пользователя
    return DB_SESSION.query(User).filter(User.uid == uid).first()


def get_users_by_role(role: str) -> List[User]:   # получить список пользователей по роли
    return DB_SESSION.query(User).filter(User.role == role).all()


def is_user_have_role(uid: int, role: str) -> bool:   # получить список пользователей по роли
    return DB_SESSION.query(User).filter(User.uid == uid, User.role == role).count() > 0


"""____________________________________ filter DB METHODS ____________________________________"""


def reg_filter(uid: int):   # зарегистрировать фильтр
    filter = Filter(uid=uid)
    DB_SESSION.add(filter)
    DB_SESSION.commit()


def delete_filter(uid: int, fid: int):   # удалить фильтр
    DB_SESSION.delete(DB_SESSION.query(Filter).filter(Filter.uid == uid, Filter.fid == fid).first())
    DB_SESSION.commit()


def is_filter_exist(uid: int, fid: int) -> bool:   # проверить существование фильтра
    return DB_SESSION.query(Filter).filter(Filter.uid == uid, Filter.fid == fid).count() > 0


def get_filter_data(uid: int, fid: int) -> Filter:   # получить данные фильтра
    return DB_SESSION.query(Filter).filter(Filter.uid == uid, Filter.fid == fid).first()


def get_filters(uid: int) -> List[Filter]:   # получить фильтры пользователя
    return DB_SESSION.query(Filter).filter(Filter.uid == uid).all()


def count_filters(uid: int) -> int:   # количество фильтров пользователя
    return DB_SESSION.query(Filter).filter(Filter.uid == uid).count()


def get_filters_for_notifies() -> List[Filter]:
    return DB_SESSION.query(Filter).filter(Filter.notify, Filter.notified == False).all()


async def clear_filters_to_notify(uid: int):
    for fi in get_filters(uid):
        fi.notified = False
    DB_SESSION.commit()


"""____________________________________ blank DB METHODS ____________________________________"""


def reg_blank(uid: int):   # зарегистрировать анкету (бланк)
    blank = Blank(uid=uid)
    DB_SESSION.add(blank)
    DB_SESSION.commit()


def delete_blank(uid: int, bid: int):   # удалить бланк
    DB_SESSION.delete(DB_SESSION.query(Blank).filter(Blank.uid == uid, Blank.bid == bid, Blank.exist_to_user).first())
    DB_SESSION.commit()


def is_blank_exist(uid: int, bid: int) -> bool:   # проверить существование анкеты
    return DB_SESSION.query(Blank).filter(Blank.uid == uid, Blank.bid == bid, Blank.exist_to_user).count() > 0


def is_blank_exist_sp(bid: int) -> bool:   # проверить существование анкеты только по его bid
    return DB_SESSION.query(Blank).filter(Blank.bid == bid, Blank.exist_to_user).count() > 0


def is_blank_exist_sp2(bid: int) -> bool:   # проверить существование анкеты только по его bid без учёта доступности
    return DB_SESSION.query(Blank).filter(Blank.bid == bid).count() > 0


def count_blanks(uid: int) -> int:   # посчитать анкеты пользователя
    return DB_SESSION.query(Blank).filter(Blank.uid == uid, Blank.exist_to_user).count()


def get_blanks(uid: int) -> List[Blank]:   # получить анкеты пользователя
    return DB_SESSION.query(Blank).filter(Blank.uid == uid, Blank.exist_to_user).all()


def get_blank(bid: int) -> Blank:   # получить анкету
    return DB_SESSION.query(Blank).filter(Blank.bid == bid, Blank.exist_to_user).first()


def count_lasts_blanks(uid: int) -> int:   # посчитать черновые бланки пользователя
    return DB_SESSION.query(Blank).filter(Blank.uid == uid, Blank.exist_to_user, Blank.finished == False).count()


"""____________________________________ pin DB METHODS ____________________________________"""


def is_blank_pinned(bid: int) -> bool:   # проверить закреплён ли бланк
    return DB_SESSION.query(Pin).filter(Pin.bid == bid).count() > 0


def is_blank_pinned_for_user(uid: int, bid: int) -> bool:   # закреплён ли бланк для определённого пользователя
    return DB_SESSION.query(Pin).filter(Pin.bid == bid, Pin.uid == uid).count() > 0


def pin(uid: int, bid: int):   # закрепить бланк
    pin = Pin(uid=uid, bid=bid)
    DB_SESSION.add(pin)
    DB_SESSION.commit()


def delete_pin(uid: int, pid: int):   # открепить бланк
    DB_SESSION.delete(DB_SESSION.query(Pin).filter(Pin.uid == uid, Pin.pid == pid).first())
    DB_SESSION.commit()


def get_pins(uid: int) -> List[Pin]:   # получить закрепы пользователя
    return DB_SESSION.query(Pin).filter(Pin.uid == uid).all()


def count_pins(uid: int) -> int:   # посчитать закрепы пользователя
    return DB_SESSION.query(Pin).filter(Pin.uid == uid).count()


"""____________________________________ search _DB METHODS ____________________________________"""


async def sp_find_blanks(uid: int, fid: int, enc: list):   # поиск бланков с очисткой списка
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
    ssl["search"]["query"] = list(map(lambda g: g.bid, sorted(list(bl), key=lambda g: (arpho.grate_similarity(g.fil_fand, fi.fil_fand), g.search_grate(fi.fil_blacklist, fi.fil_typ_dc, fi.fil_typ_ff)), reverse=const.SEARCH_REVERSE_F)))
    end = datetime.now()
    ssl["search"]["time"] = round((end - start).total_seconds() * 1000 + (end - start).microseconds / 1000, 4)
    ub.sp_dat = dumps(ssl)
    DB_SESSION.commit()


async def find_blanks(uid: int, fid: int, enc: list):   # поиск бланков с добавлением в список
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
    ssl["search"]["query"][ub.gbid:ub.gbid] = list(filter(lambda sd: sd not in ssl["search"]["query"], map(lambda g: g.bid, sorted(list(bl), key=lambda g: (arpho.grate_similarity(g.fil_fand, fi.fil_fand), g.search_grate(fi.fil_blacklist, fi.fil_typ_dc, fi.fil_typ_ff)), reverse=const.SEARCH_REVERSE_F))))
    end = datetime.now()
    ssl["search"]["time"] = round((end - start).total_seconds() * 1000 + (end - start).microseconds / 1000, 4)
    ub.sp_dat = dumps(ssl)
    DB_SESSION.commit()


def get_se_rez(ub: User, n: int) -> int | None:   # получить результат поиска
    ssl = loads(ub.sp_dat)
    return ssl["search"]["query"][ub.gbid] if 0 <= n < len(ssl["search"]["query"]) else None


def find_in_se(ub: User, bid: int):   # получить номер бланка в поиске
    ssl = loads(ub.sp_dat)
    return ssl["search"]["query"].index(bid) if bid in ssl["search"]["query"] else None


def clear_sl(ub: User):   # очистить результаты поиска
    ssl = loads(ub.sp_dat)
    ssl["search"]["query"] = []
    ub.sp_dat = dumps(ssl)
    DB_SESSION.commit()


async def search_to_notify(bid: int, notify_func, timed_func):
    bl = get_blank(bid)
    uids = []
    for fi in get_filters_for_notifies():
        corp = bl.search_grate(fi.fil_blacklist, fi.fil_typ_dc, fi.fil_typ_ff, limited=True) if fi.fil_typ_ff is not None else 1
        if corp >= const.FILTER_NOTIFY_LIMIT and arpho.grate_similarity(bl.fil_fand, fi.fil_fand) >= const.DES_CORR_LIMIT:
            if fi.uid not in uids:
                asyncio.create_task(notify_func(fi.uid, "Уведомление от одного из ваших фильтров, хотите посмотреть?", [{"text": "открыть", "callback_data": f"$do#openblank^{bl.bid}"}]))
                uids.append(fi.uid)
    if uids:
        asyncio.create_task(timed_func(bl.uid, f"О вашем бланке уже знают {len(uids)} {arpho.agree_with_number('пользователь', len(uids))}.", 10))


"""____________________________________ membership + chat DB METHODS ____________________________________"""


def reg_membership(uid: int, chid: int, owner=False):   # добавить члена чата
    ch = ChatMember(uid=uid, chid=chid, is_owner=owner, nickname=get_user_data(uid).nickname)
    DB_SESSION.query(Chat).filter(Chat.chid == chid).first().members_co += 1
    DB_SESSION.add(ch)
    DB_SESSION.commit()


def reg_chat(uid: int, name: str) -> int:   # зарегистрировать чат
    c = Chat(title=name.lstrip("$"), is_writable=name.startswith("$"))
    DB_SESSION.add(c)
    DB_SESSION.commit()
    if not name.startswith("$"):
        reg_message(c.chid, uid, name)
    reg_membership(uid, c.chid, True)
    return c.chid


def get_games(uid: int) -> List[ChatMember]:   # получить все доступные пользователю игры
    return DB_SESSION.query(ChatMember).filter(ChatMember.uid == uid).all()


def count_games(uid: int) -> int:   # посчитать количество доступных игр
    return DB_SESSION.query(ChatMember).filter(ChatMember.uid == uid).count()


def get_membership(uid: int, chid: int) -> ChatMember:   # получить данные участника чата
    return DB_SESSION.query(ChatMember).filter(ChatMember.uid == uid, ChatMember.chid == chid).first()


def get_chat_data(chid: int) -> Chat:   # получить данные чата
    return DB_SESSION.query(Chat).filter(Chat.chid == chid).first()


def get_waitingers(chid: int) -> List[ChatMember]:   # получить ожидающих принятия в чат
    return DB_SESSION.query(ChatMember).filter(ChatMember.chid == chid, ChatMember.accepted != True, ChatMember.is_owner != True).all()


def count_waitingers(chid: int) -> int:   # посчитать ожидающих принятия в чат
    return DB_SESSION.query(ChatMember).filter(ChatMember.chid == chid, ChatMember.accepted != True, ChatMember.is_owner != True).count()


async def clear_messages(chid: int):   # очистить сообщения чата
    for i in DB_SESSION.query(Message).filter(Message.chid == chid).all():
        DB_SESSION.delete(i)
    DB_SESSION.commit()


async def reduce_blanks(chid: int):   # снять с публикации анкеты к которым привязан чат
    for bl in get_chat_binded(chid):
        bl.publ = False
    DB_SESSION.commit()


def del_chat(chid: int):   # удалить чат
    DB_SESSION.delete(DB_SESSION.query(Chat).filter(Chat.chid == chid).first())
    DB_SESSION.commit()
    asyncio.create_task(reduce_blanks(chid))
    asyncio.create_task(clear_messages(chid))


def del_member(uid: int, chid: int):   # удалить участие в чате
    chat = get_chat_data(chid)
    chat.members_co -= 1
    if chat.members_co < 1:
        del_chat(chid)
    DB_SESSION.delete(DB_SESSION.query(ChatMember).filter(ChatMember.uid == uid, ChatMember.chid == chid).first())
    for bl in get_chat_binded_for_user(chid, uid):
        bl.publ = False
    DB_SESSION.commit()


def is_membership_exist(uid: int, chid: int) -> bool:   # проверить наличие членства в чате
    return DB_SESSION.query(ChatMember).filter(ChatMember.uid == uid, ChatMember.chid == chid).count() > 0


def get_memberships(chid: int) -> List[ChatMember]:   # получить участников чата
    return DB_SESSION.query(ChatMember).filter(ChatMember.chid == chid).all()


def is_chat_exist(chid: int) -> bool:   # проверить существование чата
    return DB_SESSION.query(Chat).filter(Chat.chid == chid).count() > 0


def is_message_exist(chid: int, mid: int) -> bool:   # проверить существование сообщения
    return DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid == mid).count() > 0


def is_messages_exist(chid: int) -> bool:   # проверить наличие сообщений в чате
    return DB_SESSION.query(Message).filter(Message.chid == chid).count() > 0


def count_messages(chid: int) -> int:   # посчитать сообщения
    return DB_SESSION.query(Message).filter(Message.chid == chid).count()


def is_next_message_exist(chid: int, mid: int) -> bool:   # существует ли следующее сообщение
    return DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid > mid).count() > 0


def is_before_message_exist(chid: int, mid: int) -> bool:   # существует ли предыдущее сообщение
    return DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid < mid).count() > 0


def get_next_message_id(chid: int, mid: int) -> int:   # получить id следующего сообщения
    return DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid > mid).first().mid


def get_before_message_id(chid: int, mid: int) -> int:   # получить id предыдущего сообщения
    return DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid < mid).all()[-1].mid


def get_all_messages(chid: int) -> List[Message]:   # получить все сообщения
    return DB_SESSION.query(Message).filter(Message.chid == chid).all()


def get_first_message_id(chid: int) -> int:   # получить id первого сообщения
    return DB_SESSION.query(Message).filter(Message.chid == chid).first().mid


def reg_message(chid: int, uid: int, text: str):   # добавить сообщение
    chat = get_chat_data(chid)
    chat.last_sended = datetime.now()
    for mt in arpho.split_string(text, const.MAX_MESSAGE_LEN):
        ms = Message(chid=chid, uid=uid, text=mt)
        chat.messages_co += 1
        DB_SESSION.add(ms)
    DB_SESSION.commit()


def del_message(chid: int, mid: int):   # удалить сообщение
    DB_SESSION.delete(DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid == mid).first())
    get_chat_data(chid).messages_co -= 1
    DB_SESSION.commit()


def get_message(chid: int, mid: int) -> Message:   # получить сообщение
    return DB_SESSION.query(Message).filter(Message.chid == chid, Message.mid == mid).first()


def should_notify_user(uid: int, from_chid: int) -> bool:   # проверить следует ли уведомить пользователя
    mb = get_membership(uid, from_chid)
    if mb.notified:
        return False
    mb.notified = True
    DB_SESSION.commit()
    return True


def clear_should_notify_user(uid: int):   # очистить флаг уведомления пользователя
    for memb in get_games(uid):
        memb.notify = False
    DB_SESSION.commit()


def chat_binded_count(chid: int) -> int:   # проверить к скольким анкетам привязан чат
    return DB_SESSION.query(Blank).filter(Blank.chid == chid, Blank.exist_to_user, Blank.finished, Blank.publ).count()


def get_chat_binded(chid: int) -> List[Blank]:   # получить бланки привязанные к чату
    return DB_SESSION.query(Blank).filter(Blank.chid == chid, Blank.exist_to_user, Blank.finished, Blank.publ).all()


def get_chat_binded_for_user(chid: int, uid: int) -> List[Blank]:   # получить бланки привязанные к чату для пользователя
    return DB_SESSION.query(Blank).filter(Blank.chid == chid, Blank.uid == uid, Blank.exist_to_user, Blank.finished, Blank.publ).all()


async def _manage_atc():   # очистка лишних скомпилированных историй
    ldd = listdir(const.ROUTE_TO_CHAT_BUILD)
    while len(ldd) > 1:
        remove(f"{const.ROUTE_TO_CHAT_BUILD}/{ldd.pop(0)}")


async def build_story(chid: int) -> str:   # скомпилировать историю
    ch = get_chat_data(chid)
    path = f"{const.ROUTE_TO_CHAT_BUILD}/chat_rv2_{chid}_{ch.messages_co}_{ch.last_sended.strftime('%d,%m,%Y | %H:%M:%S')}.txt"
    if isfile(path):
        return path
    memb = get_memberships(chid)
    msgs = get_all_messages(chid)
    with open(file=path, encoding=const.ENCODING, mode="w+") as file:
        topik = f"[сгенерировано на основе чата '{ch.title}' ({chid})]\n" \
                f"в ролях: {list(map(lambda g: g.nickname, memb))}\n" \
                f"постов: {ch.messages_co}\n" \
                f"последнее сообщение: {ch.last_sended.strftime('%d.%m.%Y | %H:%M:%S')}\n" \
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
