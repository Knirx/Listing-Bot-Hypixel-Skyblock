import math

gather_all_dict = {
        "skyblockLevel": 0,
        "skillAverage": 0,
        "SKILL_FISHING": 0,
        "SKILL_ALCHEMY": 0,
        "SKILL_MINING": 0,
        "SKILL_FARMING": 0,
        "SKILL_ENCHANTING": 0,
        "SKILL_TAMING": 0,
        "SKILL_FORAGING": 0,
        "SKILL_CARPENTRY": 0,
        "SKILL_COMBAT": 0,
        "dungeonLevel": 0,
        "networth": 0,
        "soulboundNetworth": 0,
        "unsoulboundNetworth": 0,
        "coins": 0,
        "weight": 0,
        'zombie': 0,
        'spider': 0,
        'wolf': 0,
        'enderman': 0,
        'blaze': 0,
        'vampire': 0,
        "hotmLevel": 0,
        "mithrilPowder": 0,
        "gemstonePowder": 0,
        "faction": "",
        "mages_reputation": 0,
        "barbarians_reputation": 0
    }


def dungeon_class_level(exp):
    dungeonsss = {
        50: 1,
        125: 2,
        235: 3,
        395: 4,
        625: 5,
        955: 6,
        1425: 7,
        2095: 8,
        3045: 9,
        4385: 10,
        6275: 11,
        8940: 12,
        12700: 13,
        17960: 14,
        25340: 15,
        35640: 16,
        50040: 17,
        70040: 18,
        97640: 19,
        135640: 20,
        188140: 21,
        259640: 22,
        356640: 23,
        488640: 24,
        668640: 25,
        911640: 26,
        1239640: 27,
        1684640: 28,
        2284640: 29,
        3084640: 30,
        4149640: 31,
        5559640: 32,
        7459640: 33,
        9959640: 34,
        13259640: 35,
        17559640: 36,
        23159640: 37,
        30359640: 38,
        39559640: 39,
        51559640: 40,
        66559640: 41,
        85559640: 42,
        109559640: 43,
        139559640: 44,
        177559640: 45,
        225559640: 46,
        285559640: 47,
        360559640: 48,
        453559640: 49,
        569809640: 50,
    }

    previous = 0

    for i in dungeonsss.keys():
        level = dungeonsss[i]
        if exp >= i:
            if exp >= 569809640:
                return 50
            else:
                previous = i
        else:
            level = level - 1 + (exp - previous) / (i - previous)
            return round(level, 2)


def convert_to_int_with_letters(input_string):
    numeric_string = ''.join(filter(str.isdigit, input_string))

    if 'm' in input_string.lower():
        return int(numeric_string) * 1000000
    elif 'b' and '.' in input_string.lower():
        return int(numeric_string) * 100000000
    elif 'b' and ',' in input_string.lower():
        return int(numeric_string) * 100000000
    elif 'b' in input_string.lower():
        return int(numeric_string) * 1000000000
    else:
        return int(numeric_string)


def get_farming_level_cap(data, exp, overflow):
    increase_skill_dict = {
        1: 59472425,
        2: 64072425,
        3: 68972425,
        4: 74172425,
        5: 79672425,
        6: 85472425,
        7: 91572425,
        8: 97972425,
        9: 104672425,
        10: 111672425,
    }
    try:
        new_cap = int(data["jacobs_contest"]["perks"]["farming_level_cap"])
    except:
        return "???"
    new_exp_cap = increase_skill_dict[new_cap]
    if exp >= new_exp_cap:
        if overflow:
            return f"Level: {50 + new_cap}\nOverflow: {format_TBMK(exp - new_exp_cap)}"
        else:
            return 50 + new_cap
    else:
        swapped_dict = {v: k for k, v in my_dict.items()}
        for xp, level in reversed(swapped_dict.items()):
            if xp >= exp:
                return level

def get_slayer_lvl_with_overflow_exp(skill, exp, cap=9):
    slayersss = {
        5: 1,
        15: 2,
        200: 3,
        1000: 4,
        5000: 5,
        20000: 6,
        100000: 7,
        400000: 8,
        1000000: 9,
    }
    previous = 0
    if skill == "vampire" and exp >= 5000:
        return f"Level: 5\nTotal exp: {format_TBMK(exp)}\nOverflow: {format_TBMK(exp - 5000)}"
    for i in slayersss.keys():
        level = slayersss[i]
        if exp >= i:
            if level == cap:
                return (
                    f"Level: {level}\nTotal exp: {format_TBMK(exp)}\nOverflow: {format_TBMK(exp - i)}"
                )
            else:
                previous = i
        else:
            level = round(level - 1 + (exp - previous) / (i - previous), 2)
            return f"Level: {level}\nTotal exp: {format_TBMK(exp)}\nOverflow: 0"


