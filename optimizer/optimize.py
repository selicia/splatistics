from loadout import Loadout

loadout = Loadout(".96 Gal", "Sprinkler", "Ink Armor")
loadout.randomize_abilities()
loadout.get_fitness()
print(loadout.primaries)
print(loadout.secondaries)
print(loadout.fitness_score)