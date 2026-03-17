import random
import numpy as np

# extra minutes to add to every required separation (increase delays)

class Plane:
    """
    Represent a plane arriving at the airport.

    Parameters:
        time_arrival (int): Scheduled arrival time of the plane.
        num_people_on_plane (int): Number of passengers on the plane.
        time_till_next_plane (int): Minimum separation time before the next plane can land.
        plane_size (str): Category or size of the plane.

    Attributes:
        arrival (int): Scheduled arrival time.
        occupants (int): Number of passengers on the plane.
        plane_type (str): Type or size category of the plane.
        time_landed (int or None): Actual landing time assigned during scheduling.
    """
    def __init__(self, time_arrival, num_people_on_plane, plane_size):
        self.arrival = time_arrival
        self.occupants = num_people_on_plane
        self.plane_type = plane_size
        self.time_landed = None
            
            
class Individual:
    """
    Represent a candidate solution in the genetic algorithm.

    Parameters:
        genome (list): Permutation of Plane objects representing a landing schedule.

    Attributes:
        genome (list): Ordered list of Plane objects defining the landing sequence.
        objectives (tuple or None): Objective values for the individual (e.g., total delay,
                                    number of passengers delayed).
        front (int or None): Pareto front rank assigned during non-dominated sorting.
        crowding (float): Crowding distance used to maintain diversity in NSGA-II.
    """
    
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
    """
    Perform swap mutation on an Individual.

    Parameters:
        individual (Individual): Individual whose genome is a permutation of Plane objects.

    Returns:
        mutant (Individual): New Individual with two randomly selected planes swapped.
    """

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
    """
    Perform partially mapped crossover (PMX) between two parents.

    Parameters:
        parent1 (Individual): First parent Individual whose genome is a permutation of Plane objects.
        parent2 (Individual): Second parent Individual whose genome is a permutation of Plane objects.

    Returns:
        offspring1 (Individual): First offspring Individual produced from crossover.
        offspring2 (Individual): Second offspring Individual produced from crossover.
    """

    p1 = parent1.genome
    p2 = parent2.genome

    parent_size = len(p1)
    
    offspring1 = [None]*parent_size
    offspring2 = [None]*parent_size

    random_cut_index1 = random.randint(0, parent_size-1)
    random_cut_index2 = random.randint(random_cut_index1 + 1, parent_size)
    
    offspring1[random_cut_index1:random_cut_index2] = p1[random_cut_index1:random_cut_index2]
    offspring2[random_cut_index1:random_cut_index2] = p2[random_cut_index1:random_cut_index2]
    

    # Get middle segment from P2 placed for offspring 1
    for i in range(random_cut_index1, random_cut_index2):
        item_placed = False
        item = p2[i]

        if item not in offspring1:
            index = i
            
            while not item_placed:
                mapped_item = p1[index]
                index = p2.index(mapped_item)

                if offspring1[index] is None:
                    offspring1[index] = item
                    item_placed = True
    
    # Place rest of P2 for offspring 1
    for i in range(parent_size):
        if offspring1[i] is None:
            offspring1[i] = p2[i]

    
    # Get middle segment from P1 placed for offspring 2
    for i in range(random_cut_index1, random_cut_index2):
        item_placed = False
        item = p1[i]

        if item not in offspring2:
            index = i
            
            while not item_placed:
                mapped_item = p2[index]
                index = p1.index(mapped_item)

                if offspring2[index] is None:
                    offspring2[index] = item
                    item_placed = True
    
    # Place rest of P1 for offspring 2
    for i in range(parent_size):
        if offspring2[i] is None:
            offspring2[i] = p1[i]
                
    return Individual(offspring1), Individual(offspring2)


def survivor_selection(offspring, mu, population):
    """
    Perform survivor selection using NSGA-II fast non-dominated sorting and crowding distance.

    Parameters:
        offspring (list): List of newly generated Individuals.
        mu (int): Maximum number of Individuals allowed in the population.
        population (list): Current population of Individuals.

    Returns:
        new_population (list): Next generation population containing mu Individuals.
    """
    combined_population = population + offspring

    for ind in combined_population:
        ind.objectives = compute_multi_objectives(ind)

    sorted_population = compute_pareto_fronts(combined_population)

    new_population = []

    for front in sorted_population:
        sorted_front = compute_crowding_distance(front)
        if (len(new_population)+ len(front)) <= mu:
            new_population += front
        else:
            remaining = mu - len(new_population)
            new_population += sorted_front[:remaining]
            break
    
    return new_population

