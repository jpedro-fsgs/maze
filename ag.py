from pyamaze import maze, agent, COLOR
import random
import tk_state_patch

# ====== CONFIGURAÇÕES ======
start = (50, 50)
goal = (1, 1)
m = maze(*start)
m.CreateMaze(loopPercent=50)

# ====== FUNÇÕES AUXILIARES ======


def coord_in_direction(position: tuple[int, int], direction: str):
    r, c = position
    deltas = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
    if direction not in deltas:
        raise ValueError(f"Direção inválida: {direction}")
    dr, dc = deltas[direction]
    return (r + dr, c + dc)

def is_dead_end(position: tuple[int, int], direction: str):
    count = 0
    for v in m.maze_map[position].values():
        if not v:
            count += 1
    return count == 3


# max_distance_reached = [0]  # variável global para registrar a maior distância


def fitness(path: str, start_pos: tuple[int, int], goal=(1, 1)):
    pos = start_pos
    steps = 0
    penalties = 0
    reached_goal = False

    for move in path:
        if pos == goal:
            reached_goal = True
            break

        # if is_dead_end(pos, move):
        #     penalties += 10

        if m.maze_map[pos][move]:
            pos = coord_in_direction(pos, move)
            steps += 1
        else:
            penalties += 1

    # Distância Manhattan (mais coerente para grids)
    distance = abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    if reached_goal:
        base = 1000
        path_efficiency = 300 * (1 / (1 + 0.05 * steps))
        collision_penalty = 1 / (1 + penalties * 0.3)
        score = (base + path_efficiency) * collision_penalty
    else:
        proximity_score = 300 / (1 + distance)
        exploration_penalty = (steps * 0.2) + (penalties * 2)
        score = proximity_score - exploration_penalty

    return max(0.01, round(score, 3))


def generate_agent():
    colors = [COLOR.red, COLOR.blue, COLOR.green, COLOR.yellow, COLOR.light, COLOR.cyan]
    return agent(m, filled=True, footprints=True, color=random.choice(colors))


def generate_path(max_size: int):
    """Gera um caminho inicial válido e variado, evitando loops locais e reversões imediatas."""
    path = []
    pos = start
    visited = {pos}
    last_move = None

    for _ in range(random.randint(max_size // 2, max_size)):  # diversidade de tamanhos
        possible_moves = [d for d, open_ in m.maze_map[pos].items() if open_]

        if not possible_moves:
            break

        # Evita o movimento reverso imediato (ex: N seguido de S)
        if last_move:
            reverse = {"N": "S", "S": "N", "E": "W", "W": "E"}[last_move]
            if reverse in possible_moves and len(possible_moves) > 1:
                possible_moves.remove(reverse)

        # Escolha ponderada (50% chance de explorar, 50% chance de seguir reto)
        if last_move in possible_moves and random.random() < 0.5:
            move = last_move
        else:
            move = random.choice(possible_moves)

        path.append(move)
        pos = coord_in_direction(pos, move)
        visited.add(pos)
        last_move = move

    return "".join(path)


def generate_child_path(paths):
    """Cria um filho a partir de dois pais, com pesos baseados no fitness e mutação adaptativa."""

    weights = [fitness(p, start) for p in paths]

    # escolha ponderada dos pais
    # father, mother = random.choices(paths, weights=weights, k=2)

    father, mother = random.choices(paths, k=2)

    # caso os pais sejam muito curtos, regenera
    if len(father) < 2 or len(mother) < 2:
        return generate_path(max(len(father), len(mother)))
    
    if random.random() < 0.1:
        father = generate_path(len(father))

    # crossover de dois pontos
    cut1 = random.randint(0, min(len(father), len(mother)) // 2)
    cut2 = random.randint(cut1, min(len(father), len(mother)))
    child = father[:cut1] + mother[cut1:cut2] + father[cut2:]

    # mutação (25% de chance)
    while random.random() < 0.5:
        child_list = list(child)
        mutation_type = random.choice(["replace", "insert", "delete"])

        if mutation_type == "replace" and child_list:
            i = random.randrange(len(child_list))
            child_list[i] = random.choice(["N", "S", "E", "W"])

        elif mutation_type == "insert":
            i = random.randrange(len(child_list) + 1)
            child_list.insert(i, random.choice(["N", "S", "E", "W"]))

        elif mutation_type == "delete" and len(child_list) > 1:
            i = random.randrange(len(child_list))
            del child_list[i]

        child = "".join(child_list)

    # evita string vazia
    if not child:
        child = generate_path((m.rows + m.cols) // 2)

    return child


def valid_path(path, start):
    pos = start
    valid_moves = ""
    for move in path:
        if m.maze_map[pos][move]:
            pos = coord_in_direction(pos, move)
            valid_moves += move
    return valid_moves


def trace_paths(paths, delay=10):
    agents = {generate_agent(): valid_path(path, start) for path in paths}
    m.tracePath(agents, delay=delay, kill=True)


# ====== LOOP PRINCIPAL ======

record = []


def generation(times: int, population: int, selection: int):
    max_path_size = (m.rows + m.cols) * 2
    paths = [generate_path(max_path_size) for _ in range(population)]

    for g in range(times):
        paths.sort(key=lambda p: fitness(p, start), reverse=True)
        record.append(
            f"Geração {g+1:03d} | Melhor fitness: {fitness(paths[0], start):.4f}"
        )

        # exibe os 5 melhores
        trace_paths(paths[:5])

        survivors = paths[:selection]
        children = [
            generate_child_path(survivors) for _ in range(population - selection)
        ]
        paths = survivors + children


# ====== EXECUÇÃO ======
generation(times=50, population=100, selection=15)
m.run()
print(*record, sep="\n")
