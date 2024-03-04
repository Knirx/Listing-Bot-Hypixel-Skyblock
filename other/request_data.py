import requests, json, os, re
from dotenv import load_dotenv
from other.calcs import *

load_dotenv(".env")
hypixelAPIkey = os.getenv("API_KEY")
skyhelper_key = os.getenv("SKYHELPER_KEY")
host = os.getenv("HOST")


def get_uuid(username):
    try:
        return requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}").json()["id"]
    except:
        return None


def get_number_of_collections():
    total_collections = 0
    request = requests.get(f"https://api.hypixel.net/resources/skyblock/collections?key={hypixelAPIkey}").json()
    for key, value in request["collections"].items():
        total_collections += len(value["items"])
    return total_collections

def get_collection_data():
    return requests.get(f"https://api.hypixel.net/resources/skyblock/collections?key={hypixelAPIkey}").json()

def get_main_profile_and_index(uuid):
    index = -1
    data = requests.get(f"https://api.hypixel.net/v2/skyblock/profiles?key={hypixelAPIkey}&uuid={uuid}").json()
    for profiles in data["profiles"]:
        index += 1
        if profiles["selected"] is True:
            return [profiles["members"][uuid], profiles, index]


def get_main_profile(uuid):
    data = requests.get(f"https://api.hypixel.net/v2/skyblock/profiles?key={hypixelAPIkey}&uuid={uuid}").json()
    for profiles in data["profiles"]:
        if profiles["selected"] is True:
            return profiles["members"][uuid]

def get_skills_overflow(base_data):
    empty_skill_dict = {
        "skyblockLevel": "",
        "skillAverage": "",
        "SKILL_FISHING": "",
        "SKILL_ALCHEMY": "",
        "SKILL_MINING": "",
        "SKILL_FARMING": "",
        "SKILL_ENCHANTING": "",
        "SKILL_TAMING": "",
        "SKILL_FORAGING": "",
        "SKILL_CARPENTRY": "",
        "SKILL_COMBAT": "",
    }
    dict_length = 0
    all_dict_values = 0
    for key, value in base_data["player_data"]["experience"].items():
        if key == "SKILL_RUNECRAFTING" or key == "SKILL_SOCIAL" or key == "SKILL_DUNGEONEERING":
            continue
        level = get_skill_lvl_overflow(base_data, key, value)
        empty_skill_dict[key] = level
        dict_length += 1
        all_dict_values += float(level.split(": ")[1].split("\n")[0])
    return empty_skill_dict


def get_skills(base_data):
    empty_skill_dict = {
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
    }
    dict_length = 0
    all_dict_values = 0
    for key, value in base_data["player_data"]["experience"].items():
        if key == "SKILL_RUNECRAFTING" or key == "SKILL_SOCIAL" or key == "SKILL_DUNGEONEERING":
            continue
        level = get_skill_lvl(key, value,  base_data)
        empty_skill_dict[key] = level
        dict_length += 1
        all_dict_values += level
    empty_skill_dict["skyblockLevel"] = int(base_data["leveling"]["experience"]/100)
    try:
        empty_skill_dict["skillAverage"] = f"{(all_dict_values / dict_length):.2f}"
    except:
        pass
    return empty_skill_dict


def get_dungeon_level(data):
    return get_dungeon_lvl(int(data["dungeons"]["dungeon_types"]["catacombs"]["experience"]))

def get_skyhelper_data(uuid):
    try:
        return get_networth(requests.get(f"http://{host}/v1/profiles/{uuid}?key={skyhelper_key}").json()["data"][0])
    except:
        return {"networth": 0, "soulboundNetworth": 0, "unsoulboundNetworth": 0, "coins": 0, "weight": 0, "username": "", "rank": ""}

def get_skyhelper_data_only(uuid):
    try:
        return requests.get(f"http://{host}/v1/profiles/{uuid}?key={skyhelper_key}").json()["data"][0]
    except:
        return {"networth": 0, "soulboundNetworth": 0, "unsoulboundNetworth": 0, "coins": 0, "weight": 0, "username": "", "rank": ""}