def parent_selection(population):
    """
    Select a parent using binary tournament selection.

    Parameters:
        population (list): Current population of Individuals.

    Returns:
        selected (Individual): Selected parent Individual based on Pareto rank and crowding distance.
    """

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
    """
    Compute Pareto fronts using fast non-dominated sorting.

    Parameters:
        population (list): List of Individuals whose objective values have been computed.

    Returns:
        front_list (list): List of Pareto fronts, where each front is a list of Individuals.
    """

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
    """
    Determine whether one Individual dominates another.

    Parameters:
        ind1 (Individual): First Individual being compared.
        ind2 (Individual): Second Individual being compared.

    Returns:
        dominates (bool): True if ind1 dominates ind2, False otherwise.
    """

    ind1_objectives = ind1.objectives
    ind2_objectives = ind2.objectives

    no_worse = ind1_objectives[0] <= ind2_objectives[0] and ind1_objectives[1] <= ind2_objectives[1]
    better_in_one = ind1_objectives[0] < ind2_objectives[0] or ind1_objectives[1] < ind2_objectives[1]

    return no_worse and better_in_one

def compute_crowding_distance(front):
    """
    Compute crowding distance for Individuals in the same Pareto front.

    Parameters:
        front (list): List of Individuals belonging to the same Pareto front.

    Returns:
        sorted_front (list): List of Individuals sorted from highest crowding distance
                            (most diverse) to lowest crowding distance.
    """
    
    num_individuals = len(front)

    for i in front:
        i.crowding = 0
    
    if num_individuals == 0:
        return []
    elif num_individuals == 1:
        front[0].crowding = float("inf")
        return front
    elif num_individuals == 2:
        front[0].crowding = float("inf")
        front[1].crowding = float("inf")
        return front
    else:
        for j in range(2):
            sorted_front = sorted(front, key=lambda ind: ind.objectives[j])
            sorted_front[0].crowding = float("inf")
            sorted_front[-1].crowding = float("inf")

            # skip the objective if the denominator will be 0
            if sorted_front[-1].objectives[j] - sorted_front[0].objectives[j] == 0:
                continue
            
            for k in range (1, num_individuals-1):
                sorted_front[k].crowding += (sorted_front[k + 1].objectives[j] - sorted_front[k - 1].objectives[j]) / (sorted_front[-1].objectives[j] - sorted_front[0].objectives[j])
        
        return sorted(front, key=lambda ind: ind.crowding, reverse=True)


def separation_time(prev_size, curr_size):
    """
    Return required separation time (in minutes) between two planes based on their size categories.

    The separation depends primarily on the size of the preceding aircraft (wake turbulence
    and wake vortex strength) and, to a lesser extent, the following aircraft. Adjust the
    table values to match your operational requirements.
    """

    prev = str(prev_size).lower()
    curr = str(curr_size).lower()

    table = {
        ("small", "small"): 2,
        ("small", "medium"): 3,
        ("small", "large"): 4,

        ("medium", "small"): 3,
        ("medium", "medium"): 4,
        ("medium", "large"): 5,

        ("large", "small"): 4,
        ("large", "medium"): 5,
        ("large", "large"): 7,
    }

    base = table.get((prev, curr), 4)

    return base

def compute_multi_objectives(individual):
    """
    Compute the objective values for an Individual.

    Parameters:
        individual (Individual): Individual whose genome represents a landing schedule.

    Returns:
        objectives (tuple): Tuple containing:
            total_delay (int): Total delay across all planes.
            occupants_delayed (int): Total number of passengers affected by delays.
    """

    total_delay = 0
    occupants_delayed = 0
    

    schedule = [Plane(x.arrival, x.occupants, x.plane_type) for x in individual.genome]

    for i in range(len(schedule)):
        if i == 0:
            schedule[i].time_landed = schedule[i].arrival

        else:
            # compute required separation based on previous/current plane sizes
            req_sep = separation_time(schedule[i - 1].plane_type, schedule[i].plane_type)
            if schedule[i].arrival >= schedule[i - 1].time_landed + req_sep:
                schedule[i].time_landed = schedule[i].arrival
            else:
                schedule[i].time_landed = schedule[i - 1].time_landed + req_sep

        # compute delay for this plane (0 if on time)
        this_delay = max(0, schedule[i].time_landed - schedule[i].arrival)
        if this_delay > 0:
            total_delay += this_delay
            occupants_delayed += schedule[i].occupants

    return total_delay, occupants_delayed


