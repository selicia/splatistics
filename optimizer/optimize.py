import copy
from loadout import Loadout
from splatoon_data import SplatoonData
from operator import itemgetter

class Optimizer(object):
    def __init__(self, num_communities=10, community_size=10, generations=10, required_primaries=[], restricted_primaries=[], required_secondaries=[], restricted_secondaries=[]):
        self.communities = []
        self.num_communities = num_communities
        self.community_size = community_size
        self.generations = generations
        SplatoonData.REQUIRED_PRIMARIES = required_primaries
        SplatoonData.REQUIRED_SECONDARIES = required_secondaries
        SplatoonData.RESTRICTED_PRIMARIES = restricted_primaries
        SplatoonData.RESTRICTED_SECONDARIES = restricted_secondaries

    def search(self):
        for i in range(self.generations):
            for j in range(len(self.communities)):
                self.communities[j] = self.crossover(self.communities[j])

    def sort_by_fitness(self, community):
        for i in range(len(community)):
            community[i] = (community[i], community[i].fitness_score)
        community.sort(key=itemgetter(1), reverse=True)
        community = [c[0] for c in community]
        return community

    def create_communities(self):
        for i in range(self.num_communities):
            self.communities.append(self.create_community())

    def create_community(self):
        community = []
        for i in range(self.community_size):
            loadout = Loadout("Kensa Undercover Brella", "Sprinkler", "Ink Armor")
            loadout.randomize_abilities()
            loadout.get_fitness()
            community.append(loadout)
        return community

    def order_primaries(self, primaries):
        if "Respawn Punisher" in primaries:
            primaries.remove("Respawn Punisher")
            primaries = ["Respawn Punisher"] + primaries
        if "Ninja Squid" in primaries:
            primaries.remove("Ninja Squid")
            primaries = ["Ninja Squid"] + primaries
        return primaries

    def crossover(self, community):
        community = self.sort_by_fitness(community)
        alpha_primaries = community[0].primaries = self.order_primaries(community[0].primaries)
        alpha_secondaries = community[0].secondaries

        candidates = community[1:]
        new_community = [community[0]]

        for i in range(len(candidates)):
            candidate_primaries = self.order_primaries(candidates[i].primaries)
            candidate_secondaries = candidates[i].secondaries

            while True:
                alpha_primaries_clone = copy.deepcopy(alpha_primaries)
                for item in SplatoonData.REQUIRED_PRIMARIES:
                    alpha_primaries_clone.remove(item)

                candidate_primaries_clone = copy.deepcopy(candidate_primaries)
                for item in SplatoonData.REQUIRED_PRIMARIES:
                    candidate_primaries_clone.remove(item)

                new_primaries = []
                for i in range(len(alpha_primaries_clone)):
                    if SplatoonData.RANDOM.randint(0, 1):
                        new_primaries.append(alpha_primaries_clone[i])
                    else:
                        new_primaries.append(candidate_primaries_clone[i])

                new_primaries = new_primaries + SplatoonData.REQUIRED_PRIMARIES
                if(SplatoonData.list_in_list(SplatoonData.REQUIRED_PRIMARIES, new_primaries)):
                    break

            while True:
                alpha_secondaries_clone = copy.deepcopy(alpha_secondaries)
                for item in SplatoonData.REQUIRED_SECONDARIES:
                    alpha_secondaries_clone.remove(item)

                candidate_secondaries_clone = copy.deepcopy(candidate_secondaries)
                for item in SplatoonData.REQUIRED_SECONDARIES:
                    candidate_secondaries_clone.remove(item)

                new_secondaries = []
                for i in range(len(alpha_secondaries_clone)):
                    if SplatoonData.RANDOM.randint(0, 1):
                        new_secondaries.append(alpha_secondaries_clone[i])
                    else:
                        new_secondaries.append(candidate_secondaries_clone[i])

                new_secondaries = new_secondaries + SplatoonData.REQUIRED_SECONDARIES
                if(SplatoonData.list_in_list(SplatoonData.REQUIRED_SECONDARIES, new_secondaries)):
                    break

            while True:
                mutated_primaries = self.mutate_primaries(new_primaries)
                if(SplatoonData.list_in_list(SplatoonData.REQUIRED_PRIMARIES, mutated_primaries)):
                    break

            while True:
                mutated_secondaries = self.mutate_secondaries(new_secondaries)
                if(SplatoonData.list_in_list(SplatoonData.REQUIRED_SECONDARIES, mutated_secondaries)):
                    break

            new_primaries = mutated_primaries
            new_secondaries = mutated_secondaries
 
            loadout = Loadout(community[0].weapon["name"], community[0].sub["name"], community[0].special["name"])
            loadout.primaries = new_primaries
            loadout.secondaries = new_secondaries
            loadout.get_fitness()
            new_community.append(loadout)

        return new_community

    def mutate_primaries(self, primaries):
        mutated_primaries = copy.deepcopy(primaries)
        for item in SplatoonData.REQUIRED_PRIMARIES:
            mutated_primaries.remove(item)

        ability_names = SplatoonData.get_ability_names()
        for i in range(len(mutated_primaries)):
            if SplatoonData.RANDOM.randint(1, 12) == 12:
                while True:
                    random_ability = ability_names[SplatoonData.RANDOM.randint(0, len(ability_names) - 1)]
                    if random_ability == "Respawn Punisher" or random_ability == "Ninja Squid":
                        if random_ability not in mutated_primaries:
                            mutated_primaries[i] = random_ability
                            break
                    else:
                        mutated_primaries[i] = random_ability
                        break
        return mutated_primaries + SplatoonData.REQUIRED_PRIMARIES

    def mutate_secondaries(self, secondaries):
        mutate_secondaries = copy.deepcopy(secondaries)
        for item in SplatoonData.REQUIRED_SECONDARIES:
            mutate_secondaries.remove(item)

        ability_names = SplatoonData.get_ability_names()
        for i in range(len(mutate_secondaries)):
            if SplatoonData.RANDOM.randint(1, 12) == 12:
                while True:
                    random_ability = ability_names[SplatoonData.RANDOM.randint(0, len(ability_names) - 1)]
                    if random_ability == "Respawn Punisher" or random_ability == "Ninja Squid":
                        if random_ability not in mutate_secondaries:
                            mutate_secondaries[i] = random_ability
                            break
                    else:
                        mutate_secondaries[i] = random_ability
                        break
        return mutate_secondaries + SplatoonData.REQUIRED_SECONDARIES


if __name__ == "__main__":
    optimizer = Optimizer(restricted_primaries=["Respawn Punisher","Ninja Squid"], required_secondaries=["DUMMY","DUMMY","DUMMY"])
    optimizer.create_communities()
    optimizer.search()

    alphas = []
    for i in range(len(optimizer.communities)):
        optimizer.communities[i] = optimizer.sort_by_fitness(optimizer.communities[i])
        alphas.append((optimizer.communities[i][0], optimizer.communities[i][0].fitness_score))
    alphas.sort(key=itemgetter(1), reverse=True)
    alphas = [a[0] for a in alphas]
    
    # TODO: Print report
    print("Optimizing for Weapon: Kensa Undercover Brella...")
    import json
    
    output = []
    for loadout in alphas:
        data = {"fitness_score":loadout.fitness_score,"primaries":loadout.primaries,"secondaries":loadout.secondaries}
        output.append(data)

    with open(SplatoonData.DIR + "/results.txt", "w", encoding="utf-8") as results:
        results.write(json.dumps(output, indent=1, ensure_ascii=False))
