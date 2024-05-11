import asyncio
from .db_trans import *
from aiogram import types, Bot
from datetime import datetime, timedelta
bot = Bot(token=const.API, parse_mode=types.ParseMode.HTML)


def special_but_conv(data):
    keyboard = types.InlineKeyboardMarkup(row_width=len(data[0]))
    for row in data:
        row_buttons = []
        for button_data in row:
            text = button_data["text"]
            callback_data = button_data["callback_data"] if "callback_data" in button_data.keys() else None
            url = button_data["url"] if "url" in button_data.keys() else None
            if text == "" and url is None:
                continue
            button = types.InlineKeyboardButton(text=text, callback_data=callback_data, url=url)
            row_buttons.append(button)
        keyboard.row(*row_buttons)
    return keyboard


async def delete_message(message: types.Message, time=3):
    await asyncio.sleep(time)
    await message.delete()


async def send_message(uid: int, text: str, notify=None):
    await bot.send_message(uid, text, disable_notification=notify)


async def send_message_timed(uid: int, text: str, time=20):
    await delete_message(await bot.send_message(uid, text), time)


async def hideable_message(uid: int, text: str, buttons=()):
    await bot.send_message(uid, text, reply_markup=special_but_conv([[{"text": "скрыть уведомление", "callback_data": "$delite_this_message"}, *buttons]]))


dpp = {"$sp^pg": "PG",
       "$sp^pg15": "PG-15",
       "$sp^r": "R",
       "$sp^nc17": "NC-17",
       "$sp^male": "муж.",
       "$sp^feml": "жен.",
       "$sp^nstd": "обсудим",
       None: "---"}
_sp1 = [{"text": "оценки ⭐️", "callback_data": "$root#rates"},
        {"text": "удали 🗑", "callback_data": "$root#delite_profile"}]
_sp2 = [{"text": "оценки ⭐️", "callback_data": "$root#rates"},
        {"text": "ДА, удали", "callback_data": "$root#delite_profile"},
        {"text": "НЕТ, не надо", "callback_data": "$root#delite_p_f"}]