def minutes_to_military(minutes):
    """Convert minutes-since-midnight to HH:MM string."""
    minutes = int(minutes)
    hrs = (minutes // 60) % 24
    mins = minutes % 60
    return f"{hrs:02d}:{mins:02d}"

def permutation(pop_size, planes_list):
    """
    Initialize a population of Individuals using random permutations.

    Parameters:
        pop_size (int): Number of Individuals to generate.
        planes_list (list): List of Plane objects to be permuted.

    Returns:
        population (list): List of Individuals with randomly permuted genomes.
    """

    population = []

    for i in range(pop_size):
        genome = list(np.random.permutation(planes_list))
        population.append(Individual(genome))

    return population

def main():
    # Generate a larger set of planes.
    num_planes = 50
    interval = 10  # minutes between scheduled arrivals
    sizes = ["Small", "Medium", "Large"]

    # seed for reproducible occupant numbers
    random.seed(42)

    planes = []
    for i in range(num_planes):
        arrival = i * interval
        arrival = max(0, i * interval)
        size = sizes[i % len(sizes)]
        occupants = random.randint(40, 220)
        planes.append(Plane(arrival, occupants, size))
    # GA parameters you can tune
    pop_size = 30
    generations = 100000
    crossover_prob = 0.9
    mutation_prob = 0.2

    # initialize population
    population = permutation(pop_size, planes)

    # evaluate initial population
    for ind in population:
        ind.objectives = compute_multi_objectives(ind)

    # evolutionary loop
    for gen in range(1, generations + 1):
        # ensure Pareto front ranks and crowding distances are set before selection
        fronts = compute_pareto_fronts(population)
        for f in fronts:
            # compute_crowding_distance sets .crowding on members
            _ = compute_crowding_distance(f)

        offspring = []

        # create offspring until we have pop_size children
        while len(offspring) < pop_size:
            parent1 = parent_selection(population)
            parent2 = parent_selection(population)

            if random.random() <= crossover_prob:
                child1, child2 = partially_mapped_crossover(parent1, parent2)
            else:
                child1 = Individual(parent1.genome.copy())
                child2 = Individual(parent2.genome.copy())

            # mutation
            if random.random() <= mutation_prob:
                child1 = swap_mutation(child1)
            if random.random() <= mutation_prob:
                child2 = swap_mutation(child2)

            offspring.extend([child1, child2])

        # trim offspring to desired size
        offspring = offspring[:pop_size]

        # survivor selection
        population = survivor_selection(offspring, pop_size, population)

        # print progress every 50 generations
        if gen % 50 == 0 or gen == 1 or gen == generations:
            # evaluate and show best front summary
            for ind in population:
                ind.objectives = compute_multi_objectives(ind)
            fronts = compute_pareto_fronts(population)
            best_front = fronts[0]
            print(f"Generation {gen}: Best front size={len(best_front)}, sample objectives={best_front[0].objectives}")
        if best_front[0].objectives[0] == 0 and best_front[0].objectives[1] == 0:
            print(f"Optimal solution found at generation {gen}.")
            break

    # final evaluation and print full fronts
    for ind in population:
        ind.objectives = compute_multi_objectives(ind)

    sorted_population = compute_pareto_fronts(population)

    for front in sorted_population:
        sorted_front = compute_crowding_distance(front)
        print(f"Front {front[0].front}:")
        for ind in sorted_front:
            print(f"Objectives: {ind.objectives}, Crowding Distance: {ind.crowding}")
        # Print detailed schedule for the best individual in this front
        if len(sorted_front) > 0:
            best = sorted_front[0]
            schedule = [Plane(x.arrival, x.occupants, x.plane_type) for x in best.genome]
            # compute landing times using separation_time
            for i in range(len(schedule)):
                if i == 0:
                    schedule[i].time_landed = schedule[i].arrival
                else:
                    req_sep = separation_time(schedule[i-1].plane_type, schedule[i].plane_type)
                    if schedule[i].arrival >= schedule[i-1].time_landed + req_sep:
                        schedule[i].time_landed = schedule[i].arrival
                    else:
                        schedule[i].time_landed = schedule[i-1].time_landed + req_sep

            print("Schedule (arrival -> landed) and per-plane delay:")
            for p in schedule:
                arrival_s = minutes_to_military(p.arrival)
                landed_s = minutes_to_military(p.time_landed) if p.time_landed is not None else "--:--"
                delay = max(0, p.time_landed - p.arrival) if p.time_landed is not None else 0
                print(f"  {arrival_s} -> {landed_s} | Delay: {delay} min | Type: {p.plane_type}, Occupants: {p.occupants}")

main()