def dungeon_cless_level(exp):
    dungeonsss = {
        50: 1,
        125: 2,
        235: 3,
        395: 4,
        625: 5,
        955: 6,
        1425: 7,
        2095: 8,
        3045: 9,
        4385: 10,
        6275: 11,
        8940: 12,
        12700: 13,
        17960: 14,
        25340: 15,
        35640: 16,
        50040: 17,
        70040: 18,
        97640: 19,
        135640: 20,
        188140: 21,
        259640: 22,
        356640: 23,
        488640: 24,
        668640: 25,
        911640: 26,
        1239640: 27,
        1684640: 28,
        2284640: 29,
        3084640: 30,
        4149640: 31,
        5559640: 32,
        7459640: 33,
        9959640: 34,
        13259640: 35,
        17559640: 36,
        23159640: 37,
        30359640: 38,
        39559640: 39,
        51559640: 40,
        66559640: 41,
        85559640: 42,
        109559640: 43,
        139559640: 44,
        177559640: 45,
        225559640: 46,
        285559640: 47,
        360559640: 48,
        453559640: 49,
        569809640: 50,
    }

    previous = 0
    for i in dungeonsss.keys():
        level = dungeonsss[i]
        if exp >= i:
            if exp >= 569809640:
                return 50
            else:
                previous = i
        else:
            level = level - 1 + (exp - previous) / (i - previous)
            return round(level, 2)


def get_skill_lvl_overflow(data, skill, exp, cap=60):
    skills = {
        50: 1,
        175: 2,
        375: 3,
        675: 4,
        1175: 5,
        1925: 6,
        2925: 7,
        4425: 8,
        6425: 9,
        9925: 10,
        14925: 11,
        22425: 12,
        32425: 13,
        47425: 14,
        67425: 15,
        97425: 16,
        147425: 17,
        222425: 18,
        322425: 19,
        522425: 20,
        822425: 21,
        1222425: 22,
        1722425: 23,
        2322425: 24,
        3022425: 25,
        3822425: 26,
        4722425: 27,
        5722425: 28,
        6822425: 29,
        8022425: 30,
        9322425: 31,
        10722425: 32,
        12222425: 33,
        13822425: 34,
        15522425: 35,
        17322425: 36,
        19222425: 37,
        21222425: 38,
        23322425: 39,
        25522425: 40,
        27822425: 41,
        30222425: 42,
        32722425: 43,
        35322425: 44,
        38072425: 45,
        40972425: 46,
        44072425: 47,
        47472425: 48,
        51172425: 49,
        55172425: 50,
        59472425: 51,
        64072425: 52,
        68972425: 53,
        74172425: 54,
        79672425: 55,
        85472425: 56,
        91572425: 57,
        97972425: 58,
        104672425: 59,
        111672425: 60,
    }
    if skill == "SKILL_FARMING" and exp > 55172425:
        return get_farming_level_cap(data, exp, True)
    if skill in ["SKILL_TAMING", "SKILL_FORAGING", "SKILL_CARPENTRY", "SKILL_FISHING", "SKILL_ALCHEMY"] and exp >= 55172425:
        return f"Level: 50\nOverflow: {format_TBMK(exp - 55172425)}"
    previous = 0
    for i in skills.keys():
        level = skills[i]
        if exp >= i:
            if level == cap:
                return f"Level: {level}\nOverflow: {format_TBMK(exp - i)}"
            else:
                previous = i
        else:
            level = round(level - 1 + (exp - previous) / (i - previous), 2)
            return f"Level: {level}\nOverflow: 0"


