import math
from splatoon_data import SplatoonData

class Loadout(object):
    def __init__(self, weapon, sub, special):
        self.weapon = SplatoonData.get_weapon(weapon)
        self.sub = SplatoonData.get_sub(sub)
        self.special = SplatoonData.get_special(special)
        self.primaries = []
        self.secondaries = []
        self.fitness_score = 0

    def __calcP(self, ability_score):
        return min(3.3*ability_score - 0.027*(ability_score**2),100)

    def __calcS(self, values):
        _max = values[0]
        _mid = values[1]
        _min = values[2]
        return (_mid - _min) / (_max - _min)

    def __calcRes(self, values, p, s):
        _max = values[0]
        _mid = values[1]
        _min = values[2]
        return _min + (_max - _min) * self.__lerpN(p / 100, s)

    def __lerpN(self, p, s):
        s = float("{0:.3f}".format(s))
        if s == 0.5:
            return p
        if p == 0.0:
            return p
        if p == 1.0:
            return p
        if s != 0.5:
            return math.exp(-1 * (math.log(p) * math.log(s) / math.log(2)))   

    def __add_primary(self, ability):
        if len(self.primaries) < 3:
            self.primaries.append(ability)

    def __add_secondary(self, ability):
        if len(self.secondaries) < 9:
            self.secondaries.append(ability)

    def randomize_abilities(self):
        random_primaries = [] + SplatoonData.REQUIRED_PRIMARIES
        random_secondaries = [] + SplatoonData.REQUIRED_SECONDARIES

        while len(random_primaries) < 3:
            while True:
                ability = SplatoonData.get_random_ability()
                if ability not in SplatoonData.RESTRICTED_PRIMARIES:
                    break
            random_primaries.append(ability)

        while len(random_secondaries) < 9:
            while True:
                ability = SplatoonData.get_random_ability()
                if ability != "Respawn Punisher" and ability != "Ninja Squid" and ability not in SplatoonData.REQUIRED_SECONDARIES:
                    break
            random_secondaries.append(ability)

        self.primaries = random_primaries
        self.secondaries = random_secondaries

    def get_fitness(self):
        for ability in SplatoonData.get_ability_names():
            primary_ability_points = len([x for x in self.primaries if x == ability]) * 10
            secondary_ability_points = len([x for x in self.secondaries if x == ability]) * 3
            ability_points = primary_ability_points + secondary_ability_points
            p = self.__calcP(ability_points)
            score = 0
            num_params = 0

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

                s = self.__calcS(swim_speed_parameters)
                swim_speed = self.__calcRes(swim_speed_parameters, p, s)

                # NOTE: Non base stat abilities aren't implement currently
                if "Ninja Squid" in self.primaries:
                    swim_speed *= 0.9

                score += abs((swim_speed / swim_speed_parameters[2] - 1) * 100)
                num_params += 1

                if num_params > 1:
                    self.fitness_score += (score / num_params) * (1 + (.1 * (num_params - 1)))
                else:
                    self.fitness_score += score

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

                s = self.__calcS(run_speed_parameters)
                run_speed = self.__calcRes(run_speed_parameters, p, s)
                score += abs((run_speed / run_speed_parameters[2] - 1) * 100)
                num_params += 1

                # ii. Run Speed while firing
                if self.weapon["class"].lower() == "brush" or self.weapon["class"].lower() == "roller":
                    pass
                else:
                    run_speed_firing_params = SplatoonData.get_ability(ability)["Shooting"][self.weapon["shootingSpeed"]]
                    s = self.__calcS(run_speed_firing_params)
                    run_speed_firing = self.__calcRes(run_speed_firing_params, p, s) * self.weapon["baseSpeed"]
                    delta = abs((run_speed_firing / self.weapon["baseSpeed"] - 1) * 100)
                    score += delta
                    num_params += 1

                # iii. Run Speed while charging
                if self.weapon["class"].lower() == "splatling" or self.weapon["class"].lower() == "brella":
                    run_speed_charging = self.__calcRes(run_speed_firing_params, p, s) * self.weapon["chargeSpeed"]
                    delta = abs((run_speed_charging / self.weapon["chargeSpeed"] - 1) * 100)
                    score += delta
                    num_params += 1

                if num_params > 1:
                    self.fitness_score += (score / num_params) * (1 + (.1 * (num_params - 1)))
                else:
                    self.fitness_score += score

            """
            3. Ink Resistance Up provides the following benefits this optimizer evaluates:
                i.   Increased Run Speed in Enemy Ink
                ii.  Reduced Damage per Frame from Enemy Ink
                iii. Reduced Damage Limit from Enemy Ink
            """
            if ability == "Ink Resistance Up":
                # i. Increased Run Speed in Enemy Ink
                ink_resistance_parameters = SplatoonData.get_ability(ability)["Run"]
                s = self.__calcS(ink_resistance_parameters)
                run_speed_enemy_ink = self.__calcRes(ink_resistance_parameters, p, s)
                score += abs((run_speed_enemy_ink / ink_resistance_parameters[2] - 1) * 100)
                num_params += 1

                # ii. Reduced Damage per Frame from Enemy Ink
                ink_resistance_parameters = SplatoonData.get_ability(ability)["Dmg Per Frame"]
                s = self.__calcS(ink_resistance_parameters)
                ink_damage_per_frame = self.__calcRes(ink_resistance_parameters, p, s)
                score += abs((ink_damage_per_frame / ink_resistance_parameters[2] - 1) * 100)
                num_params += 1

                # iii. Reduced Damage Limit from Enemy Ink
                ink_resistance_parameters = SplatoonData.get_ability(ability)["Dmg Limit"]
                s = self.__calcS(ink_resistance_parameters)
                ink_damage_limit = self.__calcRes(ink_resistance_parameters, p, s)
                score += abs((ink_damage_per_frame / ink_resistance_parameters[2] - 1) * 100)
                num_params += 1

                if num_params > 1:
                    self.fitness_score += (score / num_params) * (1 + (.1 * (num_params - 1)))
                else:
                    self.fitness_score += score            

            """
            4. Ink Recovery Up provides the following benefits this optimizer evaluates:
                i.  Increased Ink Recovery in Kid Form
                ii. Increased Ink Recovery in Squid Form
            """
            if ability == "Ink Recovery Up":
                # i. Increased Ink Recovery in Kid Form
                ink_recovery_parameters = SplatoonData.get_ability(ability)["Standing"]
                s = self.__calcS(ink_recovery_parameters)
                refill_rate = self.__calcRes(ink_recovery_parameters, p, s)
                refill_time = refill_rate / 60.0
                score += abs((10 / refill_time) * 100)
                num_params += 1

                # ii. Increased Ink Recovery in Squid Form
                ink_recovery_parameters = SplatoonData.get_ability(ability)["In Ink"]
                s = self.__calcS(ink_recovery_parameters)
                refill_rate = self.__calcRes(ink_recovery_parameters, p, s)
                refill_time = refill_rate / 60.0
                score += abs((3 / refill_time) * 100)
                num_params += 1

                if num_params > 1:
                    self.fitness_score += (score / num_params) * (1 + (.1 * (num_params - 1)))
                else:
                    self.fitness_score += score                  
            
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

                s = self.__calcS(ink_saver_main_parameters)
                reduction = self.__calcRes(ink_saver_main_parameters, p, s)
                costPerShot = self.weapon["inkPerShot"] * reduction
                score += abs((costPerShot / self.weapon["inkPerShot"] - 1) * 100)
                num_params += 1

                if num_params > 1:
                    self.fitness_score += (score / num_params) * (1 + (.1 * (num_params - 1)))
                else:
                    self.fitness_score += score

            """
            6. Ink Saver Sub provides a single benefit the optimizer evaluates.
            """
            if ability == "Ink Saver Sub":
                ink_saver_sub_parameters = SplatoonData.get_ability(ability)[self.sub["inkSaver"]]                
                s = self.__calcS(ink_saver_sub_parameters)
                reduction = self.__calcRes(ink_saver_sub_parameters, p, s)
                costPerSub = self.sub["cost"] * reduction
                score += abs((costPerSub / self.sub["cost"] - 1) * 100)
                num_params += 1

                if num_params > 1:
                    self.fitness_score += (score / num_params) * (1 + (.1 * (num_params - 1)))
                else:
                    self.fitness_score += score

            """
            7. Special Charge Up provides a single benefit the optimizer evaluates.
            """
            if ability == "Special Charge Up":
                special_charge_speed_parameters = SplatoonData.get_ability(ability)["default"]
                s = self.__calcS(special_charge_speed_parameters)
                special_charge_speed = self.__calcRes(special_charge_speed_parameters, p, s)
                score += abs((special_charge_speed / special_charge_speed_parameters[2] - 1) * 100)
                num_params += 1

                if num_params > 1:
                    self.fitness_score += (score / num_params) * (1 + (.1 * (num_params - 1)))
                else:
                    self.fitness_score += score

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

                s = self.__calcS(special_saver_parameters)
                modifier = self.__calcRes(special_saver_parameters, p, s)
                special_saved = 100.0 * modifier

                # NOTE: Non base stat abilities aren't implement currently
                if "Respawn Punisher" in self.primaries:
                    special_saved *= 0.775

                score += abs((special_saved / 100 - 1) * 100)
                num_params += 1

                # ii. Special Saved when killed while using it
                if self.special["name"] == "Splashdown":
                    special_saver_parameters = SplatoonData.get_ability(ability)["Splashdown"]
                else:
                    special_saver_parameters = SplatoonData.get_ability(ability)["default"]
                
                s = self.__calcS(special_saver_parameters)               
                modifier = self.__calcRes(special_saver_parameters, p, s)
                special_saved = 100.0 * modifier
                
                if special_saved > 100:
                    special_saved = 100.0

                # NOTE: Non base stat abilities aren't implement currently
                if "Respawn Punisher" in self.primaries:
                    special_saved *= 0.775

                score += abs((special_saved / 100 - 1) * 100)
                num_params += 1

                if num_params > 1:
                    self.fitness_score += (score / num_params) * (1 + (.1 * (num_params - 1)))
                else:
                    self.fitness_score += score

            """
            9. Special Power Up provides a single benefit the optimizer evaluates.
               However, the benefit varies per Special.
            """
            if ability == "Special Power Up":
                if self.weapon["special"] == "Curling-Bomb Launcher":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Curling Bomb Launcher"]

                if "Launcher" in self.weapon["special"]:
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Other Bomb Launcher"]

                if self.weapon["special"] == "Ink Armor":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Ink Armor Duration"]

                if self.weapon["special"] == "Inkjet":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Inkjet Duration"]
                 
                if self.weapon["special"] == "Ink Storm":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Ink Storm Duration"]

                if self.weapon["special"] == "Sting Ray":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Sting Ray Duration"]

                if self.weapon["special"] == "Baller":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Baller HP"]

                if self.weapon["special"] == "Tenta Missiles":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Tenta Missiles Target Circle Radius"]

                if self.weapon["special"] == "Splashdown":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Splash Down Burst Radius Close"]

                if self.weapon["special"] == "Bubble Blower":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Bubble Blower Bubble Radius Multiplier"]
                    s = self.__calcS(special_power_up_parameters)
                    modifier = self.__calcRes(special_power_up_parameters, p, s)
                    min_bubble_radius = special_power_up_parameters[2] * SplatoonData.get_special("Bubble Blower")["radius"]["Max"]
                    bubble_radius = modifier * SplatoonData.get_special("Bubble Blower")["radius"]["Max"]
                    score += abs((bubble_radius / min_bubble_radius - 1) * 100)
                    num_params += 1

                if self.weapon["special"] == "Booyah Bomb":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Booyah Ball Auto Charge Increase"]
                    s = self.__calcS(special_power_up_parameters)
                    modifier = self.__calcRes(special_power_up_parameters, p, s)
                    charge_time = SplatoonData.get_special("Booyah Bomb")["duration"] - (SplatoonData.get_special("Booyah Bomb")["duration"] * modifier)
                    max_charge_time = SplatoonData.get_special("Booyah Bomb")["duration"] - (SplatoonData.get_special("Booyah Bomb")["duration"] * special_power_up_parameters[2])
                    score += abs((charge_time / max_charge_time - 1) * 100)
                    num_params += 1

                if self.weapon["special"] == "Ultra Stamp":
                    special_power_up_parameters = SplatoonData.get_ability(ability)["Ultra Stamp Duration"]

                if score == 0:
                    s = self.__calcS(special_power_up_parameters)
                    result = self.__calcRes(special_power_up_parameters, p, s)
                    score += abs((result / special_power_up_parameters[2] - 1) * 100)
                    num_params += 1

                if num_params > 1:
                    self.fitness_score += (score / num_params) * (1 + (.1 * (num_params - 1)))
                else:
                    self.fitness_score += score

            """
            10. Sub Power Up provides a single benefit the optimizer evaluates.
                However, the benefit varies per Sub Weapon.
            """
            if ability == "Sub Power Up":
                if self.sub["name"] in ["Autobomb", "Burst Bomb", "Curling Bomb", "Splat Bomb", "Suction Bomb"]:
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["General Bomb Distance Up"]

                if self.sub["name"] == "Fizzy Bomb":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Fizzy Bomb Distance Up"]

                if self.sub["name"] == "Point Sensor":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Point Sensor Distance Up"]

                if self.sub["name"] == "Toxic Mist":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Ink Mine Mark Time Duration"]
                    s = self.__calcS(sub_power_up_parameters)

                if self.sub["name"] == "Ink Mine":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Ink Mine Mark Radius"]

                if self.sub["name"] == "Splash Wall":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Splash Wall Max HP"]

                if self.sub["name"] == "Sprinkler":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Sprinkler First Phase Duration"]

                if self.sub["name"] == "Squid Beakon":
                    jump_parameters = SplatoonData.get_ability("Quick Super Jump")["Jump"]
                    s = self.__calcS(jump_parameters)
                    jump_duration = self.__calcRes(jump_parameters, p, s)

                    prepare_parameters = SplatoonData.get_ability("Quick Super Jump")["Prepare"]
                    s = self.__calcS(prepare_parameters)
                    prepare_duration = self.__calcRes(prepare_parameters, p, s)

                    total_duration = jump_duration + prepare_duration
                    max_duration = jump_parameters[2] + prepare_parameters[2]
                    score += abs((total_duration / max_duration - 1) * 100)
                    num_params += 1

                if self.sub["name"] == "Torpedo":
                    sub_power_up_parameters = SplatoonData.get_ability(ability)["Torpedo Distance Up"]
                    
                if score == 0:
                    s = self.__calcS(sub_power_up_parameters)
                    result = self.__calcRes(sub_power_up_parameters, p, s)
                    score += abs((result / sub_power_up_parameters[2] - 1) * 100)
                    num_params += 1
                
                if num_params > 1:
                    self.fitness_score += (score / num_params) * (1 + (.1 * (num_params - 1)))
                else:
                    self.fitness_score += score

            """
            11. Sub Power Up provides a single benefit the optimizer evaluates.
                Note that reduced Super Jump time in kid form is the same as
                reduced Super Jump time in squid form except a constant value.
            """
            if ability == "Quick Super Jump":
                jump_parameters = SplatoonData.get_ability(ability)["Jump"]
                s = self.__calcS(jump_parameters)
                jump_duration = self.__calcRes(jump_parameters, p, s)       

                prepare_parameters = SplatoonData.get_ability(ability)["Prepare"]
                s = self.__calcS(prepare_parameters)
                prepare_duration = self.__calcRes(prepare_parameters, p, s)

                total_duration = jump_duration + prepare_duration
                max_duration = jump_parameters[2] + prepare_parameters[2]
                score += abs((total_duration / max_duration - 1) * 100)
                num_params += 1

                if num_params > 1:
                    self.fitness_score += (score / num_params) * (1 + (.1 * (num_params - 1)))
                else:
                    self.fitness_score += score

            """
            12. Quick Respawn provides a single benefit the optimizer evaluates.
            """
            if ability == "Quick Respawn":
                death_frames_parameters = SplatoonData.get_ability(ability)["Die Frames"]
                s = self.__calcS(death_frames_parameters)
                death_duration = self.__calcRes(death_frames_parameters, p, s)

                deathcam_parameters = SplatoonData.get_ability(ability)["Deathcam Frames"]
                s = self.__calcS(deathcam_parameters)
                deathcam_duration = self.__calcRes(deathcam_parameters, p, s)

                total_duration = ((death_duration + deathcam_duration) / 60) + 2.5
                max_duration = ((death_frames_parameters[2] + deathcam_parameters[2]) / 60) + 2.5
                score += abs((total_duration / max_duration - 1) * 100)
                num_params += 1

                if num_params > 1:
                    self.fitness_score += (score / num_params) * (1 + (.1 * (num_params - 1)))
                else:
                    self.fitness_score += score

            """
            13. Bomb Defense provides the following benefits this optimizer evaluates:
                i.   Reduced Tracking Time by Ink Mine and Point Sensor
                ii.  Reduced damage dealt by Specials
                iii. Reduced damage dealt by Sub Weapons
            """         
            if ability == "Bomb Defense":
                pass # TODO

            """
            14. Main Power Up provides a varying amount of benefit the optimizer evaluates.
                Depending on the Weapon, MPU may grant one or more benefits.
            """
            if ability == "Main Power Up":
                pass # TODO  