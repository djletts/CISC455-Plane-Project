
import random
import numpy

"""
Mutation methods

The mutation we chose to implement is Swap mutaiton. this is the best option as it introduces small
changes while keeping a valid solution.
"""


def swap_mutation(individual):
    """Mutate a permutation"""

    mutant = individual.copy()

    random_1 = random.randint(0, len(mutant) - 1)
    random_2 = random.randint(0, len(mutant) - 1)

    mutant[random_1], mutant[random_2] = mutant[random_2], mutant[random_1]

    return mutant


"""
The Recombination method we chose was the partially mapped crossover as it ensures there are no repeat elements. 
We chose this methode over the edge crossover method as adjacency is not as important for this problem
"""


def partially_mapped_crossover(parent1, parent2):
    """Partially mapped crossover to keep the representation valid (No repeat planes)"""

    parent_size = len(parent1)
    
    offspring1 = [None]*parent_size
    offspring2 = [None]*parent_size

    random_cut_index1 = random.randint(0, parent_size-1)
    random_cut_index2 = random.randint(random_cut_index1 + 1, parent_size)
    
    offspring1[random_cut_index1:random_cut_index2] = parent1[random_cut_index1:random_cut_index2]
    offspring2[random_cut_index1:random_cut_index2] = parent2[random_cut_index1:random_cut_index2]
    

    # Get middle segment from P2 placed for offspring 1
    for i in range(random_cut_index1, random_cut_index2):
        item_placed = False
        item = parent2[i]

        if item not in offspring1:
            index = i
            
            while not item_placed:
                mapped_item = parent1[index]
                index = parent2.index(mapped_item)

                if offspring1[index] is None:
                    offspring1[index] = item
                    item_placed = True
    
    # Place rest of P2 for offspring 1
    for i in range(parent_size):
        if offspring1[i] is None:
            offspring1[i] = parent2[i]

    
    # Get middle segment from P1 placed for offspring 2
    for i in range(random_cut_index1, random_cut_index2):
        item_placed = False
        item = parent1[i]

        if item not in offspring2:
            index = i
            
            while not item_placed:
                mapped_item = parent2[index]
                index = parent1.index(mapped_item)

                if offspring2[index] is None:
                    offspring2[index] = item
                    item_placed = True
    
    # Place rest of P1 for offspring 2
    for i in range(parent_size):
        if offspring2[i] is None:
            offspring2[i] = parent1[i]
                
    return offspring1, offspring2


def survivor_selection(offspring, mu, population):
    """
    Do NSGA II fast sorting and NSGA II crowding.

    Parameters:
        offspring (np.array): Generated offspring. A list of lambd lists of dim floats.
        mu (int): Number of individuals in population.
        population (np.array): Initialized population. A list of mu lists of dim floats.
        
    Returns:
        population (np.array): Initialized population. A list of mu lists of dim floats.
        sigma (np.array): Initialized sigmas. A single int which pairs with population via index.
    """

    # student code begins
    combined = population + offspring

    # student code ends
    
    return population