import random
import numpy


class Plane:
    def __init__(self, time_arrival, num_people_on_plane, time_till_next_plane, plane_size):
        self.arrival = time_arrival
        self.occupants = num_people_on_plane
        self.time_taken = time_till_next_plane
        self.plane_type = plane_size
        self.time_landed = None
            
            
class Individual:
    def __init__(self, genome):
        self.crowding = 0
        self.front = None
        self.objectives = None
        self.genome = genome # List of plane objects

"""
Mutation methods

The mutation we chose to implement is Swap mutaiton. this is the best option as it introduces small
changes while keeping a valid solution.
"""

def swap_mutation(individual):
    """Mutate a permutation"""

    mutant = individual.genome.copy()

    random_1 = random.randint(0, len(mutant) - 1)
    random_2 = random.randint(0, len(mutant) - 1)

    mutant[random_1], mutant[random_2] = mutant[random_2], mutant[random_1]

    return Individual(mutant)


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
                
    return Individual(offspring1), Individual(offspring2)


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
    combined_population = population + offspring

    for ind in combined_population:
        ind.objectives = compute_multi_objectives(ind)

    sorted_population = compute_pareto_fronts(combined_population)

    new_population = []

    for front in sorted_population:
        if (len(new_population)+ len(front)) <= mu:
            new_population += front
        else:
            remaining = mu - len(new_population)
            sorted_front = compute_crowding_distance(front)
            new_population += sorted_front[:remaining]
            break
    
    return new_population

def parent_selection(population):
    """Binary Tournament selection like done in the NSGA II paper"""

    individual_1 = random.choice(population)
    individual_2 = random.choice(population)

    if individual_1.front < individual_2.front:
        selected = individual_1
    elif individual_1.front > individual_2.front:
        selected = individual_2
    else:
        if individual_1.crowding > individual_2.crowding:
            selected = individual_1
        elif individual_1.crowding < individual_2.crowding:
            selected = individual_2
        else:
            selected = random.choice([individual_1, individual_2])

    return selected

def compute_pareto_fronts(population):
    dominations = {i: [] for i in population}
    unassigned = population.copy()
    front_list = []

    for i in population:
        for j in population:
            if i != j:
                if dominates(i,j):
                    dominations[j].append(i)

    while len(unassigned) != 0:
        front = []

        # Find all unassigned individuals not dominated by any other unassigned individual
        for ind in unassigned:
            if len(dominations[ind]) == 0:
                front.append(ind)

        if len(front) == 0:
            break

        # Remove front members from unassigned
        for ind in front:
            unassigned.remove(ind)

        # Remove front members from domination lists of remaining individuals
        for ind in unassigned:
            for f in front:
                if f in dominations[ind]:
                    dominations[ind].remove(f)

        front_list.append(front)
    
    for i in range(len(front_list)):
        for j in front_list[i]:
            j.front = i + 1
    
    return front_list

def dominates(ind1, ind2):
    pass

def compute_crowding_distance(front):
    pass

def compute_multi_objectives(individual):

    total_delay = 0
    occupants_delayed = 0
    

    schedule = [Plane(x.arrival, x.occupants, x.time_taken, x.plane_type) for x in individual.genome]

    for i in range(len(schedule)):
        if i == 0:
            schedule[i].time_landed = schedule[i].arrival

        else:
            if schedule[i].arrival >= schedule[i - 1].time_landed + schedule[i - 1].time_taken:
                schedule[i].time_landed = schedule[i].arrival
            else:
                schedule[i].time_landed = schedule[i - 1].time_landed + schedule[i - 1].time_taken

        # compute delay for this plane (0 if on time)
        this_delay = max(0, schedule[i].time_landed - schedule[i].arrival)
        if this_delay > 0:
            total_delay += this_delay
            occupants_delayed += schedule[i].occupants

    return total_delay, occupants_delayed

def permutation(pop_size, planes_list):
    """initialize a population of permutations"""

    population = []

    for i in range(pop_size):
        genome = list(numpy.random.permutation(planes_list))
        population.append(Individual(genome))

    return population