import os, json, copy
from random import SystemRandom

class SplatoonData(object):
    __LOADED = False
    __SPECIALS = None
    __WEAPONS = None
    __SUBS = None
    __ABILITIES = None
    REQUIRED_PRIMARIES = []
    REQUIRED_SECONDARIES = []
    RESTRICTED_PRIMARIES = []
    RESTRICTED_SECONDARIES = []
    RANDOM = SystemRandom()
    DIR = os.path.dirname(os.path.realpath(__file__))

    def __init__(self):
        raise Exception("SplatoonData is a static class!")

    @staticmethod
    def list_in_list(list_one, list_two):
        list_one = copy.deepcopy(list_one)
        list_two = copy.deepcopy(list_two)
        
        count = 0
        for item in list_one:
            if item in list_two:
                list_two.remove(item)
                count += 1
        
        if count == len(list_one):
            return True 
        else:
            return False

    @staticmethod
    def get_special(special):
        SplatoonData.__load_specials()
        return SplatoonData.__SPECIALS[special]

    @staticmethod
    def get_weapon(weapon):
        SplatoonData.__load_weapons()
        return SplatoonData.__WEAPONS[weapon]

    @staticmethod
    def get_sub(sub):
        SplatoonData.__load_subs()
        return SplatoonData.__SUBS[sub]

    @staticmethod
    def get_ability(ability):
        SplatoonData.__load_abilities()
        return SplatoonData.__ABILITIES[ability]

    @staticmethod
    def get_ability_names():
        abilities = [
            "Ink Saver Sub",
            "Ink Saver Main",
            # "Bomb Defense", # TODO
            "Special Charge Up",
            "Quick Respawn",
            "Special Saver",
            "Swim Speed Up",
            "Special Power Up",
            "Ink Recovery Up",
            "Ink Resistance Up",
            "Quick Super Jump",
            "Run Speed Up",
            "Sub Power Up",
            # "Main Power Up", # TODO
            "Respawn Punisher",
            "Ninja Squid"
        ]

        return abilities

    @staticmethod
    def get_random_ability():
        # SplatoonData.__load_abilities()
        abilities = [
            "Ink Saver Sub",
            "Ink Saver Main",
            # "Bomb Defense", # TODO
            "Special Charge Up",
            "Quick Respawn",
            "Special Saver",
            "Swim Speed Up",
            "Special Power Up",
            "Ink Recovery Up",
            "Ink Resistance Up",
            "Quick Super Jump",
            "Run Speed Up",
            "Sub Power Up",
            # "Main Power Up", # TODO
            "Respawn Punisher",
            "Ninja Squid"
        ]

        random_index = SplatoonData.RANDOM.randint(0, len(abilities) - 1)
        return abilities[random_index]

    @staticmethod
    def __load_specials():
        if SplatoonData.__SPECIALS is None:
            with open(SplatoonData.DIR + "/specials.json", "r", encoding="utf-8") as specials_json:
                specials = json.loads(specials_json.read())
                SplatoonData.__SPECIALS = {}
                for i in range(len(specials)):
                    SplatoonData.__SPECIALS[specials[i]["name"]] = specials[i]

    @staticmethod
    def __load_weapons():
        if SplatoonData.__WEAPONS is None:
            with open(SplatoonData.DIR + "/weapons.json", "r", encoding="utf-8") as weapons_json:
                weapons = json.loads(weapons_json.read())
                SplatoonData.__WEAPONS = {}
                for i in range(len(weapons)):
                    SplatoonData.__WEAPONS[weapons[i]["name"]] = weapons[i]

    @staticmethod
    def __load_subs():
        if SplatoonData.__SUBS is None:
            with open(SplatoonData.DIR + "/subs.json", "r", encoding="utf-8") as subs_json:
                subs = json.loads(subs_json.read())
                SplatoonData.__SUBS = {}
                for i in range(len(subs)):
                    SplatoonData.__SUBS[subs[i]["name"]] = subs[i]

    @staticmethod
    def __load_abilities():
        if SplatoonData.__ABILITIES is None:
            with open(SplatoonData.DIR + "/abilities.json", "r", encoding="utf-8") as abilities_json:
                abilities = json.loads(abilities_json.read())
                SplatoonData.__ABILITIES = {}
                for key in abilities.keys():
                    SplatoonData.__ABILITIES[key] = abilities[key]
