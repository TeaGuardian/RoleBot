from pymorphy3 import MorphAnalyzer
from . import const
morph = MorphAnalyzer()


def distance(a: str, b: str) -> int:
    """расстояние по левенштейну между строками"""
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n
    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)
    return current_row[n]


def grate_similarity(a: str, b: str) -> float:
    """схожесть слов от 0 до 1, где 1 - полное совпадение"""
    if a is None or b is None:
        return 1
    gd = 1 - round(distance(a, b) / max([len(a), len(b)]), 8)
    return 0 if gd < const.INSEPTION_TEG_LIMIT else gd


def desea(word: str, lis: list) -> (list, float):
    """найти в списке самое подходящее слово, удалить его и вернуть новый список с оценкой схожести лучшего вхождения"""
    es = max(map(lambda g: (g, grate_similarity(g, word)), list), key=lambda g: g[1])
    lis.pop(lis.index(es[0]))
    return lis, es[1]


def abl_str_chm(ins: str, key: str):
    """устаревшая функция оценки схожести"""
    ins, key = ins.lower(), key.lower()
    repr, ablt = [], "!@#%^&*()_+=-;:'/.,|" + '"'
    rez = 0
    if not ins or not key:
        return True, 0
    for wor in key.split():
        if not wor:
            continue
        for d in ablt:
            wor = wor.rstrip(d).lstrip(d)
        dhj = []
        for wor2 in ins.split():
            if not wor2:
                continue
            for d in ablt:
                wor2 = wor2.rstrip(d)
                wor2 = wor2.lstrip(d)
            dhj.append(1 - distance(wor, wor2) / max(len(wor), len(wor2)))
            if "$" in wor and distance(wor, wor2) / max(len(wor), len(wor2)) < const.INSEPTION_TEG_LIMIT:
                return False, rez
        fu = round(max(dhj), 4)
        if fu > const.INSEPTION_TEG_LIMIT:
            rez -= fu
    return True, rez


def split_string(input_str: str, max_len: int, sep=" ", pre_p=20) -> list[str]:
    """
    Разделяет строку на более маленькие строки, согласно пределу.
    :param input_str: Входная строка.
    :param max_len: Максимальная длинна конечных строк.
    :param sep: Разделитель, по которому будут определены строки.
    :param pre_p: Нижний порог. Если разница в разделённой строке и максимальной длине больше, то произойдёт разделение не по разделителю, а по длине.
    :return: Список строк на основе исходной строки, чья длина не превышает максимальную.
    """
    trf, lp, ste = max_len - pre_p, 0, 0
    rez, line = [], ""
    for si in input_str:
        if si == sep and ste == 0:
            continue
        if si == sep:
            lp = ste
        line += si
        if len(line) - 1 >= max_len:
            if ste - lp > trf or ste - lp == 0:
                rez.append(line)
                line, ste, lp = "", -1, 0
            else:
                if lp == 0:
                    lp = len(line)
                rez.append(line[:lp])
                line, ste, lp = line[lp:], len(line[lp + 1:])- 1, 0
        ste += 1
    if line:
        rez.append(line)
    return rez if len(rez) else [""]


def check_word(word: str):
    """выяснить чем является слово"""
    global morph
    if any(map(lambda g: g.isdigit(), word)):
        return "number"
    p_w = morph.parse("".join(list(filter(lambda g: g.isalnum(), word))))[0]
    if 'LATN' in p_w.tag:
        return 'foreign'
    elif 'LATN' not in p_w.tag and 'UNKN' not in p_w.tag and p_w.score >= const.WORD_THRESHOLD_LIMIT:
        return "russian"
    return "other"


def check_text(text: str) -> [int, int, int, int, int]:
    """
    all count, number, foreign, russian, other
    статистика количества типов слов в тексте для оценки адекватности текста
    """
    abtl = "!@#$%^&*()_+=-;:'/.,|" + '"'
    rez = [0, 0, 0, 0, 0]
    dr = ""
    cpr = {"number": 1, "foreign": 2, "russian": 3, "other": 4}
    for wor in text.split():
        tt = wor[:]
        for d in abtl:
            wor = wor.rstrip(d)
            wor = wor.lstrip(d)
        rez[0] += 1
        npf = cpr[check_word(wor)]
        rez[npf] += 1
        dr += f" <code>{tt}</code>" if npf == 4 else f" {tt}"
    return rez[:], dr