def build_menu(user_obj, bot: Bot, call="", in_bt=None, in_tt=None):
    text, buttons, agr, upd_b = "", None, "✅", []
    uid = user_obj.id

    def _rv_addnot(ub: User):
        nonlocal call
        ub.notify_a = not ub.notify_a
        confirm_data_editing()
        call = "$root#settings"

    def _rv_gamenot(ub: User):
        nonlocal call
        ub.notify_c = not ub.notify_c
        confirm_data_editing()
        call = "$root#settings"

    def _rv_adminot(ub: User):
        nonlocal call
        ub.notify_i = not ub.notify_i
        confirm_data_editing()
        call = "$root#settings"

    def _rv_delprof(ub: User):
        nonlocal call
        if ub.delete_p:
            delete_user(ub.uid)
        else:
            ub.delete_p = True
            confirm_data_editing()
        call = "$root#settings"

    def _rv_del_prof_f(ub: User):
        nonlocal call
        ub.delete_p = False
        confirm_data_editing()
        call = "$root#settings"

    """ <-------------------------------- blank methods -------------------------------->"""

    def _rv_show_bl(ub: User, des=""):
        nonlocal text, agr, call
        global dpp
        bl = get_blanks(ub.uid)
        if len(bl) <= 0:
            text = const.choice(const._ft_nr) + "\n\nУ вас пока нет анкет."
        else:
            if ub.mbid >= len(bl):
                ub.mbid = len(bl) - 1
            if ub.mbid < 0:
                ub.mbid = 0
            b = bl[ub.mbid]
            if not b.finished and b.publ:
                b.publ = False
                confirm_data_editing()
            agr = "❌" if not b.publ else "✅"
            text = f"бланк {ub.mbid + 1} / {len(bl)} ({'активно' if b.publ else 'черновик'})\n" \
                   f"имя: {b.fil_name} ({dpp[b.fil_ypol]})\n" \
                   f"фандом: {b.fil_fand}\n" \
                   f"теги: {b.fil_typ}\n" \
                   f"искомый: {b.fil_tmp}\n" \
                   f"рейтинг: {dpp[b.fil_rate]}\n" \
                   f"просмотры: {b.views}\n" \
                   f"описание: {des if des else b.fil_des}\n" \
                   f"чат: {b.fil_chat}\n" \
                   f"👍 {b.score_pl} | {round(b.score_pl / (b.score_pl + b.score_mi) * 100, 1) if (b.score_pl + b.score_mi) else 0}% | 👎 {b.score_mi}"

    def _rv_add_bl(ub: User):
        nonlocal call
        if count_blanks(ub.uid) >= const.MAX_COUNT_OF_BLANKS:
            call = "$root#blanks"
            asyncio.create_task(send_message_timed(ub.uid, "превышено максимальное количество бланков"))
        else:
            reg_blank(ub.uid)
            ub.mbid = count_blanks(ub.uid) - 1
            ub.beid_f = True
            confirm_data_editing()
            call = "$blank#edit"

    def _rv_ac_bl_ed(ub: User):
        bl = get_blanks(ub.uid)
        if len(bl):
            if ub.mbid >= len(bl):
                ub.mbid = len(bl) - 1
            if ub.mbid < 0:
                ub.mbid = 0
            if is_blank_exist(ub.uid, bl[ub.mbid].bid):
                ub.beid_f = True
                bl[ub.mbid].state = 0
            confirm_data_editing()

    def _rv_bl_pl(ub: User):
        nonlocal call
        bl = get_blanks(ub.uid)
        ub.mbid += 1
        if len(bl):
            if ub.mbid >= len(bl):
                ub.mbid = len(bl) - 1
            if ub.mbid < 0:
                ub.mbid = 0
        _rv_show_bl(ub)
        confirm_data_editing()
        call = "$root#blanks"

    def _rv_bl_mi(ub: User):
        nonlocal call
        bl = get_blanks(ub.uid)
        ub.mbid -= 1
        if len(bl):
            if ub.mbid >= len(bl):
                ub.mbid = len(bl) - 1
            if ub.mbid < 0:
                ub.mbid = 0
        _rv_show_bl(ub)
        confirm_data_editing()
        call = "$root#blanks"

    def _rv_bl_del(ub: User):
        nonlocal call
        bl = get_blanks(ub.uid)
        if len(bl):
            if ub.mbid >= len(bl):
                ub.mbid = len(bl) - 1
            if ub.mbid < 0:
                ub.mbid = 0
            if is_blank_pinned(bl[ub.mbid].bid):
                bl[ub.mbid].exist_to_user = False
                confirm_data_editing()
            else:
                delete_blank(ub.uid, bl[ub.mbid].bid)
        _rv_show_bl(ub)
        call = "$root#blanks"

    def _rv_bl_sk(ub: User):
        nonlocal call
        bl = get_blanks(ub.uid)
        if len(bl) and ub.beid_f and bl[ub.mbid].state < len(const.blank_questions):
            bl[ub.mbid].state += 1
            if bl[ub.mbid].state >= len(const.blank_questions):
                ub.beid_f = False
        else:
            ub.beid_f = False
        confirm_data_editing()
        call = "$do#skip_be"

    def _rv_bl_edit(ub: User):
        nonlocal text, upd_b, call
        bl = get_blanks(ub.uid)
        if len(bl):
            if ub.mbid >= len(bl):
                ub.mbid = len(bl) - 1
            if ub.mbid < 0:
                ub.mbid = 0
            b = bl[ub.mbid]
            b.publ = False
            acs = True
            if call == "$do#accept_be":
                if b.state >= 7:
                    b.state = 0
                    ub.beid_f = False
                    b.finished = False
                    _rv_show_bl(ub)
                    confirm_data_editing()
                    call = "$root#blanks"
                    return 1
                if b.state == 0:
                    upd_b.append([{"text": "муж.", "callback_data": "$sp^male"},
                                  {"text": "жен.", "callback_data": "$sp^feml"},
                                  {"text": "обсудим", "callback_data": "$sp^nstd"}])
                    upd_b.append([{"text": "✅", "callback_data": "$do#accept_be"},
                                  {"text": "🔙", "callback_data": "$root#blanks"}])
                elif b.state == 5:
                    upd_b.append([{"text": "PG", "callback_data": "$sp^pg"},
                                  {"text": "PG-15", "callback_data": "$sp^pg15"},
                                  {"text": "R", "callback_data": "$sp^r"},
                                  {"text": "NC-17", "callback_data": "$sp^nc17"}])
                    upd_b.append([{"text": "✅", "callback_data": "$do#accept_be"},
                                  {"text": "🔙", "callback_data": "$root#blanks"}])
                else:
                    upd_b.append([{"text": "✅", "callback_data": "$do#accept_be"},
                                  {"text": "🔙", "callback_data": "$root#blanks"}])
            elif b.state == 0 and const.MIN_LINE_LEN <= len(call) <= const.MAX_TITLES_LEN and "$" not in call:
                b.fil_name = call
                upd_b.append([{"text": "муж.", "callback_data": "$sp^male"},
                              {"text": "жен.", "callback_data": "$sp^feml"},
                              {"text": "обсудим", "callback_data": "$sp^nstd"}])
                upd_b.append([{"text": "✅", "callback_data": "$do#accept_be"},
                              {"text": "🔙", "callback_data": "$root#blanks"}])
            elif b.state == 1 and call in ["$sp^male", "$sp^feml", "$sp^nstd"]:
                b.fil_ypol = call
                upd_b.append([{"text": "✅", "callback_data": "$do#accept_be"},
                              {"text": "🔙", "callback_data": "$root#blanks"}])
            elif b.state == 2 and const.MIN_LINE_LEN <= len(call) <= const.MAX_TITLES_LEN and "$" not in call:
                b.fil_fand = call
                upd_b.append([{"text": "✅", "callback_data": "$do#accept_be"},
                              {"text": "🔙", "callback_data": "$root#blanks"}])
            elif b.state == 3 and const.MIN_LINE_LEN <= len(call) <= const.MAX_TEG_LINE_LEN and "$" not in call:
                b.fil_typ = call
                upd_b.append([{"text": "✅", "callback_data": "$do#accept_be"},
                              {"text": "🔙", "callback_data": "$root#blanks"}])
            elif b.state == 4 and const.MIN_LINE_LEN <= len(call) <= const.MAX_TEG_LINE_LEN and "$" not in call:
                b.fil_tmp = call
                upd_b.append([{"text": "✅", "callback_data": "$do#accept_be"},
                              {"text": "🔙", "callback_data": "$root#blanks"}])
            elif b.state == 5 and const.MIN_LINE_LEN <= len(call) <= const.MAX_BLANK_DES_LEN and "$" not in call:
                b.fil_des = call
                upd_b.append([{"text": "PG", "callback_data": "$sp^pg"},
                              {"text": "PG-15", "callback_data": "$sp^pg15"},
                              {"text": "R", "callback_data": "$sp^r"},
                              {"text": "NC-17", "callback_data": "$sp^nc17"}])
                upd_b.append([{"text": "✅", "callback_data": "$do#accept_be"},
                              {"text": "🔙", "callback_data": "$root#blanks"}])
            elif b.state == 6 and call in ["$sp^pg", "$sp^pg15", "$sp^r", "$sp^nc17"]:
                b.fil_rate = call
                upd_b.append([{"text": "✅", "callback_data": "$do#accept_be"},
                              {"text": "🔙", "callback_data": "$root#blanks"}])
            elif b.state == 7 and const.MIN_LINE_LEN <= len(call) <= const.MAX_TITLES_LEN:
                b.fil_chat = call
                ub.beid_f = False
                b.finished = True
                confirm_data_editing()
                _rv_show_bl(ub)
                call = "$root#blanks"
                return 1
            else:
                acs = False
            if acs:
                b.state = b.state + 1
                confirm_data_editing()
            _rv_show_bl(ub)
            text += "\n\n" + const.blank_questions[b.state]["question"]()
            ub.beid_f = True
            if b.state > 7:
                ub.beid_f = False
        else:
            ub.beid_f = False
        confirm_data_editing()

    def _rv_bl_ac(ub: User):
        nonlocal text, call
        bl = get_blanks(ub.uid)
        if len(bl):
            if ub.mbid >= len(bl):
                ub.mbid = len(bl) - 1
            if ub.mbid < 0:
                ub.mbid = 0
            b = bl[ub.mbid]
            _rv_show_bl(ub)
            if all(map(lambda g: g is not None and len(g) >= 1, [b.fil_name, b.fil_ypol, b.fil_fand, b.fil_typ, b.fil_tmp, b.fil_des, b.fil_rate, b.fil_chat])):
                b.finished = True
            if not b.publ:
                if b.finished:
                    dt, tt = arpho.check_text(b.fil_des)
                    allp, nu, fo, ru, ot = dt
                    allp = allp if allp else 1
                    if (1 - ot / allp) >= const.DES_CORR_LIMIT and (1 - fo / allp) >= const.DES_RUSN_LIMIT:
                        if b.chid is None or ub.state != "bind_blank":
                            b.chid = reg_chat(ub.uid, b.fil_chat)
                        else:
                            if count_games(ub.uid) >= const.MAX_COUNT_OF_GAMES:
                                asyncio.create_task(send_message_timed(ub.uid, "Превышено максимальное количество игр, привязка невозможна."))
                                b.publ = False
                                b.views = 0
                                confirm_data_editing()
                                _rv_show_bl(ub)
                                ub.state = ""
                                call = "$root#blanks"
                                return 0
                            else:
                                b.chid = get_games(ub.uid)[ub.gsel].chid
                                asyncio.create_task(send_message_timed(ub.uid, "Анкета успешно привязана к существующему чату."))
                        b.publ = True
                        b.views = 0
                        confirm_data_editing()
                        _rv_show_bl(ub)
                        asyncio.create_task(search_to_notify(b.bid, hideable_message, send_message_timed))
                    else:
                        if ub.state == "bind_blank":
                            asyncio.create_task(send_message_timed(ub.uid, "Привязка невозможна, бланк не завершён."))
                        _rv_show_bl(ub, des=tt)
                        if (1 - ot / allp) < const.DES_CORR_LIMIT:
                            text += "\n\n" + f"Ваш текст адекватен лишь на {round(1 - ot / allp, 3)}, необходимо минимум {const.DES_CORR_LIMIT}."
                        if (1 - fo / allp) < const.DES_RUSN_LIMIT:
                            text += "\n" + f"Ваш текст на {round(1 - fo / allp, 3)} русский, необходимо минимум {const.DES_RUSN_LIMIT}."
                else:
                    text += "\n\n" + "Анкета не завершена. :/"
                    if ub.state == "bind_blank":
                        asyncio.create_task(send_message_timed(ub.uid, "Привязка невозможна, бланк не завершён."))
                    _rv_show_bl(ub)
            else:
                b.publ = False
                confirm_data_editing()
                _rv_show_bl(ub)
                if ub.state == "bind_blank":
                    asyncio.create_task(send_message_timed(ub.uid, "Привязка бланка отменена."))
        ub.state = ""
        call = "$root#blanks"

    """ <-------------------------------- filter methods -------------------------------->"""

    def _rv_fl_show(ub: User):
        nonlocal text, agr
        global dpp
        fl = get_filters(ub.uid)
        if len(fl) <= 0:
            text = const.choice(const._ff_ab) + "\n\nУ вас пока нет фильтров. Для работы поиска необходим фильтр, вы можете создать пустой, чтобы просматривать все анкеты." \
                                                " Указывайте <code>-</code>, если хотите оставить поле пустым (можно впринципе любой символ, главное чтобы он был один, тогда поле останется пустым)."
        else:
            if ub.mfid >= len(fl):
                ub.mfid = len(fl) - 1
            if ub.mfid < 0:
                ub.mfid = 0
            ff = fl[ub.mfid]
            agr = "" if ub.gfid == ub.mfid else "✅"
            text = f"Фильтр: {ub.mfid + 1}/{len(fl)} ({ff.fid}) ({'активно' if ub.gfid == ub.mfid else 'доступно'})\n\n" \
                   f"Пол: {ff.fil_ypol if ff.fil_ypol is not None else '<b>-все-</b>'}\n" \
                   f"Фандом: {ff.fil_fand if ff.fil_fand is not None else '<b>-все-</b>'}\n" \
                   f"Сортировать по: {ff.fil_typ_ff if ff.fil_typ_ff is not None else '<b>---</b>'}\n" \
                   f"Обязательно: {ff.fil_typ_dc if ff.fil_typ_dc is not None else '<b>---</b>'}\n" \
                   f"Недопустимо: {ff.fil_blacklist if ff.fil_blacklist is not None else '<b>---</b>'}\n" \
                   f"Возрастное: {ff.fil_rate if ff.fil_rate is not None else '<b>-все-</b>'}\n" \
                   f"\nУведомления о новых анкетах: {'✅' if ff.notify else '❌'}"

    def _rv_fl_ch_not(ub: User):
        nonlocal call
        fl = get_filters(ub.uid)
        if fl:
            if ub.mfid >= len(fl):
                ub.mfid = len(fl) - 1
            if ub.mfid < 0:
                ub.mfid = 0
            ff = fl[ub.mfid]
            ff.notify = not ff.notify
            confirm_data_editing()
            _rv_fl_show(ub)
        call = "$root#filters"

    def _rv_fl_add(ub: User):
        nonlocal call
        if count_filters(ub.uid) >= const.MAX_COUNT_OF_FILTERS:
            call = "$root#filters"
            asyncio.create_task(send_message_timed(ub.uid, "превышено максимальное количество фильтров"))
        else:
            call = "$filter#edit"
            reg_filter(ub.uid)
            ub.mfid = count_filters(ub.uid) - 1
            ub.feid_f = True
            confirm_data_editing()

    def _rv_fl_del(ub: User):
        nonlocal call
        fl = get_filters(ub.uid)
        if len(fl):
            if ub.mfid >= len(fl):
                ub.mbid = len(fl) - 1
            if ub.mbid < 0:
                ub.mbid = 0
            delete_filter(ub.uid, fl[ub.mfid].fid)
        _rv_fl_show(ub)
        call = "$root#filters"

    def _rv_fl_edit(ub: User):
        nonlocal text, upd_b, call
        global dpp
        bl = get_filters(ub.uid)
        if len(bl):
            if ub.mfid >= len(bl):
                ub.mfid = len(bl) - 1
            if ub.mfid < 0:
                ub.mfid = 0
            fl = bl[ub.mfid]
            acs = True
            c_len = 0 if call is None else len(call)
            if const.MIN_LINE_LEN >= c_len:
                call = None
            if call == "$do#accept_fe":
                if fl.state >= 5:
                    fl.state = 0
                    ub.feid_f = False
                    fl.finished = True
                    _rv_fl_show(ub)
                    confirm_data_editing()
                    call = "$root#filters"
                    return 1
                if fl.state == 0:
                    upd_b.append([{"text": "муж.", "callback_data": "$sp^male"},
                                  {"text": "жен.", "callback_data": "$sp^feml"},
                                  {"text": "обсудим", "callback_data": "$sp^nstd"}])
                    upd_b.append([{"text": "✅", "callback_data": "$do#accept_fe"},
                                  {"text": "🔙", "callback_data": "$root#filters"}])
                elif fl.state == 4:
                    upd_b.append([{"text": "PG", "callback_data": "$sp^pg"},
                                  {"text": "PG-15", "callback_data": "$sp^pg15"},
                                  {"text": "R", "callback_data": "$sp^r"},
                                  {"text": "NC-17", "callback_data": "$sp^nc17"}])
                    upd_b.append([{"text": "✅", "callback_data": "$do#accept_fe"},
                                  {"text": "🔙", "callback_data": "$root#filters"}])
                else:
                    upd_b.append([{"text": "✅", "callback_data": "$do#accept_fe"},
                                  {"text": "🔙", "callback_data": "$root#filters"}])
            elif fl.state == 0 and (c_len is None or c_len <= const.MAX_TEG_LINE_LEN) and call != "$filter#edit":
                fl.fil_fand = call
                upd_b.append([{"text": "муж.", "callback_data": "$sp^male"},
                              {"text": "жен.", "callback_data": "$sp^feml"},
                              {"text": "обсудим", "callback_data": "$sp^nstd"}])
                upd_b.append([{"text": "✅", "callback_data": "$do#accept_fe"},
                              {"text": "🔙", "callback_data": "$root#filters"}])
            elif fl.state == 1 and call in ["$sp^male", "$sp^feml", "$sp^nstd", None]:
                fl.fil_ypol = None if call is None else dpp[call]
                upd_b.append([{"text": "✅", "callback_data": "$do#accept_fe"},
                              {"text": "🔙", "callback_data": "$root#filters"}])
            elif fl.state == 2 and (c_len is None or c_len <= const.MAX_TEG_LINE_LEN):
                fl.fil_typ_ff = call
                upd_b.append([{"text": "✅", "callback_data": "$do#accept_fe"},
                              {"text": "🔙", "callback_data": "$root#filters"}])
            elif fl.state == 3 and (c_len is None or c_len <= const.MAX_TEG_LINE_LEN):
                fl.fil_typ_dc = call
                upd_b.append([{"text": "✅", "callback_data": "$do#accept_fe"},
                              {"text": "🔙", "callback_data": "$root#filters"}])
            elif fl.state == 4 and (c_len is None or c_len <= const.MAX_TEG_LINE_LEN):
                fl.fil_blacklist = call
                upd_b.append([{"text": "PG", "callback_data": "$sp^pg"},
                              {"text": "PG-15", "callback_data": "$sp^pg15"},
                              {"text": "R", "callback_data": "$sp^r"},
                              {"text": "NC-17", "callback_data": "$sp^nc17"}])
                upd_b.append([{"text": "✅", "callback_data": "$do#accept_fe"},
                              {"text": "🔙", "callback_data": "$root#filters"}])
            elif fl.state == 5 and call in ["$sp^pg", "$sp^pg15", "$sp^r", "$sp^nc17", None]:
                fl.fil_rate = None if call is None else dpp[call]
                ub.feid_f = False
                fl.finished = True
                confirm_data_editing()
                _rv_fl_show(ub)
                call = "$root#filters"
                if ub.gfid == ub.mfid:
                    clear_sl(ub)
                return 1
            else:
                acs = False
            if call != "$do#accept_fe" and ub.gfid == ub.mfid:
                clear_sl(ub)
            if acs:
                fl.state = fl.state + 1
            confirm_data_editing()
            _rv_fl_show(ub)
            text += "\n\n" + const.filter_blank[fl.state]["question"]()
            ub.feid_f = True
            if fl.state > 5:
                ub.feid_f = False
        else:
            ub.feid_f = False
        confirm_data_editing()

    def _rv_fl_pl(ub: User):
        nonlocal call
        fl = get_filters(ub.uid)
        ub.mfid += 1
        if len(fl):
            if ub.mfid >= len(fl):
                ub.mfid = len(fl) - 1
            if ub.mfid < 0:
                ub.mfid = 0
        _rv_fl_show(ub)
        confirm_data_editing()
        call = "$root#filters"

    def _rv_fl_mi(ub: User):
        nonlocal call
        fl = get_filters(ub.uid)
        ub.mfid -= 1
        if len(fl):
            if ub.mfid >= len(fl):
                ub.mfid = len(fl) - 1
            if ub.mfid < 0:
                ub.mfid = 0
        _rv_fl_show(ub)
        confirm_data_editing()
        call = "$root#filters"

    def _rv_ac_fl_ed(ub: User):
        fl = get_filters(ub.uid)
        if len(fl):
            if ub.mfid >= len(fl):
                ub.mfid = len(fl) - 1
            if ub.mfid < 0:
                ub.mfid = 0
            if is_filter_exist(ub.uid, fl[ub.mfid].fid):
                ub.feid_f = True
                fl[ub.mfid].state = 0
            confirm_data_editing()

    def _rv_ac_fl_se(ub: User):
        nonlocal call
        fl = get_filters(ub.uid)
        if len(fl):
            if ub.mfid >= len(fl):
                ub.mfid = len(fl) - 1
            if ub.mfid < 0:
                ub.mfid = 0
            if is_filter_exist(ub.uid, fl[ub.mfid].fid):
                ub.gfid, ub.gbid = ub.mfid, 0
                asyncio.create_task(sp_find_blanks(ub.uid, fl[ub.gfid].fid, []))
                call = "$root#filters"
                _rv_fl_show(ub)
            confirm_data_editing()

    """<-------------------------------- search methods -------------------------------->"""

    def _rv_se_show(ub: User):
        nonlocal text, agr
        fl = get_filters(ub.uid)
        if len(fl) and ub.gfid < len(fl):
            data = loads(ub.sp_dat)["search"]
            if not len(data['query']):
                text = "Анкет не найдено! Пожалуйста, дождитесь полного запуска сервиса."
                agr = ""
                return False
            if not is_blank_exist_sp(data['query'][ub.gbid]):
                text = f"Данный бланк не удалось получить (bid: {data['query'][ub.gbid]})."
                agr = ""
                return False
            b = get_blank(data['query'][ub.gbid])
            text = f"нашлось! ({data['time']} ms) ({ub.gbid + 1} / {len(data['query'])})\n" \
                   f"бланк {b.bid} ({'активно' if b.publ else 'черновик'})\n" \
                   f"имя: {b.fil_name} ({dpp[b.fil_ypol]})\n" \
                   f"фандом: {b.fil_fand}\n" \
                   f"теги: {b.fil_typ}\n" \
                   f"искомый: {b.fil_tmp}\n" \
                   f"рейтинг: {dpp[b.fil_rate]}\n" \
                   f"просмотры: {b.views}\n" \
                   f"описание: {b.fil_des}\n" \
                   f"чат: {b.fil_chat if '$' in b.fil_chat else 'другое'} (можно будет присоедениться или прочесть после одобрения запроса)\n\n" \
                   f"👍 {b.score_pl} | {round(b.score_pl / (b.score_pl + b.score_mi) * 100, 1) if (b.score_pl + b.score_mi) else 0}% | 👎 {b.score_mi}"
            agr = "✅" if b.publ and b.exist_to_user and b.uid != ub.uid and not is_membership_exist(ub.uid, b.chid) else ""
            if agr == "":
                text += "\n\n"
                if b.uid == ub.uid:
                    text += "это ваш бланк"
                elif len(get_waitingers(ub.uid)) >= const.USER_WAIT_LIMIT:
                    text += "число заявок на этот бланк уже превышено"
                elif is_membership_exist(ub.uid, b.chid):
                    text += "вы уже подали заявку"
                else:
                    text += "анкета удалена, или находиться в черновиках"
        else:
            text = "Выберите (создайте) фильтр, чтобы работать с поиском. (можно создать пустой) \n\n" + const.choice(const._static_about)
            agr = ""

    def _rv_se_pl(ub: User):
        nonlocal call
        fl = get_filters(ub.uid)
        if len(fl) and ub.gfid <= len(fl) and is_filter_exist(ub.uid, fl[ub.gfid].fid) and get_se_rez(ub, ub.gbid + 1) is not None:
            qu = loads(ub.sp_dat)["search"]['query']
            if is_blank_exist_sp(qu[ub.gbid]):
                b = get_blank(qu[ub.gbid])
                if b.uid != ub.uid:
                    b.views += 1
            ub.gbid += 1
            if len(fl) - ub.gfid - 1 < const.SEARCH_RN_LIMIT:
                asyncio.create_task(find_blanks(ub.uid, fl[ub.gfid].fid, qu))
        _rv_se_show(ub)
        confirm_data_editing()
        call = "$root#search"

    def _rv_se_mi(ub: User):
        nonlocal call
        fl = get_filters(ub.uid)
        if len(fl) and ub.gfid <= len(fl) and is_filter_exist(ub.uid, fl[ub.gfid].fid) and get_se_rez(ub, ub.gbid - 1) is not None:
            qu = loads(ub.sp_dat)["search"]['query']
            if is_blank_exist_sp(qu[ub.gbid]):
                b = get_blank(qu[ub.gbid])
                if b.uid != ub.uid:
                    b.views += 1
            #asyncio.create_task(find_blanks(ub.uid, fl[ub.gfid].fid, qu))
            ub.gbid -= 1
        _rv_se_show(ub)
        confirm_data_editing()
        call = "$root#search"

    def _rv_se_ac(ub: User):
        nonlocal call
        data = loads(ub.sp_dat)["search"]["query"]
        if is_blank_exist_sp(data[ub.gbid]):
            bl = get_blank(data[ub.gbid])
            if len(get_waitingers(bl.chid)) <= const.USER_WAIT_LIMIT:
                for mem in get_memberships(bl.chid):
                    if mem.is_owner or mem.accepted:
                        asyncio.create_task(send_message(mem.uid, f"Поступила заявка на бланк ({bl.fil_name}) от [{ub.nickname}].\n"
                                                                  f"Бланк перемещён в черновик, чтобы привязать его к тому же чату - найдите чат среди игр и нажмите '🪶'.", notify=None if get_user_data(mem.uid).notify_c else True))
                asyncio.create_task(send_message_timed(ub.uid, "Ваша заявка отравлена, мы уведомим вас, когда её одобрят."))
                bl.publ = False
                reg_membership(ub.uid, bl.chid)
                _rv_pin_show(ub)
            else:
                asyncio.create_task(send_message_timed(ub.uid, "Простите, на этот бланк превышено число заявок."))
        else:
            asyncio.create_task(send_message_timed(ub.uid, "К сожалению данный бланк уже не существует."))
        call = "$root#search"

    def _rv_se_reload(ub: User):
        nonlocal call
        fl = get_filters(ub.uid)
        if len(fl) and ub.gfid <= len(fl) and is_filter_exist(ub.uid, fl[ub.gfid].fid):
            qu = loads(ub.sp_dat)["search"]['query']
            asyncio.create_task(find_blanks(ub.uid, fl[ub.gfid].fid, qu))
        _rv_se_show(ub)
        confirm_data_editing()
        call = "$root#search"

    """<-------------------------------- game methods -------------------------------->"""

    def _rv_ga_show(ub: User):
        nonlocal text, agr, upd_b
        ga = get_games(ub.uid)
        if len(ga) <= ub.gsel:
            ub.gsel = len(ga) - 1
        if ub.gsel < 0:
            ub.gsel = 0
        confirm_data_editing()
        if len(ga) and len(ga) > ub.gsel and is_chat_exist(ga[ub.gsel].chid):
            chat = get_chat_data(ga[ub.gsel].chid)
            waitengers = get_waitingers(ga[ub.gsel].chid)
            text = f"game {ub.gsel + 1} / {len(ga)}\n" \
                   f"ваше имя: {ga[ub.gsel].nickname if ga[ub.gsel].nickname is not None else '-имя отсутствует-'}\n" \
                   f"к чату привязано анкет: {chat_binded_count(chat.chid)}\n" \
                   f"сообщений: {chat.messages_co}{' (есть непрочитанные)' if is_next_message_exist(chat.chid, ga[ub.gsel].cursor) else ''}\n" \
                   f"последнее: {chat.last_sended.strftime('%d.%m.%Y %H:%M')}\n" \
                   f"пользователи (+ заявки): {chat.members_co - len(waitengers)} + {len(waitengers)}\n" \
                   f"уведомления сообщений: {'✅' if ga[ub.gsel].notify else '❌'}\n" \
                   f"{'чат не поддерживает сообщения' if not chat.is_writable else 'откройте чат [<b>' + chat.title + '</b>], чтобы писать'}\n" \
                   f"{'вы участник чата' if ga[ub.gsel].accepted or ga[ub.gsel].is_owner else 'Простите, вы пока не можете использовать чат.'}\n"
            if ga[ub.gsel].accepted or ga[ub.gsel].is_owner:
                text += "Чтобы привязать к этому чату старую или новую анкету переместите её в черновик (заранее " \
                        "убедитесь, что все поля заполнены, название чата будет унаследовано от чата независимо от " \
                        "поля бланка) и нажмите на редактирование (🪶), после чего вам предложат привязать бланк."
                agr = "✅ открыть"
                for waiter in waitengers:
                    name = get_user_data(waiter.uid).nickname if waiter.nickname is None else waiter.nickname
                    upd_b.append([{"text": str(name), "callback_data": "$root#games"}, {"text": "❌", "callback_data": f"$do#sp#cl:{waiter.uid}"}, {"text": "✅", "callback_data": f"$do#sp#ac:{waiter.uid}"}])
            else:
                agr = ""
            text += "\n\n/SetLocalNickname - чтобы сменить имя в чате\n"
            if ga[ub.gsel].accepted or ga[ub.gsel].is_owner:
                text += "/download - чтобы скачать переписку\n"
        else:
            agr = ""
            text = "У вас пока нет игр, зайдите в поиск и подайте заявку на интересующую вас рп сессию используя ✅."

    def _rv_ga_pl(ub: User):
        nonlocal call
        ga = get_games(ub.uid)
        ub.gsel += 1
        if len(ga):
            if ub.gsel >= len(ga):
                ub.gsel = len(ga) - 1
            if ub.gsel < 0:
                ub.gsel = 0
        _rv_ga_show(ub)
        confirm_data_editing()
        call = "$root#games"

    def _rv_ga_mi(ub: User):
        nonlocal call
        ga = get_games(ub.uid)
        ub.gsel -= 1
        if len(ga):
            if ub.gsel >= len(ga):
                ub.gsel = len(ga) - 1
            if ub.gsel < 0:
                ub.gsel = 0
        _rv_ga_show(ub)
        confirm_data_editing()
        call = "$root#games"

    def _rv_ga_bind(ub: User):
        nonlocal call
        mm = get_membership(ub.uid, get_games(ub.uid)[ub.gsel].chid)
        if mm.accepted or mm.is_owner:
            ub.state = "bind_blank"
            confirm_data_editing()
            call = "$root#blanks"
            _rv_show_bl(ub)
        else:
            call = "$root#games"

    """<-------------------------------- chat methods -------------------------------->"""

    def _rv_chat_show(ub: User):
        nonlocal text, call, agr
        agr = ""
        ga = get_games(ub.uid)
        if len(ga) <= ub.gsel:
            ub.gsel = len(ga) - 1
        if ub.gsel < 0:
            ub.gsel = 0
        confirm_data_editing()
        if len(ga) and len(ga) > ub.gsel and is_chat_exist(ga[ub.gsel].chid):
            chat = get_chat_data(ga[ub.gsel].chid)
            memb = get_membership(ub.uid, chat.chid)
            if not chat.is_writable and not memb.accepted and not memb.is_owner:
                text = "Alert! You are not accepted."
                call = "$root#games"
                _rv_ga_show(ub)
                return False
            else:
                if not is_messages_exist(chat.chid):
                    text = "Вы будете первым, кто отправит сюда сообщение!"
                elif is_message_exist(chat.chid, memb.cursor):
                    mess = get_message(chat.chid, memb.cursor)
                    if mess.uid == ub.uid:
                        agr = "1"
                    smb = get_membership(mess.uid, mess.chid) if is_membership_exist(mess.uid, mess.chid) else ChatMember(uid=-1, is_owner=False, nickname=mess.nickname)
                    text = f"<b>{smb.nickname if smb.nickname is not None else '-имя отсутствует-'}{' (Я):' if smb.is_owner else ':'}</b>\n\n" + mess.text[:]
                elif is_before_message_exist(chat.chid, memb.cursor):
                    memb.cursor = get_before_message_id(chat.chid, memb.cursor)
                    confirm_data_editing()
                    _rv_chat_show(ub)
                elif is_next_message_exist(chat.chid, memb.cursor):
                    memb.cursor = get_next_message_id(chat.chid, memb.cursor)
                    confirm_data_editing()
                    _rv_chat_show(ub)
                else:
                    text = "Unknown Error. :("
        else:
            call = "$root#games"
            _rv_ga_show(ub)

    def _rv_ch_pl(ub: User):
        nonlocal call
        ch = get_games(ub.uid)[ub.gsel]
        if is_next_message_exist(ch.chid, ch.cursor):
            ch.cursor = get_next_message_id(ch.chid, ch.cursor)
            confirm_data_editing()
            _rv_chat_show(ub)
        confirm_data_editing()
        call = "$game#chat"

    def _rv_ch_mi(ub: User):
        nonlocal call
        ch = get_games(ub.uid)[ub.gsel]
        if is_before_message_exist(ch.chid, ch.cursor):
            ch.cursor = get_before_message_id(ch.chid, ch.cursor)
            confirm_data_editing()
            _rv_chat_show(ub)
        confirm_data_editing()
        call = "$game#chat"

    def _rv_ch_op(ub: User):
        nonlocal call
        call = "$root#games"
        if is_membership_exist(ub.uid, get_games(ub.uid)[ub.gsel].chid):
            ub.game_f = True
            confirm_data_editing()
            call = "$game#chat"

    def _rv_ga_del(ub: User):
        nonlocal call
        ga = get_games(ub.uid)
        if len(ga) > ub.gsel >= 0:
            del_member(ub.uid, ga[ub.gsel].chid)
        call = "$root#games"
        _rv_ga_show(ub)

    def _rv_ga_ntc(ub: User):
        nonlocal call
        ga = get_games(ub.uid)
        ga[ub.gsel].notify = not ga[ub.gsel].notify
        confirm_data_editing()
        call = "$root#games"
        _rv_ga_show(ub)

    def _rv_chat_del_msg(ub: User):
        nonlocal call
        memb = get_games(ub.uid)[ub.gsel]
        if is_message_exist(memb.chid, memb.cursor) and get_message(memb.chid, memb.cursor).uid == ub.uid:
            if not get_chat_data(memb.chid).is_writable:
                asyncio.create_task(send_message_timed(ub.uid, "в этом чате нельзя удалять", 6))
                call = "$game#chat"
                _rv_chat_show(ub)
                return False
            del_message(memb.chid, memb.cursor)
            if is_before_message_exist(memb.chid, memb.cursor):
                memb.cursor = get_before_message_id(memb.chid, memb.cursor)
                confirm_data_editing()
            elif is_next_message_exist(memb.chid, memb.cursor):
                memb.cursor = get_next_message_id(memb.chid, memb.cursor)
                confirm_data_editing()
        call = "$game#chat"
        _rv_chat_show(ub)

    """<-------------------------------- pin methods -------------------------------->"""

    def _rv_pin_show(ub: User):
        nonlocal text, agr
        pi = get_pins(ub.uid)
        if ub.mpid >= len(pi):
            ub.mpid = len(pi) - 1
            confirm_data_editing()
        elif ub.mpid < 0:
            ub.mpid = 0
            confirm_data_editing()
        if len(pi) and ub.mpid < len(pi):
            if not is_blank_exist_sp2(pi[ub.mpid].bid):
                text = f"Данный бланк не удалось получить (bid: {pi[ub.mbid].bid})."
                agr = ""
                return False
            if not is_blank_exist_sp(pi[ub.mpid].bid):
                agr = ""
            b = get_blank(pi[ub.mpid].bid)
            text = f"закреплено ({ub.mpid + 1} / {len(pi)})\n" \
                   f"бланк {b.bid} ({'активно' if b.publ else 'черновик'})\n" \
                   f"имя: {b.fil_name} ({dpp[b.fil_ypol]})\n" \
                   f"фандом: {b.fil_fand}\n" \
                   f"теги: {b.fil_typ}\n" \
                   f"искомый: {b.fil_tmp}\n" \
                   f"рейтинг: {dpp[b.fil_rate]}\n" \
                   f"просмотры: {b.views}\n" \
                   f"описание: {b.fil_des}\n" \
                   f"чат: {b.fil_chat if '$' in b.fil_chat else 'другое'} (можно будет присоедениться или прочесть после одобрения запроса на вступление)\n" \
                   f"👍 {b.score_pl} | {round(b.score_pl / (b.score_pl + b.score_mi) * 100, 1) if (b.score_pl + b.score_mi) else 0}% | 👎 {b.score_mi}"
            agr = "✅" if b.publ and b.exist_to_user and b.uid != ub.uid and not is_membership_exist(ub.uid, b.chid) else ""
            if agr == "":
                text += "\n\n"
                if b.uid == ub.uid:
                    text += "это ваш бланк"
                elif is_membership_exist(ub.uid, b.chid):
                    text += "вы уже подали заявку"
                else:
                    text += "анкета удалена, или находиться в черновиках"
        else:
            text = "у вас пока нет закреплённых бланков \n\n" + const.choice(const._static_about)
            agr = ""

    def _rv_pin_pl(ub: User):
        nonlocal call
        pins = get_pins(ub.uid)
        if pins and 0 <= ub.mpid < len(pins):
            if ub.mpid + 1 < len(pins):
                ub.mpid += 1
                confirm_data_editing()
                _rv_pin_show(ub)
            confirm_data_editing()
        call = "$root#pinned"

    def _rv_pin_mi(ub: User):
        nonlocal call
        pins = get_pins(ub.uid)
        if pins and 0 <= ub.mpid < len(pins):
            if ub.mpid - 1 >= 0:
                ub.mpid -= 1
                confirm_data_editing()
                _rv_pin_show(ub)
            confirm_data_editing()
        call = "$root#pinned"

    def _rv_pin_del(ub: User):
        nonlocal call
        pins = get_pins(ub.uid)
        if pins:
            delete_pin(ub.uid, pins[ub.mpid].pid)
            _rv_pin_mi(ub)
            _rv_pin_show(ub)
        call = "$root#pinned"

    def _rv_pin_ac(ub: User):
        nonlocal call
        pins = get_pins(ub.uid)
        if is_blank_exist_sp(pins[ub.mpid]):
            bl = get_blank(pins[ub.mpid].bid)
            for mem in get_memberships(bl.chid):
                if mem.is_owner or mem.accepted:
                    asyncio.create_task(
                        send_message(mem.uid, f"Поступила заявка на бланк ({bl.fil_name}) от [{ub.nickname}].\n"
                                              f"Бланк перемещён в черновик, чтобы привязать его к тому же чату - найдите чат среди игр и нажмите '🪶'.",
                                     notify=None if get_user_data(mem.uid).notify_c else True))
            asyncio.create_task(send_message_timed(ub.uid, "Ваша заявка отравлена, мы уведомим вас, когда её одобрят."))
            bl.publ = False
            reg_membership(ub.uid, bl.chid)
            _rv_pin_show(ub)
        elif is_blank_exist_sp2(pins[ub.mpid].bid):
            asyncio.create_task(send_message_timed(ub.uid, "К сожалению данный бланк пока в черновиках, на него нельзя ответить."))
        else:
            asyncio.create_task(send_message_timed(ub.uid, "К сожалению данный бланк уже не существует."))
        call = "$root#search"

    def _rv_pin_bl(ub: User):
        nonlocal call
        data = loads(ub.sp_dat)["search"]
        if len(data['query']) and 0 <= ub.gbid < len(data['query']):
            if is_blank_exist_sp2(data['query'][ub.gbid]) and not is_blank_pinned(data['query'][ub.gbid]):
                pin(ub.uid, data['query'][ub.gbid])
                _rv_se_show(ub)
                asyncio.create_task(send_message_timed(ub.uid, "Успешно закреплено."))
            else:
                asyncio.create_task(send_message_timed(ub.uid, "К сожалению нельзя закрепить."))
        call = "$root#search"

    def _open_blank(ub: User, bid: int):
        if is_blank_exist_sp(bid):
            irn = find_in_se(ub, bid)
            if irn is None:
                ssl = loads(ub.sp_dat)
                ssl["search"]["query"].append(bid)
                ssl["search"]["time"] = 0
                ub.sp_dat = dumps(ssl)
                ub.gbid = len(ssl["search"]["query"]) - 2
                confirm_data_editing()
            else:
                ub.gbid = irn - 1
                confirm_data_editing()
            _rv_se_pl(ub)
        else:
            asyncio.create_task(send_message_timed(ub.uid, "К сожалению данный бланк уже не существует."))


    a = {"text": "✅", "callback_data": ""}
    if call == "register" and not is_user_exist(uid):
        reg_user(uid, "@" + user_obj.username)
        call = "$root#start"
        if str(uid) == const.ADMIN:
            get_user_data(uid).role = "admin"
            confirm_data_editing()
    if not is_user_exist(uid):
        return special_but_conv([[{"text": "правила", "url": "https://docs.google.com/document/d/1PcjJ4RJr-5_pf95Zn2FUfJXBzYhzKSFIDqOE5_lyH98/edit?usp=sharing"}],
                                 [{"text": "сообщество (канал)", "url": const.CHANEL}],
                                 [{"text": "вступить", "callback_data": "register"}]]), const.inf_mes
    user = get_user_data(uid)
    #user.state = call[:]   отключено всвязи с изменениями в логике
    do_l = {"$do#addnot": _rv_addnot, "$do#gamenot": _rv_gamenot, "$do#adminot": _rv_adminot, "$root#delite_profile": _rv_delprof,
            "$root#delite_p_f": _rv_del_prof_f, "$root#blanks": _rv_show_bl, "$do#add_blank": _rv_add_bl, "$blank#edit": _rv_ac_bl_ed,
            "$do#blanks-1": _rv_bl_mi, "$do#blanks+1": _rv_bl_pl, "$do#delete_bl": _rv_bl_del, "$do#skip_be": _rv_bl_sk,
            "$do#accept_bl": _rv_bl_ac, "$root#filters": _rv_fl_show, "$do#delete_fe": _rv_fl_del, "$do#add_filter": _rv_fl_add,
            "$filter#edit": _rv_ac_fl_ed, "$do#filters-1": _rv_fl_mi, "$do#filters+1": _rv_fl_pl, "$do#accept_fl": _rv_ac_fl_se,
            "$root#search": _rv_se_show, "$do#search-1": _rv_se_mi, "$do#search+1": _rv_se_pl, "$do#accept_se": _rv_se_ac,
            "$do#game-1": _rv_ga_mi, "$do#game+1": _rv_ga_pl, "$root#games": _rv_ga_show, "$do#bind_ga": _rv_ga_bind,
            "$do#chat-1": _rv_ch_mi, "$do#chat+1": _rv_ch_pl, "$do#open_ga": _rv_ch_op, "$do#delete_ga": _rv_ga_del,
            "$do#notify_ga": _rv_ga_ntc, "$do#delete_msg": _rv_chat_del_msg, "$do#reload_se": _rv_se_reload,
            "$root#pinned": _rv_pin_show, "$do#pinned-1": _rv_pin_mi, "$do#pinned+1": _rv_pin_pl, "$do#accept_ga": _rv_pin_ac,
            "$do#delete_pi": _rv_pin_del, "$do#pin_se": _rv_pin_bl, "$do#notify_fe": _rv_fl_ch_not}
    if call.startswith("$root#"):
        user.beid_f = False
        user.feid_f = False
        user.game_f = False
        clear_should_notify_user(user.uid)
        if call == "$root#start":
            user.state = ""
            asyncio.create_task(clear_filters_to_notify(user.uid))
        confirm_data_editing()
    elif call.startswith("$do#openblank^"):
        _open_blank(user, int(call.lstrip("$do#openblank^")))
    if call in do_l.keys():
        do_l[call](user)
    if user.beid_f:
        _rv_bl_edit(user)
    if user.feid_f:
        _rv_fl_edit(user)
    if user.game_f:
        _rv_chat_show(user)
    profile = f"  ⭐️  ваши настройки  ⭐️\n" \
              f"uid: {user.uid}\n" \
              f"id в системе: {user.iid} / {get_user_count()}\n" \
              f"никнейм: {user.nickname}\n" \
              f"вы с нами  с: {user.reg_date.strftime('%d.%m.%Y %H:%M')}\n" \
              f"уведомления   рекламы:       {'✅' if user.notify_a else '❌'}\n" \
              f"уведомления о принятии в рп: {'✅' if user.notify_c else '❌'}\n" \
              f"объявления администрации:    {'✅' if user.notify_i else '❌'}\n" \
              f"роль: {user.role}\n" \
              f"грамотность: {'---' if user.gram_co <= 0 else user.gram_su / user.gram_co}\n" \
              f"ваша  карма: {'---' if user.rate_co <= 0 else user.rate_su / user.rate_co}\n" \
              f"  ⚙️  системные  ⚙️\n" \
              f"max filters count: {const.MAX_COUNT_OF_FILTERS}\n" \
              f"max blanks  count: {const.MAX_COUNT_OF_BLANKS}\n" \
              f"max  games  count: {const.MAX_COUNT_OF_GAMES}\n" \
              f"max tegs string len: {const.MAX_TEG_LINE_LEN}\n" \
              f"max  titles  length: {const.MAX_TITLES_LEN}\n" \
              f"max blank descr len: {const.MAX_BLANK_DES_LEN}\n" \
              f"(чтобы сменить имя напишите /SetNickname)"
    _p = const.static_about() if user is not None and datetime.now() - user.reg_date > timedelta(minutes=3) else const.about()
    menu = {"$root#start": {"disp": _p, "var": [[{"text": "настройки ⚙️", "callback_data": "$root#settings"},
                                                 {"text": "поиск 🔍", "callback_data": "$root#search"}],
                                                [{"text": "фильтры 🏷", "callback_data": "$root#filters"},
                                                 {"text": "анкеты 🪪", "callback_data": "$root#blanks"}],
                                                [{"text": "игры 🕹", "callback_data": "$root#games"},
                                                 {"text": "избранное 📌", "callback_data": "$root#pinned"}]]},
            "$root#settings": {"disp": profile, "var": [
                [{"text": f"уведомления рекламы {'🔕' if user.notify_a else '🔔'}", "callback_data": "$do#addnot"}],
                [{"text": f"уведомления заявок {'🔕' if user.notify_c else '🔔'}", "callback_data": "$do#gamenot"}],
                [{"text": f"объявления админов {'🔕' if user.notify_i else '🔔'}", "callback_data": "$do#adminot"}],
                _sp2 if user.delete_p else _sp1,
                [{"text": f"bugreport {const.choice(['👨🏻‍🔧', '👩‍💻', '👩‍🔧', '🧙‍♂️', '🤦', '🪲', '🕸'])}", "callback_data": "$do#bugreport"},
                 {"text": "🔙", "callback_data": "$root#start"}],
                [{"text": "правила", "url": "https://docs.google.com/document/d/1PcjJ4RJr-5_pf95Zn2FUfJXBzYhzKSFIDqOE5_lyH98/edit?usp=sharing"}],
                [{"text": "сообщество (канал)", "url": const.CHANEL}]]},
            "$root#search": {"disp": "", "var": [[{"text": "🏷", "callback_data": "$root#filters"},
                                                  {"text": "⬅️", "callback_data": "$do#search-1"},
                                                  {"text": "➡️", "callback_data": "$do#search+1"},
                                                  {"text": "📌", "callback_data": "$do#pin_se"}],
                                                  [{"text": agr, "callback_data": "$do#accept_se"},
                                                  {"text": "🔙", "callback_data": "$root#start"},
                                                   {"text": "♻️", "callback_data": "$do#reload_se"}]]},
            "$root#filters": {"disp": "", "var": [[{"text": "⬅️", "callback_data": "$do#filters-1"},
                                                   {"text": "➕", "callback_data": "$do#add_filter"},
                                                   {"text": "🪶", "callback_data": "$filter#edit"},
                                                   {"text": "➡️", "callback_data": "$do#filters+1"}],
                                                  [{"text": agr, "callback_data": "$do#accept_fl"},
                                                   {"text": "🗑", "callback_data": "$do#delete_fe"},
                                                   {"text": "🔙", "callback_data": "$root#start"},
                                                   {"text": '🔔', "callback_data": "$do#notify_fe"}]]},
            "$root#blanks": {"disp": "", "var": [[{"text": "⬅️", "callback_data": "$do#blanks-1"},
                                                  {"text": "➕", "callback_data": "$do#add_blank"},
                                                  {"text": "🪶", "callback_data": "$blank#edit"},
                                                  {"text": "➡️", "callback_data": "$do#blanks+1"}],
                                                 [{"text": agr, "callback_data": "$do#accept_bl"},
                                                  {"text": "🗑", "callback_data": "$do#delete_bl"},
                                                  {"text": "🔙", "callback_data": "$root#start"}]]},
            "$blank#edit": {"disp": "", "var": [[{"text": "✅", "callback_data": "$do#accept_be"},
                                                 {"text": "🔙", "callback_data": "$root#blanks"}]]},
            "$filter#edit": {"disp": "", "var": [[{"text": "✅", "callback_data": "$do#accept_fe"},
                                                  {"text": "🔙", "callback_data": "$root#filters"}]]},
            "$root#games": {"disp": "", "var": [[{"text": "⬅️", "callback_data": "$do#game-1"},
                                                 {"text": agr, "callback_data": "$do#open_ga"},
                                                 {"text": "➡️", "callback_data": "$do#game+1"}],
                                                [{"text": '🔔' if agr else '', "callback_data": "$do#notify_ga"},
                                                 {"text": "🗑", "callback_data": "$do#delete_ga"},
                                                 {"text": "🔙", "callback_data": "$root#start"},
                                                 {"text": "🪶" if agr else "", "callback_data": "$do#bind_ga"}]]},
            "$game#chat": {"disp": "", "var": [[{"text": "⬅️", "callback_data": "$do#chat-1"},
                                                {"text": "🗑" if agr else "", "callback_data": "$do#delete_msg"},
                                                {"text": "➡️", "callback_data": "$do#chat+1"},
                                                {"text": "🔙", "callback_data": "$root#games"}]]},
            "$root#pinned": {"disp": "", "var": [[{"text": "⬅️", "callback_data": "$do#pinned-1"},
                                                  {"text": "➡️", "callback_data": "$do#pinned+1"}],
                                                 [{"text": agr, "callback_data": "$do#accept_ga"},
                                                  {"text": "🗑", "callback_data": "$do#delete_pi"},
                                                  {"text": "🔙", "callback_data": "$root#start"}]]}
            }
    if user.last_message == "$game#chat":
        menu["$game#chat"]["var"].append([{"text": "ждём ваши сообщения...", "callback_data": ""}])
    if call in menu.keys():
        buttons = menu[call]["var"][:]
        buttons.extend(upd_b)
        if not text:
            text = menu[call]["disp"]
    if buttons is None and upd_b:
        buttons = upd_b[:]
    buttons = special_but_conv(buttons) if buttons is not None else in_bt
    if in_bt is not None and in_tt is not None and in_bt == buttons and in_tt == text:
        return None, None
    if not text:
        return None, None
    return buttons, text
