import random
import math

TAMANHO_POPULAÇÃO = 100
NUMERO_GERACOES = 4000
TAXA_CROSSOVER = 0.65
TAXA_MUTAÇÃO = 0.008


def generate_number():
    return f'{random.getrandbits(44):044b}'

def crossover(parent1, parent2):
    if random.random() < TAXA_CROSSOVER:
        return parent1, parent2
    
    point = random.randint(1, 44)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    
    return child1, child2

def mutation(cromossome):
    point = random.randint(0, 43)
    mutated = list(cromossome)
    mutated[point] = '1' if cromossome[point] == '0' else '0'
    return ''.join(mutated)

def F6(x, y):
    numerator = (math.sin(math.sqrt(x**2 + y**2)))**2 - 0.5
    denominator = (1.0 + 0.001 * (x**2 + y**2))**2
    return 0.5 - numerator / denominator

def decode(cromossome):
    x = int(cromossome[:22], 2)
    y = int(cromossome[22:], 2)
    x *= 200/(2**22 - 1)
    y *= 200/(2**22 - 1)
    x += - 100
    y += - 100
    return x, y

def encode(x, y):
    x += 100
    y += 100
    x /= 200/(2**22 - 1)
    y /= 200/(2**22 - 1)
    return f'{int(x):022b}{int(y):022b}'

def evaluation(cromossome, function=F6):
    x, y = decode(cromossome)
    return function(x, y)

def start_population():
    population = [generate_number() for _ in range(TAMANHO_POPULAÇÃO)]
    population.sort(key=evaluation, reverse=True)

    for _ in range(NUMERO_GERACOES):

        children = population[:1]

        while len(children) < TAMANHO_POPULAÇÃO:
            parent1, parent2 = random.choices(population, k=2)
            child1, child2 = crossover(parent1, parent2)
            children.extend([child1, child2])

        if len(children) > TAMANHO_POPULAÇÃO:
            population = children[:-1]

        for i in range(len(population)):
            if random.random() < TAXA_MUTAÇÃO:
                population[i] = mutation(population[i])
                
        population.sort(key=evaluation, reverse=True)
        
        yield population[0]

x = None
for i in start_population():
    if i != x:
        print(i, decode(i), evaluation(i))
        x = i