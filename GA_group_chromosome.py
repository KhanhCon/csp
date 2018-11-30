import random, sys, bisect, time, heapq

from itertools import chain


class Genotype:
    def __init__(self, item, fitness):
        self.item_chromosome = item
        self.fitness = fitness


class GA:
    def __init__(self, data):
        self.stock = sorted(data["stock"])
        self.piece = sorted(data["piece"])
        self.price = data["price"]
        self.piece_map = range(0, len(data["piece"]))
        self.fe_count = 0;  # function evaluation count

    def best_stock(self, item_chromosome):

        """
        :param item_chromosome:
        :return: a list that contains the best fit stocks for groups in the item chromosome
        """

        def piece_sum(piece_map):
            return sum([self.piece[p] for p in piece_map])

        best_stocks = [None] * len(item_chromosome)
        for i in xrange(0, len(best_stocks)):
            l = sum([self.piece[p] for p in item_chromosome[i]])
            point = (bisect.bisect(self.stock, l))
            best_stock = None
            best_price = float('inf')
            for p in xrange(point - 1, len(self.stock)):
                if self.stock[p] >= l and best_price > self.price[self.stock[p]]:
                    best_price = self.price[self.stock[p]]
                    best_stock = self.stock[p]
            best_stocks[i] = best_stock
        return best_stocks

    def print_geno(self, item_chromosome):
        best_stocks = self.best_stock(item_chromosome)
        solution = {}
        for s in self.stock:
            solution[s] = []
        for i in xrange(0, len(item_chromosome)):
            pheno_bin = []
            for item in item_chromosome[i]:
                pheno_bin.append(self.piece[item])
            solution[best_stocks[i]].append(pheno_bin)

        piece_test = []
        for key, value in solution.iteritems():
            piece_test.append(list(chain(*value)))
            for val in value:
                if sum(val) > key:
                    print "Exceed"
        piece_test = sorted(chain(*piece_test), reverse=False)
        if piece_test == self.piece:
            print "Check piece: Passed"
        else:
            print "Check piece: Failed"
            print piece_test
        fitness = 0
        for key, value in solution.iteritems():
            fitness += len(value) * self.price[key]
            print "%s: %s" % (key, value)
        print "cost: %s" % fitness

    def calculate_fitness(self, item_chromosome):
        best_stocks = self.best_stock(item_chromosome)
        self.fe_count += 1;
        return sum([self.price[stock] for stock in best_stocks])

    def mutation(self, item_chromosome):
        num_of_bins = random.randint(3, 5)
        mutating_pieces = []
        child = []
        child[:] = item_chromosome[:]
        for i in xrange(0, num_of_bins):
            bin = random.choice(child)
            mutating_pieces += bin
            child.remove(bin)
        mutating_pieces.sort()
        # print mutating_pieces
        child += self.FF(mutating_pieces)
        fitness = self.calculate_fitness(child)
        child_geno = Genotype(child, fitness=fitness)

        return child_geno

    def crossover(self, item_chromosome1, item_chromosome2):

        def crossover_chromosome(chromosome, inserted_chromosome):
            """
            :param chromosome:
            :param inserted_chromosome:
            :return: 
            """
            removed_items = []
            tobe_removed_groups = []

            for group_index in xrange(0, len(chromosome)):
                tobe_reinsert = []
                group = chromosome[group_index]
                delete = False
                for item_index in xrange(0, len(group)):
                    if any(group[item_index] in bin for bin in inserted_chromosome):
                        delete = True
                    else:
                        tobe_reinsert.append(item_index)
                if delete:
                    tobe_removed_groups.append(group_index)
                    for group_index in tobe_reinsert:
                        removed_items.append(group[group_index])


            tobe_removed_groups.sort(reverse=True)
            for item_index in tobe_removed_groups:
                del chromosome[item_index]

            # Insert the part to original chromosome
            if not chromosome:
                chromosome = inserted_chromosome
            else:
                insertpoint1 = random.randint(0, len(chromosome) - 1)
                chromosome[insertpoint1:insertpoint1] = inserted_chromosome
            # Insert missing items with FF algorithm
            if removed_items:
                removed_items.sort()
                chromosome += self.FF(removed_items)
            return chromosome

        child_chromosome1 = []
        child_chromosome2 = []
        child_chromosome1[:] = item_chromosome1[:]
        child_chromosome2[:] = item_chromosome2[:]

        crosspoint1 = sorted(random.sample(xrange(0, len(item_chromosome1) - 1), 2))
        crosspoint2 = sorted(random.sample(xrange(0, len(item_chromosome2) - 1), 2))

        child_chromosome2 = crossover_chromosome(child_chromosome2,
                                                 inserted_chromosome=item_chromosome1[crosspoint1[0]:crosspoint1[1]])
        child_chromosome1 = crossover_chromosome(child_chromosome1,
                                                 inserted_chromosome=item_chromosome2[crosspoint2[0]:crosspoint2[1]])

        fitness1 = self.calculate_fitness(child_chromosome1)
        geno1 = Genotype(child_chromosome1, fitness=fitness1)

        fitness2 = self.calculate_fitness(child_chromosome2)
        geno2 = Genotype(child_chromosome2, fitness=fitness2)

        return geno1, geno2

    # Recursive First Fit algorithm
    def FF(self, piece_mapping):
        """
        :param piece_mapping: a list that contains the index numbers of our PIECE
        :return: an item chromosome
        """

        def piece_sum(piece_map):
            total = 0
            for p in piece_map:
                total += self.piece[p]
            return total

        item_chromosome = []
        # stock_chromosome = []
        copy_piece_map = []
        copy_piece_map[:] = piece_mapping[:]
        while len(copy_piece_map) > 0:
            _yield = float('-inf')
            best_solution = None

            for stock_size in self.stock:
                solution_pieces = []
                for piece_index in reversed(copy_piece_map):
                    item = self.piece[piece_index]
                    length = sum([self.piece[piece] for piece in solution_pieces])
                    if stock_size - length >= item:
                        solution_pieces.append(piece_index)
                current_yield = (float(sum([self.piece[piece] for piece in solution_pieces]))) / float(
                    self.price[stock_size])

                if current_yield > _yield:
                    _yield = current_yield
                    best_solution = solution_pieces

            item_chromosome.append(best_solution)

            for sol in best_solution:
                copy_piece_map.remove(sol)

        return item_chromosome

    # Generate a random genotype
    def random_solution(self):

        copy_piece_mapping = []
        copy_piece_mapping[:] = self.piece_map[:]
        random.shuffle(copy_piece_mapping)
        item_chromosome = self.FF(copy_piece_mapping)
        fitness = self.calculate_fitness(item_chromosome)
        geno = Genotype(item_chromosome, fitness=fitness)
        return geno

    def random_population(self, population_size):
        """
        :param population_size: size of our population
        :return: Return initial population with the size 'population_size'
        """

        population = []
        for i in xrange(0, population_size):
            population.append(self.random_solution())
        return population

    def tournament_selection(self, geno_population):
        """
        :param geno_population: This function takes a population and perform a tourament selection on them
        :return: 2 best solution that will be used to perform crossover
        """

        max_pop = 30  # maximum size of tournament population
        if len(geno_population) < 30:
            max_pop = len(geno_population)
        min_pop = max_pop / 2  # minimum size of tournament population
        tournament_population_size = random.randint(min_pop, max_pop)
        tournament_population = random.sample(geno_population, tournament_population_size)  # pick random solutions

        min1, min2 = heapq.nsmallest(2, tournament_population,
                                     key=lambda x: x.fitness)  # Get 2 solution with lowest cost
        return min1, min2

    def get_best(self, population, best_geno, best_fitness):
        currbest = min(population, key=lambda x: x.fitness)
        if (currbest.fitness < best_fitness):
            best_geno = currbest
            best_fitness = currbest.fitness
        return best_geno, best_fitness

    def run(self, function_evaluation, population_size=50, mutation_rate=0.00):
        print "running EA_stock_cutting..."
        mutation_rate = mutation_rate
        population = self.random_population(population_size)

        best_fitness = 100000
        best_geno = None
        iter = 0
        start_time = time.time()

        while self.fe_count < function_evaluation:

            newGen = []

            while len(newGen) < population_size:
                prob = random.uniform(0, 1)
                if self.fe_count >= function_evaluation:
                    best_geno, best_fitness = self.get_best(population + newGen, best_geno, best_fitness)
                    return best_geno, best_fitness

                if prob < mutation_rate:
                    parent = random.choice(population)
                    child = self.mutation(parent.item_chromosome)
                    newGen.append(child)

                else:
                    parent1, parent2 = self.tournament_selection(population)
                    child1, child2 = self.crossover(parent1.item_chromosome, parent2.item_chromosome)
                    newGen.append(child1)
                    if child1.item_chromosome != child2.item_chromosome:
                        newGen.append(child2)

            sys.stdout.write('')
            sys.stdout.write("\r iteration: %s || seconds: %s || mutation rate: %s" % (str(iter), time.time() - start_time, str(mutation_rate)))

            if iter % 2 == 0:
                best_geno, best_fitness = self.get_best(population, best_geno, best_fitness)
            population[:] = newGen[:]
            iter += 1

        return self.get_best(population, best_geno, best_fitness)


