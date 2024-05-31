import random
import numpy as np
from deap import base, creator, tools, algorithms
import IO

S, t = IO.get_data()

# Define the fitness function
def fitness(individual):
    subset_sum = sum(item for item, selected in zip(S, individual) if selected)
    return abs(t - subset_sum),

# Create the DEAP components
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
# Attribute generator: binary values 0 or 1
toolbox.register("attr_bool", random.randint, 0, 1)
# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=len(S))
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Register the evaluation function
toolbox.register("evaluate", fitness)
# Register the crossover operator
toolbox.register("mate", tools.cxTwoPoint)
# Register a mutation operator
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
# Register the selection operator
toolbox.register("select", tools.selTournament, tournsize=3)

def main():
    random.seed(42)
    # Create an initial population of 300 individuals
    population = toolbox.population(n=64)
    # Define the statistics to collect
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    # Run the genetic algorithm
    population, logbook = algorithms.eaSimple(population, toolbox, cxpb=0.7, mutpb=0.2, ngen=50, stats=stats, verbose=False)
    
    # Get the best individual
    best_individual = tools.selBest(population, 1)[0]
    subset = [item for item, selected in zip(S, best_individual) if selected]
    
    #print("Best individual is: %s\nwith fitness: %s" % (best_individual, best_individual.fitness.values))
    #print("Subset with sum closest to %d: %s (sum: %d)" % (t, subset, sum(subset)))

    if sum(subset) == t:
        print(1)
    else:
        print(0)

if __name__ == "__main__":
    main()
