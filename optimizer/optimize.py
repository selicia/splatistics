from loadout import Loadout
from splatoon_data import SplatoonData
from operator import itemgetter

class Optimizer(object):
    def __init__(self):
        self.communities = []
        self.num_communities = 10
        self.community_size = 10
        self.generations = 10
        self.generation = 0

    def search(self):
        for i in range(self.generations):
            for j in range(len(self.communities)):
                self.communities[j] = self.crossover(self.communities[j])
            self.generation += 1

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
            loadout = Loadout(".96 Gal", "Sprinkler", "Ink Armor")
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

            new_primaries = []
            for i in range(len(alpha_primaries)):
                if SplatoonData.RANDOM.randint(0, 1):
                    new_primaries.append(alpha_primaries[i])
                else:
                    new_primaries.append(candidate_primaries[i])
                        
            new_secondaries = []
            for i in range(len(alpha_secondaries)):
                if SplatoonData.RANDOM.randint(0, 1):
                    new_secondaries.append(alpha_secondaries[i])
                else:
                    new_secondaries.append(candidate_secondaries[i])

            new_primaries = self.mutate(new_primaries)
            new_secondaries = self.mutate(new_secondaries)
 
            loadout = Loadout(community[0].weapon["name"], community[0].sub["name"], community[0].special["name"])
            loadout.primaries = new_primaries
            loadout.secondaries = new_secondaries
            loadout.get_fitness()
            new_community.append(loadout)

        return new_community

    def mutate(self, abilities):
        ability_names = SplatoonData.get_ability_names()
        for i in range(len(abilities)):
            if SplatoonData.RANDOM.randint(1, 12) == 12: # TODO: Tune the mutation rate
                randomizing = True
                while randomizing:
                    random_ability = ability_names[SplatoonData.RANDOM.randint(0, len(ability_names) - 1)]
                    if random_ability == "Respawn Punisher" or random_ability == "Ninja Squid":
                        if random_ability not in abilities:
                            abilities[i] = random_ability
                            randomizing = False
                    else:
                        abilities[i] = random_ability
                        randomizing = False
        return abilities


if __name__ == "__main__":
    optimizer = Optimizer()
    optimizer.create_communities()
    optimizer.search()

    alphas = []
    for i in range(len(optimizer.communities)):
        optimizer.communities[i] = optimizer.sort_by_fitness(optimizer.communities[i])
        alphas.append((optimizer.communities[i][0], optimizer.communities[i][0].fitness_score))
    alphas.sort(key=itemgetter(1), reverse=True)
    alphas = [a[0] for a in alphas]
    
    # TODO: Print report
    print("Optimizing for Weapon: .96 Gal...")
    import json
    for loadout in alphas:
        data = {"fitness_score":loadout.fitness_score,"primaries":loadout.primaries,"secondaries":loadout.secondaries}
        print(json.dumps(data, indent=1, ensure_ascii=False))
