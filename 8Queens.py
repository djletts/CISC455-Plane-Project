"""
CISC455/851 Coding Exercise 1 - EA for 8-Queens
"""

import random
import numpy
import operator

"""
Evaluation Methods
"""


def fitness_8queen(individual):  # maximization
    """Compute fitness of an individual for the 8-queen puzzle"""

    Max = 28 
    violations = 0
    l = len(individual)
    for i in range(0, l):
        for j in range(i + 1, l):
            if abs(individual[i] - individual[j]) == abs(i - j):
                violations += 1

    return Max - violations


"""
Initialization methods for different representations
"""


def permutation(pop_size, genome_length):
    """initialize a population of permutations"""

    population = []

    for i in range(0, pop_size):
        population.append(numpy.random.permutation(genome_length))

    return population


"""
Mutation methods
"""


def permutation_swap(individual):
    """Mutate a permutation"""

    mutant = individual.copy()

    random_1 = random.randint(0, len(mutant) - 1)
    random_2 = random.randint(0, len(mutant) - 1)

    mutant[random_1], mutant[random_2] = mutant[random_2], mutant[random_1]

    return mutant


"""
Recombination methods
"""


def permutation_cut_and_crossfill(parent1, parent2):
    """cut-and-crossfill crossover for permutation representations"""

    offspring1 = []
    offspring2 = []

    random_cut_index = random.randint(1, len(parent1) - 2)

    offspring1_part1 = parent1[0:random_cut_index]
    offspring2_part1 = parent2[0:random_cut_index]
    parent1_part2 = parent1[random_cut_index:]
    parent2_part2 = parent2[random_cut_index:]

    # fill the rest of the offspring with the remaining genes from the other parent
    for gene in numpy.concatenate((offspring2_part1, parent2_part2)):
        if gene not in offspring1_part1:
            offspring1.append(gene)
    for gene in numpy.concatenate((offspring1_part1, parent1_part2)):
        if gene not in offspring2_part1:
            offspring2.append(gene)

    offspring1 = numpy.concatenate((offspring1_part1, offspring1))
    offspring2 = numpy.concatenate((offspring2_part1, offspring2))
    return offspring1, offspring2


"""
Parent selection methods
"""

def tournament(fitness, mating_pool_size, tournament_size):
    """Tournament selection without replacement"""

    selected_to_mate = []

    for i in range(mating_pool_size // 2):
        tournament_contestants = random.sample(range(0, len(fitness)), tournament_size)
        best_fitness = -1
        second_best_fitness = -1
        best_index = -1
        second_best_index = -1
        for j in range(0, tournament_size):
            if fitness[tournament_contestants[j]] > best_fitness:
                second_best_fitness = best_fitness
                second_best_index = best_index
                best_fitness = fitness[tournament_contestants[j]]
                best_index = tournament_contestants[j]

            elif fitness[tournament_contestants[j]] > second_best_fitness:
                second_best_fitness = fitness[tournament_contestants[j]]
                second_best_index = tournament_contestants[j]

        selected_to_mate.append(best_index)
        selected_to_mate.append(second_best_index)

    return selected_to_mate


def random_uniform(population_size, mating_pool_size):
    """Random uniform selection"""

    selected_to_mate = random.sample(range(0, population_size), mating_pool_size)
    return selected_to_mate


"""
Survivor selection methods
"""


def sort_population(population, fitness):  # sort a population based on fitness, from max to min
    pop_fit_pair = list(map(list, zip(population, fitness)))
    pop_fit_pair.sort(key=operator.itemgetter(1), reverse=True)
    sorted_pop = []
    sorted_fit = []
    for entry in pop_fit_pair:
        sorted_pop.append(entry[0])
        sorted_fit.append(entry[1])
    return sorted_pop, sorted_fit


def replacement(current_pop, current_fitness, offspring, offspring_fitness):
    """Offspring to replace the worst individuals in the current generation"""

    population = []
    fitness = []
    sorted_pop, sorted_fit = sort_population(current_pop.copy(), current_fitness.copy())
    k = len(current_pop) - len(offspring)
    for i in range(0, k):
        population.append(sorted_pop[i])
        fitness.append(sorted_fit[i])
    for j in range(0, len(offspring)):
        population.append(offspring[j])
        fitness.append(offspring_fitness[j])

    return population, fitness


def random_uniform(current_pop, current_fitness, offspring, offspring_fitness):
    population = []
    fitness = []
    temp_pop = current_pop.copy() + offspring.copy()
    temp_fit = current_fitness.copy() + offspring_fitness.copy()
    pick_index = random.sample(range(0, len(temp_pop)), len(current_pop))
    for i in range(0, len(pick_index)):
        population.append(temp_pop[pick_index[i]])
        fitness.append(temp_fit[pick_index[i]])
    return population, fitness


def visualize(population, fitness):
    print("=====================\n")
    for i in range(8):
        for j in range(8):
            if population[j] == i:
                print(" ♛ ", end='')
            else:
                print(" □ ", end='')
        print()

    print(f"fitness: {fitness}")
    print("=====================\n")


"""
An evolutionary algorithm for the eight queens puzzle
"""


def main():
    random.seed()
    numpy.random.seed()

    string_length = 8  # may extend to N queens
    # you may set your own parameters below
    popsize = 20
    mating_pool_size = int(popsize * 0.5)  # has to be even
    tournament_size = 4
    xover_rate = 0.9
    mut_rate = 0.2
    gen_limit = 50

    # initialize population
    gen = 0  # initialize the generation counter
    population = permutation(popsize, string_length)
    fitness = []
    for i in range(0, popsize):
        fitness.append(fitness_8queen(population[i]))
    print("generation", gen, ": best fitness", max(fitness),
          "\taverage fitness", sum(fitness) / len(fitness))

    # evolution begins
    while gen < gen_limit:

        # pick parents

        parents_index = tournament(fitness, mating_pool_size, tournament_size)
        #        parents_index = random_uniform(popsize, mating_pool_size)

        # in order to randomly pair up parents
        random.shuffle(parents_index)

        # reproduction
        offspring = []
        offspring_fitness = []
        i = 0  # initialize the counter for parents in the mating pool
        # offspring are generated using selected parents in the mating pool
        while len(offspring) < mating_pool_size:

            # recombination
            if random.random() < xover_rate:
                off1, off2 = permutation_cut_and_crossfill(population[parents_index[i]],
                                                           population[parents_index[i + 1]])
            else:
                off1 = population[parents_index[i]].copy()
                off2 = population[parents_index[i + 1]].copy()

            # mutation
            if random.random() < mut_rate:
                off1 = permutation_swap(off1)
            if random.random() < mut_rate:
                off2 = permutation_swap(off2)

            offspring.append(off1)
            offspring_fitness.append(fitness_8queen(off1))
            offspring.append(off2)
            offspring_fitness.append(fitness_8queen(off2))
            i = i + 2  # update the counter

        # survivor selection

        # population, fitness = replacement(population, fitness, offspring, offspring_fitness)
        population, fitness = random_uniform(population, fitness, offspring, offspring_fitness)

        gen = gen + 1  # update the generation counter
        print("generation", gen, ": best fitness", max(fitness),
              "average fitness", sum(fitness) / len(fitness))

    # evolution ends

    # print the final best solution(s)
    k = 0
    for i in range(0, popsize):
        if fitness[i] == max(fitness):
            print("best solution", k, [int(x) for x in population[i]], fitness[i])
            visualize(population[i], fitness[i])
            k = k + 1


# end of main

if __name__ == "__main__":
    main()
