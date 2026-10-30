"""Эталонный глоссарий Grand Mobile для kk и uz.

Предпочтительные казахские термины подобраны как слова живого игрового
интерфейса: коротко, на «сіз», без русской кальки там, где в языке есть
устойчивый эквивалент. Заимствованные термины оставлены только когда их
уже использует сам игрок (сервер, гараж, полиция).
"""

from __future__ import annotations

# Каждый термин: триггеры в источнике и допустимые/запрещённые формы.
TERMS: list[dict] = [
    {
        "id": "quest",
        "triggers": {"en": ["quest", "mission"], "ru": ["квест"]},
        "kk": ["тапсырма"],
        "kk_bad": ["квест", "задание"],
        "uz": ["topshiriq"],
        "uz_bad": ["квест", "quest", "задание"],
    },
    {
        "id": "case",
        "triggers": {"en": ["case", "lootbox"], "ru": ["кейс"]},
        "kk": ["сандық"],
        "kk_bad": ["кейс"],
        "uz": ["quti"],
        "uz_bad": ["keys", "кейс", "case"],
    },
    {
        "id": "battle_pass",
        "triggers": {"en": ["battle pass"], "ru": ["батл пасс", "боевой пропуск"]},
        "kk": ["маусымдық жол"],
        "kk_bad": ["батл пасс", "battle pass"],
        "uz": ["mavsum yoʻli", "mavsum yo'li"],
        "uz_bad": ["battle pass", "батл пасс"],
    },
    {
        "id": "fuel",
        "triggers": {"en": ["fuel"], "ru": ["топливо"]},
        "kk": ["жанармай"],
        "kk_bad": ["бензин"],
        "uz": ["yoqilgʻi", "yoqilg'i"],
        "uz_bad": ["benzin", "бензин"],
    },
    {
        "id": "vehicle",
        "triggers": {"en": ["vehicle"], "ru": ["транспорт"]},
        "kk": ["көлік"],
        "kk_bad": ["машина"],
        "uz": ["transport"],
        "uz_bad": ["mashina", "машина"],
    },
    {
        "id": "donate",
        "triggers": {"en": ["donate"], "ru": ["донат"]},
        "kk": ["алтын"],
        "kk_bad": ["донат"],
        "uz": ["oltin"],
        "uz_bad": ["donat", "донат"],
    },
    {
        "id": "hospital",
        "triggers": {"en": ["hospital"], "ru": ["больниц"]},
        "kk": ["аурухана"],
        "kk_bad": ["больниц"],
        "uz": ["shifoxona"],
        "uz_bad": ["больниц", "gospital", "kasalxona"],
    },
    {
        "id": "inventory",
        "triggers": {"en": ["inventory"], "ru": ["инвентар"]},
        "kk": ["заттар"],
        "kk_bad": ["инвентар"],
        "uz": ["buyum"],
        "uz_bad": ["inventar", "инвентар", "inventory"],
    },
    {
        "id": "skin",
        "triggers": {"en": ["skin"], "ru": ["скин"]},
        "kk": ["бейне"],
        "kk_bad": ["скин"],
        "uz": ["qiyofa"],
        "uz_bad": ["skin", "скин"],
    },
    {
        "id": "tutorial",
        "triggers": {"en": ["tutorial"], "ru": ["обучен"]},
        "kk": ["оқыту"],
        "kk_bad": ["туториал", "скип"],
        "uz": ["oʻqit", "o'qit"],
        "uz_bad": ["tutorial", "туториал"],
    },
    {
        "id": "nickname",
        "triggers": {"en": ["nickname"], "ru": ["ник"]},
        "kk": ["лақап"],
        "kk_bad": ["ник"],
        "uz": ["laqab"],
        "uz_bad": ["nik"],
    },
    {
        "id": "business",
        "triggers": {"en": ["business"], "ru": ["бизнес"]},
        "kk": ["кәсіп"],
        "kk_bad": ["бизнес", "доход"],
        "uz": ["tadbirkorlik"],
        "uz_bad": [],
    },
    {
        "id": "password",
        "triggers": {"en": ["password"], "ru": ["парол"]},
        "kk": ["құпиясөз"],
        "kk_bad": ["парол"],
        "uz": ["parol", "maxfiy soʻz", "maxfiy so'z"],
        "uz_bad": ["парол"],
    },
    {
        "id": "garage",
        "triggers": {"en": ["garage"], "ru": ["гараж"]},
        "kk": ["гараж"],
        "kk_bad": ["гаражъ"],
        "uz": ["garaj"],
        "uz_bad": [],
    },
    {
        "id": "reward",
        "triggers": {"en": ["reward"], "ru": ["награда"]},
        "kk": ["марапат"],
        "kk_bad": ["бонус"],
        "uz": ["mukofot"],
        "uz_bad": ["bonus", "бонус"],
    },
    {
        "id": "coins",
        "triggers": {"en": ["coins"], "ru": ["монет"]},
        "kk": ["тиын"],
        "kk_bad": ["коин", "монет"],
        "uz": ["tanga"],
        "uz_bad": ["coin", "монет"],
    },
    {
        "id": "server",
        "triggers": {"en": ["server"], "ru": ["сервер"]},
        "kk": ["сервер"],
        "kk_bad": [],
        "uz": ["server"],
        "uz_bad": [],
    },
    {
        "id": "police",
        "triggers": {"en": ["police"], "ru": ["полици"]},
        "kk": ["полиция"],
        "kk_bad": [],
        "uz": ["politsiya"],
        "uz_bad": [],
    },
]


# Целая строка, совпавшая с русским источником, не считается калькой,
# если это утверждённый заимствованный термин.
APPROVED_LOAN_STRINGS = {
    "kk": {"гараж", "сервер", "полиция", "телефон", "меню"},
    "uz": {"garaj", "server", "politsiya", "telefon", "menyu"},
}


# Русские UI-слова, которых не должно быть в казахской строке.
RUSSIAN_LEAKS = [
    "нажмите",
    "ошибка",
    "загрузка",
    "продолжить",
    "настройки",
    "сохранить",
    "отмена",
    "пожалуйста",
    "неверный",
    "пароль",
    "войти",
    "выберите",
    "введите",
    "удачи",
    "скидка",
    "ежедневный",
    "ежедневная",
    "бонус",
    "кикнул",
    "админ",
    "сообщение",
    "изменения",
    "забанены",
    "скипнуть",
    "туториал",
    "доход",
    "финишируйте",
    "опыт",
    "применён",
    "применен",
    "больница",
    "уровень",
    "купить",
    "инвентарь",
    "новый",
    "новое",
]
