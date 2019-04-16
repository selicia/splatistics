import json, math
from random import SystemRandom
from splatoon_data import SplatoonData

class Loadout(object):
    def __init__(self, weapon, sub, special):
        self.weapon = SplatoonData.get_weapon(weapon)
        self.sub = SplatoonData.get_sub(sub)
        self.special = SplatoonData.get_special(special)
        self.primaries = {}
        self.secondaries = {}
        self.fitness_score = 0

    def add_primary(self, ability):
        if len(self.primaries) < 3:
            if ability not in self.primaries:
                self.primaries[ability] = 0
            self.primaries[ability] += 1

    def add_secondary(self, ability):
        if len(self.secondaries) < 9:
            if ability not in self.secondaries:
                self.secondaries[ability] = 0
            self.secondaries[ability] += 1

    def get_fitness(self):
        for ability in list(SplatoonData.__ABILITIES.keys()):
            primary_ability_points = [x for x in self.primaries if x == ability] * 10
            secondary_ability_points = [x for x in self.secondaries if x == ability] * 3
            ability_points = primary_ability_points + secondary_ability_points
            p = self.calcP(ability_points)

            """
            1. Swim Speed Up provides a single benefit the optimizer evaluates.
               If the Loadout uses Respawn Punisher, it's penalty is factored in.
            """
            if ability == "Swim Speed Up":
                if self.weapon["speedLevel"] == "Low":
                    swim_speed_parameters = SplatoonData.get_ability(ability)["Heavy"]
                if self.weapon["speedLevel"] == "Middle":
                    swim_speed_parameters = SplatoonData.get_ability(ability)["Mid"]
                if self.weapon["speedLevel"] == "High":
                    swim_speed_parameters = SplatoonData.get_ability(ability)["Light"]

                # NOTE: Non base stat abilities aren't implement currently
                if "Ninja Squid" in self.primaries:
                    p *= 0.8

                s = self.calcS(swim_speed_parameters)
                swim_speed = self.calcRes(swim_speed_parameters, p, s)

                # NOTE: Non base stat abilities aren't implement currently
                if "Ninja Squid" in self.primaries:
                    swim_speed *= 0.9

                delta = abs((swim_speed / swim_speed_parameters[2] - 1) * 100)
                self.fitness_score += delta

            """
            2. Run Speed Up provides the following benefits the optimizer evaluates:
                i.  Run Speed while not firing or charging
                ii. Run Speed while firing
                iii. Run Speed while charging
            """
            if ability == "Run Speed Up":
                # i. Run Speed while not firing or charging
                if self.weapon["speedLevel"] == "Low":
                    run_speed_parameters = SplatoonData.get_ability(ability)["Heavy"]
                if self.weapon["speedLevel"] == "Middle":
                    run_speed_parameters = SplatoonData.get_ability(ability)["Mid"]
                if self.weapon["speedLevel"] == "High":
                    run_speed_parameters = SplatoonData.get_ability(ability)["Light"]                

                s = self.calcS(run_speed_parameters)
                run_speed = self.calcRes(run_speed_parameters, p, s)
                delta = abs((run_speed / run_speed_parameters[2] - 1) * 100)
                self.fitness_score += delta

                # ii. Run Speed while firing
                if self.weapon["class"].lower() == "brush" or self.weapon["class"].lower() == "roller":
                    pass
                else:
                    run_speed_firing_params = SplatoonData.get_ability(ability)["Shooting"][self.weapon["shootingSpeed"]]
                    s = self.calcS(run_speed_firing_params)
                    run_speed_firing = self.calcRes(run_speed_firing_params, p, s) * self.weapon["baseSpeed"]
                    delta = abs((run_speed_firing / self.weapon["baseSpeed"] - 1) * 100)
                    self.fitness_score += delta

                # iii. Run Speed while charging
                if self.weapon["class"].lower() == "splatling" or self.weapon["class"].lower() == "brella":
                    run_speed_charging = self.calcRes(run_speed_firing_params, p, s) * self.weapon["chargeSpeed"]
                    delta = abs((run_speed_charging / self.weapon["chargeSpeed"] - 1) * 100)
                    self.fitness_score += delta

            """
            3. Ink Resistance Up provides the following benefits this optimizer evaluates:
                i.   Increased Run Speed in Enemy Ink
                ii.  Reduced Damage per Frame from Enemy Ink
                iii. Reduced Damage Limit from Enemy Ink
            """
            if ability == "Ink Resistance Up":
                # i. Increased Run Speed in Enemy Ink
                ink_resistance_parameters = SplatoonData.get_ability(ability)["Run"]
                s = self.calcS(ink_resistance_parameters)
                run_speed_enemy_ink = self.calcRes(ink_resistance_parameters, p, s)
                delta = abs((run_speed_enemy_ink / ink_resistance_parameters[2] - 1) * 100)
                self.fitness_score += delta

                # ii. Reduced Damage per Frame from Enemy Ink
                ink_resistance_parameters = SplatoonData.get_ability(ability)["Dmg Per Frame"]
                s = self.calcS(ink_resistance_parameters)
                ink_damage_per_frame = self.calcRes(ink_resistance_parameters, p, s)
                delta = abs((ink_damage_per_frame / ink_resistance_parameters[2] - 1) * 100)
                self.fitness_score += delta

                # iii. Reduced Damage Limit from Enemy Ink
                ink_resistance_parameters = SplatoonData.get_ability(ability)["Dmg Limit"]
                s = self.calcS(ink_resistance_parameters)
                ink_damage_limit = self.calcRes(ink_resistance_parameters, p, s)
                delta = abs((ink_damage_per_frame / ink_resistance_parameters[2] - 1) * 100)
                self.fitness_score += delta

            """
            4. Ink Recovery Up provides the following benefits this optimizer evaluates:
                i.  Increased Ink Recovery in Kid Form
                ii. Increased Ink Recovery in Squid Form
            """
            if ability == "Ink Recovery Up":
                # i. Increased Ink Recovery in Kid Form
                ink_recovery_parameters = SplatoonData.get_ability(ability)["Standing"]
                s = self.calcS(ink_recovery_parameters)
                refill_rate = self.calcRes(ink_recovery_parameters, p, s)
                refill_time = refill_rate / 60.0
                delta = abs((10 / refill_time) * 100)
                self.fitness_score += delta

                # ii. Increased Ink Recovery in Squid Form
                ink_recovery_parameters = SplatoonData.get_ability(ability)["In Ink"]
                s = self.calcS(ink_recovery_parameters)
                refill_rate = self.calcRes(ink_recovery_parameters, p, s)
                refill_time = refill_rate / 60.0
                delta = abs((3 / refill_time) * 100)
                self.fitness_score += delta
            
            """
            5. Ink Saver Main provides a single benefit the optimizer evaluates.
            """
            if ability == "Ink Saver Main":
                if self.weapon["inkSaver"] == "Low":
                    ink_saver_main_parameters = SplatoonData.get_ability(ability)["Low"]
                if self.weapon["inkSaver"] == "Middle":
                    ink_saver_main_parameters = SplatoonData.get_ability(ability)["Mid"]
                if self.weapon["inkSaver"] == "High":
                    ink_saver_main_parameters = SplatoonData.get_ability(ability)["High"]    

                s = self.calcS(ink_saver_main_parameters)
                reduction = self.calcRes(ink_saver_main_parameters, p, s);
                costPerShot = self.weapon["inkPerShot"] * reduction;
                delta = abs((costPerShot / self.weapon["inkPerShot"] - 1) * 100)
                self.fitness_score += delta

            """
            6. Ink Saver Sub provides a single benefit the optimizer evaluates.
            """
            if ability == "Ink Saver Sub":
                if self.sub["inkSaver"] == "A":
                    ink_saver_sub_parameters = SplatoonData.get_ability(ability)["A"]
                if self.sub["inkSaver"] == "B":
                    ink_saver_sub_parameters = SplatoonData.get_ability(ability)["B"]
                if self.sub["inkSaver"] == "C":
                    ink_saver_sub_parameters = SplatoonData.get_ability(ability)["C"]
                if self.sub["inkSaver"] == "D":
                    ink_saver_sub_parameters = SplatoonData.get_ability(ability)["D"]
                if self.sub["inkSaver"] == "E":
                    ink_saver_sub_parameters = SplatoonData.get_ability(ability)["E"]
                if self.sub["inkSaver"] == "F":
                    ink_saver_sub_parameters = SplatoonData.get_ability(ability)["F"]
                
                s = self.calcS(ink_saver_sub_parameters)
                reduction = self.calcRes(ink_saver_sub_parameters, p, s)
                costPerSub = self.sub["cost"] * reduction
                delta = abs((costPerSub / self.sub["cost"] - 1) * 100)
                self.fitness_score += delta

            """
            7. Special Charge Up provides a single benefit the optimizer evaluates.
            """
            if ability == "Special Charge Up":
                special_charge_speed_parameters = SplatoonData.get_ability(ability)["default"]
                s = self.calcS(special_charge_speed_parameters)
                special_charge_speed = self.calcRes(special_charge_speed_parameters, p, s)
                delta = abs((special_charge_speed / special_charge_speed_parameters[2] - 1) * 100)
                self.fitness_score += delta

            """
            8. Special Saver provides two different benefits the optimizer evaluates:
                i.  Special Saved when killed
                ii. Special Saved when killed while using it
            """
            if ability == "Special Saver":
                #i. Special Saved when killed
                special_saver_parameters = SplatoonData.get_ability(ability)["default"]

                # NOTE: Non base stat abilities aren't implement currently
                if "Respawn Punisher" in self.primaries:
                    ability_points *= 0.7

                s = self.calcS(special_saver_parameters)
                modifier = self.calcRes(special_saver_parameters, p, s)
                special_saved = 100.0 * modifier

                # NOTE: Non base stat abilities aren't implement currently
                if "Respawn Punisher" in self.primaries:
                    special_saved *= 0.775

                delta = abs((special_saved / 100 - 1) * 100)
                self.fitness_score += delta

                # ii. Special Saved when killed while using it
                if self.special["name"] == "Splashdown":
                    special_saver_parameters = SplatoonData.get_ability(ability)["Splashdown"]
                else:
                    special_saver_parameters = SplatoonData.get_ability(ability)["default"]
                
                s = self.calcS(special_saver_parameters)               
                modifier = self.calcRes(special_saver_parameters, p, s);
                special_saved = 100.0 * modifier
                
                if special_saved > 100:
                    special_saved = 100.0

                # NOTE: Non base stat abilities aren't implement currently
                if "Respawn Punisher" in self.primaries:
                    special_saved *= 0.775

                delta = abs((special_saved / 100 - 1) * 100)
                self.fitness_score += delta

            """
            9. Special Power Up provides a single benefit the optimizer evaluates.
               However, the benefit varies per Special.
            """
            if ability == "Special Power Up":
                if self.weapon["special"]["name"] == "Curling-Bomb Launcher":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Curling Bomb Launcher"]

                if "Launcher" in self.weapon["special"]["name"]:
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Other Bomb Launcher"];

                if self.weapon["special"]["name"] == "Ink Armor":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Ink Armor Duration"];

                if self.weapon["special"]["name"] == "Inkjet":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Inkjet Duration"];
                 
                if self.weapon["special"]["name"] == "Ink Storm":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Ink Storm Duration"];

                if self.weapon["special"]["name"] == "Sting Ray":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Sting Ray Duration"];

                if self.weapon["special"]["name"] == "Baller":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Baller HP"];

                if self.weapon["special"]["name"] == "Tenta Missiles":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Tenta Missiles Target Circle Radius"];

                if self.weapon["special"]["name"] == "Splashdown":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Splash Down Burst Radius Close"];

                if self.weapon["special"]["name"] == "Bubble Blower":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Bubble Blower Bubble Radius Multiplier"];
                    s = self.calcS(special_power_up_parameters)
                    modifier = self.calcRes(special_power_up_parameters, p, s)
                    min_bubble_radius = special_power_up_parameters[2] * SplatoonData.get_special("Bubble Blower")["radius"]["Max"]
                    bubble_radius = modifier * SplatoonData.get_special("Bubble Blower")["radius"]["Max"]
                    delta = abs((bubble_radius / min_bubble_radius - 1) * 100)

                if self.weapon["special"]["name"] == "Booyah Bomb":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Booyah Ball Auto Charge Increase"]
                    s = self.calcS(special_power_up_parameters)
                    modifier = self.calcRes(special_power_up_parameters, p, s)
                    charge_time = SplatoonData.get_special("Booyah Bomb")["duration"] - (SplatoonData.get_special("Booyah Bomb")["duration"] * modifier)
                    max_charge_time = SplatoonData.get_special("Booyah Bomb")["duration"] - (SplatoonData.get_special("Booyah Bomb")["duration"] * special_power_up_parameters[2])
                    delta = abs((charge_time / max_charge_time - 1) * 100)

                if not delta:
                    s = self.calcS(special_power_up_parameters)
                    result = self.calcRes(special_power_up_parameters, p, s)
                    delta = abs((result / special_power_up_parameters[2] - 1) * 100)

                self.fitness_score += delta

            """
            10. Sub Power Up provides a single benefit the optimizer evaluates.
                However, the benefit varies per Sub Weapon.
            """
            if ability == "Sub Power Up":
                if self.sub["name"] in ["Autobomb", "Burst Bomb", "Curling Bomb", "Splat Bomb", "Suction Bomb"]:
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["General Bomb Distance Up"]
                    # s = self.calcS(sub_power_up_parameters)
                    # sub_range = self.calcRes(sub_power_up_parameters, p, s)
                    # min_sub_range = sub_power_up_parameters[2]
                    # delta = abs((sub_range / min_sub_range - 1) * 100)

                if self.sub["name"] == "Fizzy Bomb":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Fizzy Bomb Distance Up"]
                    # s = self.calcS(sub_power_up_parameters)
                    # sub_range = self.calcRes(sub_power_up_parameters, p, s)
                    # min_sub_range = sub_power_up_parameters[2]
                    # delta = abs((sub_range / min_sub_range - 1) * 100)

                if self.sub["name"] == "Point Sensor":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Point Sensor Distance Up"]
                    # s = self.calcS(sub_power_up_parameters)
                    # scan_radius = self.calcRes(sub_power_up_parameters, p, s)
                    # min_scan_radius = sub_power_up_parameters[2]
                    # delta = abs((scan_radius / min_scan_radius - 1) * 100)

                if self.sub["name"] == "Toxic Mist":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Ink Mine Mark Time Duration"]
                    s = self.calcS(sub_power_up_parameters)
                    # duration = self.calcRes(sub_power_up_parameters, p, s)
                    # min_duration = sub_power_up_parameters[2]
                    # delta = abs((duration / min_duration - 1) * 100)

                if self.sub["name"] == "Ink Mine":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Ink Mine Mark Radius"]

                if self.sub["name"] == "Splash Wall":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Splash Wall Max HP"]

                if self.sub["name"] == "Sprinkler":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Sprinkler First Phase Duration"]

                if self.sub["name"] == "Squid Beakon":
                    jump_parameters = SplatoonData.get_ability("Quick Super Jump")["Jump"]
                    s = self.calcS(jump_parameters)
                    jump_duration = self.calcRes(jump_parameters, p, s)

                    prepare_parameters = SplatoonData.get_ability("Quick Super Jump")["Prepare"]
                    s = self.calcS(prepare_parameters)
                    prepare_duration = self.calcRes(prepare_parameters, p, s)

                    total_duration = jump_duration + prepare_duration
                    max_duration = jump_parameters[2] + prepare_parameters[2]
                    delta = abs((total_duration / max_duration[2] - 1) * 100)

                if self.sub["name"] == "Torpedo":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Torpedo Distance Up"]
                    
                if not delta:
                    s = self.calcS(sub_power_up_parameters)
                    result = self.calcRes(sub_power_up_parameters, p, s)
                    delta = abs((result / sub_power_up_parameters[2] - 1) * 100)
                
                self.fitness_score += delta

            """
            11. Quick Super Jump provides two benefits the optimizer evaluates:
                i.  Reduced Super Jump time in kid form
                ii. Reduced Super Jump time in squid form
            """




            # if ability == "Main Power Up":
            #     for key in SplatoonData.get_ability(ability)[self.weapon]:
            #         if "params" in key:
            #             values = SplatoonData.get_ability(ability)[self.weapon][key]
            #             break
            # else:
            #     for key in SplatoonData.get_ability(ability):
            #         values = SplatoonData.get_ability(ability)[key]
            #         s = self.calcS(values)
            #         break

            # result = self.calcRes(values, p, s)
            # self.fitness_score += ((result / values[2] - 1) * 100)



    def calcP(self, ability_score):
        return min(3.3*ability_score - 0.027*(ability_score**2),100)

    def calcS(self, values):
        _max = values[0];
        _mid = values[1];
        _min = values[2];
        return (_mid - _min) / (_max - _min);

    def calcRes(self, values, p, s):
        _max = values[0];
        _mid = values[1];
        _min = values[2];
        return _min + (_max - _min) * self.lerpN(p / 100, s)

    def lerpN(self, p, s):
        s = float("{0:.3f}".format(s))
        if s == 0.5:
            return p
        if p == 0.0:
            return p
        if p == 1.0:
            return p
        if s != 0.5:
            return math.exp(-1 * (math.log(p) * math.log(s) / math.log(2)))         

with open("ap_params.json", "r") as ap_param_file:
    ap_params = json.loads(ap_param_file.read())
    ap_keys = []
    for key in ap_params:
        ap_keys.append(key)

loadout = Loadout(".96 Gal", "Sprinkler", "Ink Armor")
random = SystemRandom()

# Randomly add some Primaries
for i in range(3):
    random_index = random.randint(0, len(ap_keys)-1)
    loadout.add_primary(ap_keys[random_index])

# Randomly add some Secondaries
for i in range(9):
    random_index = random.randint(0, len(ap_keys)-1)
    loadout.add_secondary(ap_keys[random_index])

loadout.get_fitness()
print(loadout.primaries)
print(loadout.secondaries)
print(loadout.fitness_score)