if __name__ == '__main__':
    PRICE1 = {10: 100, 13: 130, 15: 150}
    STOCK1 = (10, 13, 15)
    PIECE1 = [3, 3, 3, 3, 3, 4, 4, 5, 6, 6, 7, 7, 7, 7, 8, 8, 9, 10, 10, 10]

    data1 = {
        "price": PRICE1,
        "stock": STOCK1,
        "piece": PIECE1,
    }

    PRICE2 = {4300: 86, 4250: 85, 4150: 83, 3950: 79, 3800: 68, 3700: 66, 3550: 64, 3500: 63}
    STOCK2 = (3500, 3550, 3700, 3800, 3950, 4150, 4250, 4300)
    PIECE2 = [1050, 1050, 1050, 1100, 1100, 1100, 1100, 1100, 1100, 1100, 1100, 1150, 1150, 1150, 1150, 1200, 1200,
              1200,
              1200, 1200, 1200, 1200, 1200, 1200, 1200, 1250, 1250, 1250, 1250, 1250, 1250, 1300, 1300, 1300, 1350,
              1350,
              1350, 1350, 1350, 1350, 1350, 1350, 1350, 1650, 1650, 1700, 1700, 1700, 1700, 1700, 1850, 1850, 1850,
              1850,
              1850, 1850, 1850, 1850, 1850, 1850, 1850, 1850, 1850, 1900, 1900, 1900, 1900, 1900, 1900, 1900, 1900,
              1900,
              1900, 1900, 1900, 1900, 1900, 1900, 1950, 1950, 1950, 1950, 1950, 1950, 2000, 2000, 2000, 2000, 2000,
              2000,
              2000, 2000, 2000, 2000, 2000, 2050, 2050, 2050, 2050, 2050, 2050, 2100, 2100, 2100, 2100, 2100, 2100,
              2100,
              2100, 2100, 2100, 2100, 2100, 2100, 2100, 2100, 2200, 2200, 2200, 2200, 2250, 2250, 2250, 2250, 2350,
              2350]

    data2 = {
        "price": PRICE2,
        "stock": STOCK2,
        "piece": PIECE2,
    }

    STOCK3 = (100, 105, 110, 115, 120)
    PRICE3 = {120: 12, 115: 11.5, 110: 11, 105: 10.5, 100: 10}
    PIECE3 = [21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22, 22,
              22, 22, 24, 24, 24, 24, 24, 24, 24, 25, 25, 25, 25, 25, 27, 27, 27, 27, 27, 27, 27, 27, 27, 29, 29, 29,
              29, 29, 29, 29, 29, 29, 30, 30, 30, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 32, 32,
              32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33,
              33, 33, 33, 33, 33, 33, 33, 34, 34, 34, 34, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35,
              35, 35, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 38, 39, 39, 39, 39,
              39, 39, 39, 39, 39, 42, 42, 42, 42, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44,
              44, 44, 45, 45, 45, 45, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 47, 47, 47, 47, 47, 47, 47, 47,
              47, 47, 47, 47, 47, 47, 47, 48, 48, 48, 49, 49, 49, 49, 49, 49, 49, 49, 49, 49, 49, 49, 49, 49, 49, 49,
              49, 49, 49, 49, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 50, 51, 51, 51, 51, 51, 51, 51, 51,
              51, 51, 51, 51, 51, 51, 51, 52, 52, 52, 52, 52, 52, 53, 53, 53, 53, 54, 54, 54, 54, 54, 54, 54, 55, 55,
              55, 55, 55, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 57, 57, 57, 57,
              57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 57, 59, 59, 59, 59, 59, 59, 60, 60, 60, 61, 61,
              61, 61, 61, 61, 61, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 65,
              65, 65, 65, 65, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67, 67,
              67, 67, 67, 67, 67]

    data3 = {
        "price": PRICE3,
        "stock": STOCK3,
        "piece": PIECE3,
    }
    start_time = time.time()
    ga = GA(data3)
    geno, fitness = ga.run(function_evaluation=500, population_size=75, mutation_rate=0.05)
    total_time = time.time() - start_time
    ga.print_geno(geno.item_chromosome)

    print("---GA runtime: %s seconds --- \n" % (total_time))
    print ga.fe_count
