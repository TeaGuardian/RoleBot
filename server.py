from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters import IDFilter
from source.builders import *
from os.path import getsize
from copy import deepcopy
import asyncio
import sys
from time import time


class Timer:
    def __init__(self, tick):
        self.tick, self.last = tick, datetime.now() - timedelta(seconds=tick)

    def tk(self):
        if (datetime.now() - self.last) > timedelta(seconds=self.tick):
            self.last = datetime.now()
            return True
        return False


dp = Dispatcher(bot)
RUN = True
DATA = get_bot_backup()
BAN_FILTER = IDFilter(user_id=DATA["banned_ips"])


timeC = Timer(180)
dpp = {"$sp^pg": "PG",
       "$sp^pg15": "PG-15",
       "$sp^r": "R",
       "$sp^nc17": "NC-17",
       "$sp^male": "муж.",
       "$sp^feml": "жен.",
       "$sp^nstd": "обсудим",
       None: "---"}


def finish_bot_workspace():
    save_bot_backup(DATA)
    sys.exit()


def write_log(log, obj):
    re = f"{datetime.now().strftime('%d.%m.%Y | %H:%M:%S')} [{obj}] >>> {log}\n"
    print(re)
    with open(const.ROUTE_TO_LOGS, mode="a+", encoding=const.ENCODING) as fi:
        fi.writelines(re)


async def send_logs(admins):
    for uid in admins:
        await bot.send_document(uid, document=open("data/logs.txt", mode="rb"))
    with open(const.ROUTE_TO_LOGS, mode="w+", encoding=const.ENCODING) as fi:
        fi.write("")


@dp.errors_handler()
async def errors_handler(update, exception):
    exp = f"\n--> type: {type(exception).__name__}\n" \
          f"--> message: {exception}\n" \
          f"--> traceback: {exception.args}\n" \
          f"--> context: {exception.__context__}\n" \
          f"--> cause: {exception.__cause__}\n" \
          f"--> update: {update}"
    write_log(exp, f"exception")
    if getsize(const.ROUTE_TO_LOGS) > const.SIZE_LIMIT:
        await send_logs([const.ADMIN])


@dp.message_handler(BAN_FILTER)
async def _ignore_users(message: types.Message):
    pass


@dp.message_handler(commands=['start'])
async def _start(message: types.Message):
    asyncio.create_task(delete_message(message))
    bt, tt = build_menu(message.from_user, bot, "$root#start")
    tid = await bot.send_message(message.from_user.id, tt, reply_markup=bt)
    if is_user_exist(message.from_user.id):
        user = get_user_data(message.from_user.id)
        try:
            await bot.delete_message(message.from_user.id, user.mmid)
        except Exception as e:
            pass
        user.mmid = tid.message_id
        confirm_data_editing()
    else:
        write_log(f"{message.from_user.id}, pressed stsrt! waiting connection", obj="f-START command")


@dp.message_handler(commands=['main_notification'])
async def _main_notification(message: types.Message):
    if is_user_have_role(message.from_user.id, "admin"):
        write_log(message.html_text, f"main_notification started by {message.from_user.id}")
        for role in const.ROLES:
            for user in get_users_by_role(role):
                try:
                    await bot.send_message(user.uid, message.html_text.lstrip('main_notification'),
                                           reply_markup=special_but_conv([[{"text": "скрыть уведомление", "callback_data": "$delite_this_message"}]]),
                                           disable_notification=not user.notify_i)
                except Exception as e:
                    await errors_handler("main_notification", e)
        asyncio.create_task(send_message_timed(message.from_user.id, "завершено!", 10))


@dp.message_handler(commands=['shutdown'])
async def _turn_off(message: types.Message):
    global RUN, timeC
    if is_user_have_role(message.from_user.id, "admin") and timeC.tk():
        RUN = False
        await bot.send_message(message.from_user.id, "goodby")
        write_log("turning off server", f"SERVER ({message.from_user.id})")
        finish_bot_workspace()


@dp.message_handler(commands=['logs'])
async def _send_logs_h(message: types.Message):
    global RUN, timeC
    asyncio.create_task(delete_message(message))
    if is_user_have_role(message.from_user.id, "admin"):
        await send_logs(list(map(lambda g: g.uid, get_users_by_role("admin"))))


@dp.message_handler(commands=['help'])
async def _help_f(message: types.Message):
    await bot.send_message(message.from_user.id, const.help_mes, parse_mode=types.ParseMode.HTML, reply_markup=special_but_conv([[{"text": "скрыть подсказку", "callback_data": "$delite_this_message"}]]))
    asyncio.create_task(delete_message(message))


@dp.message_handler(commands=['cancel'])
async def _cancel(message: types.Message):
    if is_user_exist(message.from_user.id):
        user = get_user_data(message.from_user.id)
        if user.state == "bugreport":
            asyncio.create_task(delete_message(await bot.send_message(message.from_user.id, "отменено")))
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
            user.state = ""
            confirm_data_editing()
    asyncio.create_task(delete_message(message, 6))