def get_networth_with_types(skyhelper_data):
    pattern = r'§\w'
    networth_dict = {"networth": 0, "soulboundNetworth": 0, "unsoulboundNetworth": 0, "coins": 0, "weight": 0,
                     "username": "", "rank": "", "uuid": "", "purse": 0, "bank": 0}
    networth_dict["networth"] = format_TBMK(int(skyhelper_data["networth"]["networth"]))
    networth_dict["purse"] = format_TBMK(int(skyhelper_data["networth"]["purse"]))
    networth_dict["bank"] = format_TBMK(int(skyhelper_data["networth"]["bank"]))
    networth_dict["soulboundNetworth"] = format_TBMK(
        int(skyhelper_data["networth"]["networth"]) - int(skyhelper_data["networth"]["unsoulboundNetworth"]))
    networth_dict["unsoulboundNetworth"] = format_TBMK(int(skyhelper_data["networth"]["unsoulboundNetworth"]))
    networth_dict["coins"] = format_TBMK(
        int(skyhelper_data["networth"]["purse"]) + int(skyhelper_data["networth"]["bank"]))
    try:
        networth_dict["weight"] = format_weight_number(int(skyhelper_data["weight"]["senither"]["weight"]) + int(
            skyhelper_data["weight"]["senither"]["weight_overflow"]))
    except:
        pass
    networth_dict["rank"] = re.sub(pattern, "", skyhelper_data["rank"]).replace("[", "").replace("]", "")
    networth_dict["uuid"] = skyhelper_data["uuid"]
    networth_dict["username"] = skyhelper_data["username"]
    types_array = ["armor", "equipment", "wardrobe", "inventory", "enderchest", "accessories", "storage", "pets", "sacks"]
    for types_key, types_value in skyhelper_data["networth"]["types"].items():
        if types_key in types_array:
            networth_dict[f"SKYHELPER_TYPES_{types_key}"] = format_TBMK(int(types_value.get("total")))
    return networth_dict

def get_networth(skyhelper_data):
    pattern = r'§\w'
    networth_dict = {"networth": 0, "soulboundNetworth": 0, "unsoulboundNetworth": 0, "coins": 0, "weight": 0, "username": "", "rank": "", "uuid": ""}
    networth_dict["networth"] = format_TBMK(int(skyhelper_data["networth"]["networth"]))
    networth_dict["soulboundNetworth"] = format_TBMK(int(skyhelper_data["networth"]["networth"]) - int(skyhelper_data["networth"]["unsoulboundNetworth"]))
    networth_dict["unsoulboundNetworth"] = format_TBMK(int(skyhelper_data["networth"]["unsoulboundNetworth"]))
    networth_dict["coins"] = format_TBMK(int(skyhelper_data["networth"]["purse"]) + int(skyhelper_data["networth"]["bank"]))
    try:
        networth_dict["weight"] = format_weight_number(int(skyhelper_data["weight"]["senither"]["weight"]) + int(skyhelper_data["weight"]["senither"]["weight_overflow"]))
    except:
        pass
    networth_dict["rank"] = re.sub(pattern, "", skyhelper_data["rank"]).replace("[", "").replace("]", "")
    networth_dict["uuid"] = skyhelper_data["uuid"]
    networth_dict["username"] = skyhelper_data["username"]
    return networth_dict

def get_slayer(data):
    slayer_dict = {'zombie': 0, 'spider': 0, 'wolf': 0, 'enderman': 0, 'blaze': 0, 'vampire': 0}
    for key, value in data["slayer"]["slayer_bosses"].items():
        try:
            slayer_dict[key] = get_slayer_lvl(key, int(value["xp"]))
        except:
            continue
    return slayer_dict

def get_mining(data):
    mining_dict = {"hotmLevel": 0, "mithrilPowder": 0, "gemstonePowder": 0}
    try:
        mining_dict["hotmLevel"] = get_hotm_lvl(int(data["mining_core"]["experience"]))
    except:
        pass
    try:
        mining_dict["gemstonePowder"] = format_TBMK(int(data["mining_core"]["powder_spent_gemstone"]) + int(data["mining_core"]["powder_gemstone_total"]))
    except:
        pass
    try:
        mining_dict["mithrilPowder"] = format_TBMK(int(data["mining_core"]["powder_spent_mithril"]) + int(data["mining_core"]["powder_mithril_total"]))
    except:
        pass
    return mining_dict

def get_kuudra(data):
    kuudra_dict = {}
    needed_keys = ["mages_reputation", "barbarians_reputation"]
    for key, value in data["nether_island_player_data"].items():
        if key in needed_keys:
            kuudra_dict[key] = format_TBMK(value)
        elif key == "selected_faction":
          kuudra_dict["faction"] = value.capitalize()
    return kuudra_dict


def get_all(username, uuid):
    if uuid:
        main_profile = get_main_profile(uuid)
        skyhelper_data = get_skyhelper_data(uuid)
        skyhelper_request = get_skyhelper_data_only(uuid)
    else:
        uuid = get_uuid(username)
        if uuid is None:
            return None
        skyhelper_data = get_skyhelper_data(uuid)
        skyhelper_request = get_skyhelper_data_only(uuid)
        main_profile = get_main_profile(uuid)
    for skill_key, skill_value in get_skills(main_profile).items():
        gather_all_dict[skill_key] = skill_value
    gather_all_dict["dungeonLevel"] = get_dungeon_level(main_profile)
    for skyhelper_key, skyhelper_value in skyhelper_data.items():
        gather_all_dict[skyhelper_key] = skyhelper_value
    for slayer_key, slayer_value in get_slayer(main_profile).items():
        gather_all_dict[slayer_key] = slayer_value
    for mining_key, mining_value in get_mining(main_profile).items():
        gather_all_dict[mining_key] = mining_value
    for kuudra_key, kuudra_value in get_kuudra(main_profile).items():
        gather_all_dict[kuudra_key] = kuudra_value
    return [gather_all_dict, skyhelper_request, main_profile]
