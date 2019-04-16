import json
from random import SystemRandom

class SplatoonData(object):
    __LOADED = False
    __SPECIALS = None
    __WEAPONS = None
    __SUBS = None
    __ABILITIES = None
    __RANDOM = SystemRandom()

    def __init__(self):
        raise Exception("SplatoonData is a static class!")

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
    def get_random_ability():
        SplatoonData.__load_abilities()
        random_index = SplatoonData.__RANDOM.randint(0, len(SplatoonData.__ABILITIES) - 1)
        return list(SplatoonData.__ABILITIES.keys())[random_index]

    @staticmethod
    def __load_specials():
        if SplatoonData.__SPECIALS is None:
            with open("specials.json", "r", encoding="utf-8") as specials_json:
                specials = json.loads(specials_json.read())
                SplatoonData.__SPECIALS = {}
                for i in range(len(specials)):
                    SplatoonData.__SPECIALS[specials[i]["name"]] = specials[i]

    @staticmethod
    def __load_weapons():
        if SplatoonData.__WEAPONS is None:
            with open("weapons.json", "r", encoding="utf-8") as weapons_json:
                weapons = json.loads(weapons_json.read())
                SplatoonData.__WEAPONS = {}
                for i in range(len(weapons)):
                    SplatoonData.__WEAPONS[weapons[i]["name"]] = weapons[i]

    @staticmethod
    def __load_subs():
        if SplatoonData.__SUBS is None:
            with open("subs.json", "r", encoding="utf-8") as subs_json:
                subs = json.loads(subs_json.read())
                SplatoonData.__SUBS = {}
                for i in range(len(subs)):
                    SplatoonData.__SUBS[subs[i]["name"]] = subs[i]

    @staticmethod
    def __load_abilities():
        if SplatoonData.__ABILITIES is None:
            with open("abilities.json", "r", encoding="utf-8") as abilities_json:
                abilities = json.loads(abilities_json.read())
                SplatoonData.__ABILITIES = {}
                for key in abilities.keys():
                    SplatoonData.__ABILITIES[key] = abilities[key]


if __name__ == "__main__":
    print("Splashdown Damage: " + str(SplatoonData.get_special("Splashdown")["damage"]))
    print("# Specials: " + str(len(SplatoonData.__SPECIALS)))
    print("Ink Saver Main: " + str(SplatoonData.get_ability("Ink Saver Main")["High"]))
    print("# Abilities: " + str(len(SplatoonData.__ABILITIES)))

    random_ability = SplatoonData.get_random_ability()
    print("Random Ability Name: " + random_ability)
    print("Random Ability Params: " + str(SplatoonData.__ABILITIES[random_ability]))