@dp.message_handler(commands=['download'])
async def _download_h(message: types.Message):
    if is_user_exist(message.from_user.id):
        user = get_user_data(message.from_user.id)
        games = get_games(user.uid)
        if games and len(games) > user.gsel:
            if games[user.gsel].accepted or games[user.gsel].is_owner:
                asyncio.create_task(send_message_timed(message.from_user.id, "ожидайте, идёт компиляция истории", 6))
                doc = await build_story(games[user.gsel].chid)
                await bot.send_document(message.from_user.id, document=open(doc, mode="rb"))
            else:
                asyncio.create_task(send_message_timed(message.from_user.id, "простите, но вы не можете скачивать эту историю", 10))
    asyncio.create_task(delete_message(message))


@dp.message_handler(commands=['SetNickname'])
async def _change_nickname(message: types.Message):
    if is_user_exist(message.from_user.id):
        get_user_data(message.from_user.id).state = "SetNickname"
        confirm_data_editing()
        if 15 + const.MAX_TITLES_LEN > len(message.text) > 13:
            message.text = message.text.lstrip("/SetNickname")
            await _catch(message, summoned=True)
        else:
            asyncio.create_task(send_message_timed(message.from_user.id, f"Введите новый никнейм (не более {const.MAX_TITLES_LEN} символов).", 6))
    asyncio.create_task(delete_message(message))


@dp.message_handler(commands=['SetLocalNickname'])
async def _change_local_nickname(message: types.Message):
    if is_user_exist(message.from_user.id) and len(get_games(message.from_user.id)):
        get_user_data(message.from_user.id).state = "SetLocalNickname"
        confirm_data_editing()
        if 20 + const.MAX_TITLES_LEN > len(message.text) > 18:
            message.text = message.text.lstrip("/SetLocalNickname")
            await _catch(message, summoned=True)
        else:
            asyncio.create_task(send_message_timed(message.from_user.id, f"Введите новый никнейм (не более {const.MAX_TITLES_LEN} символов).", 6))
    else:
        asyncio.create_task(send_message_timed(message.from_user.id, "У вас нет игр.", 6))
    asyncio.create_task(delete_message(message))


@dp.callback_query_handler()
async def _process_callback(callback_query: types.CallbackQuery):
    global dpp
    if callback_query.data == "$delite_this_message":
        try:
            await callback_query.message.delete()
        except Exception as e:
            asyncio.create_task(send_message_timed(callback_query.from_user.id, "Извините, это сообщение можете удалить только вы.", 2))
        return False
    if time() - callback_query.message.date.timestamp() >= 60 * 60 * 24 * 1.8:
        asyncio.create_task(send_message_timed(callback_query.from_user.id, "Простите, это меню устарело, удалите его и выберите /start .", 20))
        return False
    if is_user_exist(callback_query.from_user.id):
        user = get_user_data(callback_query.from_user.id)
        if callback_query.message.message_id != user.mmid and user.mmid:
            try:
                await bot.delete_message(callback_query.message.chat.id, user.mmid)
            except:
                pass
        user.mmid = callback_query.message.message_id
        user.last_active = datetime.now()
        confirm_data_editing()
        if callback_query.data == "register":
            callback_query.data = "$root#start"
        if callback_query.data in dpp.keys():
            user.last_message = callback_query.data
        if callback_query.data.startswith("$do#sp#cl:"):
            cus = callback_query.data.split(":")[1]
            ccs = get_user_data(int(cus))
            if not get_membership(int(cus), get_games(user.uid)[user.gsel].chid).accepted:
                asyncio.create_task(delete_message(await bot.send_message(callback_query.from_user.id, "вы отклонили заявку", disable_notification=not ccs.notify_c), 6))
                await bot.send_message(ccs.uid, "ваша заявка отклонена", disable_notification=not ccs.notify_c, reply_markup=special_but_conv([[{"text": "скрыть уведомление", "callback_data": "$delite_this_message"}]]))
                del_member(ccs.uid, get_games(user.uid)[user.gsel].chid)
                callback_query.data = "$root#games"
        if callback_query.data.startswith("$do#sp#ac:"):
            cus = callback_query.data.split(":")[1]
            ccs = get_user_data(int(cus))
            if not get_membership(int(cus), get_games(user.uid)[user.gsel].chid).accepted:
                asyncio.create_task(delete_message(await bot.send_message(callback_query.from_user.id, "вы одобрили заявку", disable_notification=not ccs.notify_c), 6))
                await bot.send_message(ccs.uid, "ваша заявка одобрена", disable_notification=not ccs.notify_c, reply_markup=special_but_conv([[{"text": "скрыть уведомление", "callback_data": "$delite_this_message"}]]))
                get_membership(ccs.uid, get_games(user.uid)[user.gsel].chid).accepted = True
                confirm_data_editing()
                callback_query.data = "$root#games"
    if callback_query.data not in ["$root#rates", "$do#bugreport"]:
        bt, tt = build_menu(callback_query.from_user, bot, callback_query.data, in_bt=callback_query.message.reply_markup, in_tt=callback_query.message.html_text)
        if (bt is None and tt is None) or (bt == callback_query.message.reply_markup and tt == callback_query.message.text):
            return 1
        await callback_query.message.edit_text(tt, reply_markup=bt)
    elif callback_query.data == "$do#bugreport" and is_user_exist(callback_query.from_user.id):
        ub = get_user_data(callback_query.from_user.id)
        if datetime.now() - ub.last_call > timedelta(minutes=const.LAST_SEND_DELAY):
            ub.state = "bugreport"
            mes = await bot.send_message(callback_query.from_user.id, "введите сообщение для отправки или /cancel")
        else:
            mes = await bot.send_message(callback_query.from_user.id, f"ещё не прошло {const.LAST_SEND_DELAY} минут с последней отправки")
        asyncio.create_task(delete_message(mes, 5))
    if not is_user_exist(callback_query.from_user.id):
        await callback_query.message.delete()