def get_skill_lvl(skill, exp, data, cap=60):
    skills = {
        50: 1,
        175: 2,
        375: 3,
        675: 4,
        1175: 5,
        1925: 6,
        2925: 7,
        4425: 8,
        6425: 9,
        9925: 10,
        14925: 11,
        22425: 12,
        32425: 13,
        47425: 14,
        67425: 15,
        97425: 16,
        147425: 17,
        222425: 18,
        322425: 19,
        522425: 20,
        822425: 21,
        1222425: 22,
        1722425: 23,
        2322425: 24,
        3022425: 25,
        3822425: 26,
        4722425: 27,
        5722425: 28,
        6822425: 29,
        8022425: 30,
        9322425: 31,
        10722425: 32,
        12222425: 33,
        13822425: 34,
        15522425: 35,
        17322425: 36,
        19222425: 37,
        21222425: 38,
        23322425: 39,
        25522425: 40,
        27822425: 41,
        30222425: 42,
        32722425: 43,
        35322425: 44,
        38072425: 45,
        40972425: 46,
        44072425: 47,
        47472425: 48,
        51172425: 49,
        55172425: 50,
        59472425: 51,
        64072425: 52,
        68972425: 53,
        74172425: 54,
        79672425: 55,
        85472425: 56,
        91572425: 57,
        97972425: 58,
        104672425: 59,
        111672425: 60,
    }
    level50cap_skills = ["SKILL_TAMING", "SKILL_FORAGING", "SKILL_CARPENTRY", "SKILL_FISHING", "SKILL_ALCHEMY"]
    if skill == "SKILL_FARMING" and exp > 55172425:
        return get_farming_level_cap(data, exp, False)
    if skill in level50cap_skills:
        if exp >= 55172425:
            return 50
    previous = 0
    for i in skills.keys():
        level = skills[i]
        if exp >= i:
            if level == cap:
                return 60
            else:
                previous = i
        else:
            level = round(level - 1 + (exp - previous) / (i - previous), 2)
            return level




def get_slayer_lvl(key, exp):
    slayers = {
        5: 1,
        15: 2,
        200: 3,
        1000: 4,
        5000: 5,
        20000: 6,
        100000: 7,
        400000: 8,
        1000000: 9,
    }
    if key == "vampire":
        if exp >= 5000:
            return 5
    for i in slayers.keys():
        if exp >= i:
            if exp >= 1000000:
                return 9
            else:
                pass
        else:
            return slayers[i] - 1


def get_dungeon_lvl(exp):
    dungeons = {
        50: 1,
        125: 2,
        235: 3,
        395: 4,
        625: 5,
        955: 6,
        1425: 7,
        2095: 8,
        3045: 9,
        4385: 10,
        6275: 11,
        8940: 12,
        12700: 13,
        17960: 14,
        25340: 15,
        35640: 16,
        50040: 17,
        70040: 18,
        97640: 19,
        135640: 20,
        188140: 21,
        259640: 22,
        356640: 23,
        488640: 24,
        668640: 25,
        911640: 26,
        1239640: 27,
        1684640: 28,
        2284640: 29,
        3084640: 30,
        4149640: 31,
        5559640: 32,
        7459640: 33,
        9959640: 34,
        13259640: 35,
        17559640: 36,
        23159640: 37,
        30359640: 38,
        39559640: 39,
        51559640: 40,
        66559640: 41,
        85559640: 42,
        109559640: 43,
        139559640: 44,
        177559640: 45,
        225559640: 46,
        285559640: 47,
        360559640: 48,
        453559640: 49,
        569809640: 50,
    }
    exp = int(exp)
    previous = 0

    for i in dungeons.keys():
        level = dungeons[i]
        if exp >= i:
            if exp >= 569809640:
                return 50
            else:
                previous = i
        else:
            level = level - 1 + (exp - previous) / (i - previous)
            return round(level, 1)


def get_hotm_lvl(exp, cap=7):
    hotm = {
        0: 1,
        3000: 2,
        12000: 3,
        37000: 4,
        97000: 5,
        197000: 6,
        347000: 7,
    }
    previous = 0
    for i in hotm.keys():
        level = hotm[i]
        if exp >= i:
            if level == cap:
                return level
            else:
                previous = i
        else:
            level = round(level - 1 + (exp - previous) / (i - previous), 1)
            return level


def format_TBMK(number):
    if -999999999 <= number < -1000000:
        return f"{number / 1000000:.2f}m"
    elif -999999 <= number < -1000:
        return f"{number / 1000:.2f}k"
    elif -1000 <= number <= 999999:
        return f"{number / 1000:.2f}k"
    elif 1000000 <= number <= 999999999:
        return f"{number / 1000000:.2f}m"
    elif 1000000000 <= number <= 999999999999:
        return f"{number / 1000000000:.2f}b"
    else:
        return str(number)



def get_minion_slots(exp, cap=26):
    minions = {
        0: 5,
        5: 6,
        15: 7,
        30: 8,
        50: 9,
        75: 10,
        100: 11,
        125: 12,
        150: 13,
        175: 14,
        200: 15,
        225: 16,
        250: 17,
        275: 18,
        300: 19,
        350: 20,
        400: 21,
        450: 22,
        500: 23,
        550: 24,
        600: 25,
        650: 26,
    }
    for i in minions.keys():
        level = minions[i]
        if exp >= i:
            if level == cap:
                return level
        else:
            level = level - 1
            return level


def format_weight_number(number):
    if 0 <= number < 10000000:
        return f"{number:.0f}"
