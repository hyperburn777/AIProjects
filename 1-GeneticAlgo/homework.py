import math, random, time

def read_input(filename="input.txt"):
    f = open(filename, "r")
    citiesNum = int(f.readline())
    
    cities = []
    for _ in range(citiesNum):
        cities.append(list(map(int, f.readline().strip().split())))

    f.close()
    return cities, citiesNum

def write_output(cities, path, dist, filename="output.txt"):
    f = open(filename, "w")
    f.write(str(dist) + "\n")
    for ind in path:
        f.write(" ".join(map(str, cities[ind])) + "\n")
    f.close()
    return

def euclidean_dist(city1, city2):
    return math.sqrt(sum((i - j) ** 2 for i, j in zip(city1, city2)))

def path_dist(path, cities):
    pathCalc = path[:]
    pathCalc.append(path[0])
    distSum = 0
    for i in range(len(pathCalc) - 1):
        distSum += euclidean_dist(cities[pathCalc[i]], cities[pathCalc[i+1]])
    distSum = round(distSum, 3)
    return distSum

def crossover(parent1, parent2, startInd, endInd):
    child = [None] * len(parent1)
    child[startInd:endInd+1] = parent1[startInd:endInd+1]
    ptr = (endInd + 1) % len(parent2)
    for city in parent2:
        if city not in child:
            child[ptr] = city
            ptr = (ptr + 1) % len(parent2)
    return child

def two_opt(path, cities, time_limit=1):
    start_time = time.time()
    improved = True
    while improved:
        improved = False
        for i in range(1, len(path) - 2):
            for j in range(i + 1, len(path)):
                if j - i == 1:
                    continue
                new_path = path[:]
                new_path[i:j] = path[j - 1:i - 1:-1]
                if path_dist(new_path, cities) < path_dist(path, cities):
                    path = new_path
                    improved = True
                if time.time() - start_time > time_limit:
                    return path
    return path

def gen_path(cities, citiesNum):
    start = random.randint(0, citiesNum - 1)
    path = [start]
    unvisited = set(range(citiesNum)) - {start}
    while unvisited:
        currentCity = path[-1]
        nextCity = min(unvisited, key=lambda city: euclidean_dist(cities[currentCity], cities[city]))
        path.append(nextCity)
        unvisited.remove(nextCity)
    return path

def gen_path_random(citiesNum):
    path = list(range(citiesNum))
    random.shuffle(path)
    return path

def gen_init_population(cities, citiesNum, size=50):
    population = []
    for _ in range(size):
        if random.random() < 0.5:
            population.append(gen_path(cities, citiesNum))
        else:
            population.append(gen_path_random(citiesNum))
    return population

def fitness(population, cities):
    fitnessScores = [path_dist(path, cities) for path in population]
    fitnessValues = [1 / (d ** 2) if d > 0 else 1e9 for d in fitnessScores]
    totalFitness = sum(fitnessValues)
    probabilities = [f / totalFitness for f in fitnessValues]
    return fitnessScores, probabilities

def select_parents(fitnessScores, probabilities, size=3):
    parents = []
    for _ in range(2):
        tournament = random.sample(range(len(fitnessScores)), size)
        winner = min(tournament, key=lambda i: fitnessScores[i])
        parents.append(winner)
    return parents

def gen_new_population(population, cities, children=100):
    fitnessScores, probabilities = fitness(population, cities)
    sortedInd = sorted(range(len(fitnessScores)), key=lambda i: fitnessScores[i])
    newPop = [population[i] for i in sortedInd[:max(1, len(population) // 20)]]
    for i in range(len(newPop)):
        newPop[i] = two_opt(newPop[i], cities, time_limit=10)
    while len(newPop) < children:
        parents = select_parents(fitnessScores, probabilities)
        start, end = sorted(random.sample(range(len(population[0])), 2))
        child = crossover(population[parents[0]], population[parents[1]], start, end)
        newPop.append(child)
    return newPop

def select_best(population, cities):
    for i in range(len(population)):
        population[i] = two_opt(population[i], cities, time_limit=10)
    fitnessScores = [path_dist(path, cities) for path in population]
    bestInd = fitnessScores.index(min(fitnessScores))
    solPath = population[bestInd][:]
    solPath.append(population[bestInd][0])
    solPath = two_opt(solPath, cities, time_limit=180)
    return solPath

def main():
    cities, citiesNum = read_input()
    paths = gen_init_population(cities, citiesNum, citiesNum*3)
    for cycle in range(10):
        print(str(cycle + 1))
        paths = gen_new_population(paths, cities, citiesNum/2)
    path = select_best(paths, cities)
    dist = path_dist(path, cities)
    print("Path Distance: " + str(dist))
    write_output(cities, path, dist)
    return

if __name__ == "__main__":
    main()