@dp.message_handler()
async def _catch(message: types.Message, summoned=False):
    if is_user_exist(message.from_user.id):
        if len(message.text) < 2:
            message.text = ""
        user = get_user_data(message.from_user.id)
        user.last_message = message.text
        user.last_active = datetime.now()
        qr = types.CallbackQuery()
        qr.from_user = deepcopy(message.from_user)
        qr.message = deepcopy(message)
        qr.message.message_id = user.mmid
        if user.state == "bugreport":
            t = f"bugreport from {message.from_user.id}: {message.text}"
            await bot.send_message(const.ADMIN, t)
            write_log(t, "bugreport - @" + message.from_user.username)
            mes = await bot.send_message(message.from_user.id, "отправлено")
            asyncio.create_task(delete_message(mes))
            user.state = ""
            user.last_call = datetime.now()
            confirm_data_editing()
        bt, tt = build_menu(message.from_user, bot, message.text)
        if bt is not None and len(tt):
            await bot.edit_message_text(text=tt, chat_id=message.from_user.id, message_id=user.mmid, reply_markup=bt)
        if user.state == "SetNickname":
            user.state = ""
            if len(message.text) > const.MAX_TITLES_LEN:
                asyncio.create_task(delete_message(await bot.send_message(message.from_user.id, f"Слишком длинное ({len(message.text)} / {const.MAX_TITLES_LEN}).")))
            else:
                user.nickname = message.text
                qr.data = "$root#settings"
                asyncio.create_task(send_message_timed(message.from_user.id, "Готово.", 3))
                await _process_callback(qr)
            confirm_data_editing()
        if user.state == "SetLocalNickname":
            ga = get_games(user.uid)
            user.state = ""
            if len(ga) > user.gsel >= 0:
                if len(message.text) > const.MAX_TITLES_LEN:
                    asyncio.create_task(delete_message(await bot.send_message(message.from_user.id, f"Слишком длинное ({len(message.text)} / {const.MAX_TITLES_LEN}).")))
                else:
                    asyncio.create_task(delete_message(await bot.send_message(message.from_user.id, "Готово.")))
                    get_membership(user.uid, ga[user.gsel].chid).nickname = message.text if message.text and message.text not in ["None", "none"] else None
                    qr.data = "$root#games"
                    await _process_callback(qr)
                confirm_data_editing()
        if user.game_f and len(message.text) >= 2:
            chat = get_games(user.uid)[user.gsel]
            if not get_chat_data(chat.chid).is_writable:
                asyncio.create_task(delete_message(await bot.send_message(message.from_user.id, "чат не для общения")))
                asyncio.create_task(delete_message(message, 1))
                return False
            fl = is_next_message_exist(chat.chid, chat.cursor)
            try:
                reg_message(get_games(user.uid)[user.gsel].chid, user.uid, message.html_text)
                asyncio.create_task(delete_message(await bot.send_message(message.from_user.id, "отправлено")))
                for memb in get_memberships(chat.chid):
                    if is_user_exist(memb.uid) and memb.notify and (memb.accepted or memb.is_owner):
                        if should_notify_user(memb.uid, chat.chid):
                            await bot.send_message(memb.uid, f"у вас есть непрочитанные сообщения в '{chat.title}'", reply_markup=special_but_conv([[{"text": "скрыть уведомление", "callback_data": "$delite_this_message"}]]))
            except Exception as e:
                asyncio.create_task(delete_message(await bot.send_message(message.from_user.id, "что-то пошло не так"), 20))
            if not fl and is_next_message_exist(chat.chid, chat.cursor):
                bt, tt = build_menu(message.from_user, bot, "$do#chat+1")
                if bt is None and tt is None:
                    return 1
                await bot.edit_message_text(text=tt, chat_id=message.from_user.id, message_id=user.mmid, reply_markup=bt)
    if not summoned:
        asyncio.create_task(delete_message(message, 6))


def infinity_run():
    global RUN
    RUN = True
    while RUN:
        if timeC.tk():
            try:
                write_log("starting server", "SERVER")
                executor.start_polling(dp, skip_updates=False)
            except Exception as ex:
                print(ex)
                if RUN:
                    write_log(ex.__str__(), "SERVER-ERROR!")


if __name__ == "__main__":
    '''
    pip install --force-reinstall -v "aiogram==2.23.1"
    '''
    infinity_run()
