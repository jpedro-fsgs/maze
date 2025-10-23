from pyamaze import maze, agent, COLOR
import random
import tk_state_patch

# ====== CONFIGURAÇÕES ======
start = (20, 20)
goal = (1, 1)
m = maze(*start)
m.CreateMaze(loopPercent=0)

# ====== FUNÇÕES AUXILIARES ======

def coord_in_direction(position: tuple[int, int], direction: str):
    r, c = position
    deltas = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
    if direction not in deltas:
        raise ValueError(f"Direção inválida: {direction}")
    dr, dc = deltas[direction]
    return (r + dr, c + dc)


def fitness(path: str, start_pos: tuple[int, int], goal=(1, 1)):
    pos = start_pos
    penalties = 0
    steps = 0
    reached_goal = False

    for move in path:
        if pos == goal:
            reached_goal = True
            break
        if m.maze_map[pos][move]:
            pos = coord_in_direction(pos, move)
            steps += 1
        else:
            penalties += 1

    # distância Euclidiana normalizada
    distance = ((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2) ** 0.5

    if reached_goal:
        # recompensa base alta por ter alcançado o objetivo
        reach_bonus = 1000

        # bônus extra se chegou com poucos passos (otimização de eficiência)
        efficiency_bonus = max(0, 500 - steps * 5)

        # penalidade pequena por colisões
        penalty_factor = max(0.1, 1 - 0.1 * penalties)

        # fitness final: recompensa por alcançar + eficiência - penalidades
        base_score = reach_bonus + efficiency_bonus
        final_score = base_score * penalty_factor

    else:
        # se não chegou: recompensa contínua pela proximidade do objetivo
        distance_score = 200 / (1 + distance)
        exploration_penalty = penalties * 2
        final_score = distance_score - exploration_penalty

    # evita valores negativos
    return max(0.01, final_score)



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


def generate_child_path(paths, fitness_fn=fitness):
    """Cria um filho a partir de dois pais, com pesos baseados no fitness e mutação adaptativa."""

    # se o fitness_fn foi fornecido, usa ele para calcular pesos
    if fitness_fn:
        weights = [fitness_fn(p, start) for p in paths]
    else:
        # fallback: pais mais à frente da lista têm mais peso
        weights = [len(paths) - i for i in range(len(paths))]

    # escolha ponderada dos pais
    father, mother = random.choices(paths, weights=weights, k=2)

    # caso os pais sejam muito curtos, regenera
    if len(father) < 2 or len(mother) < 2:
        return generate_path(max(len(father), len(mother)))

    # crossover de dois pontos
    cut1 = random.randint(0, min(len(father), len(mother)) // 2)
    cut2 = random.randint(cut1, min(len(father), len(mother)))
    child = father[:cut1] + mother[cut1:cut2] + father[cut2:]

    # mutação (25% de chance)
    if random.random() < 0.25:
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

def generation(times: int, population: int, selection: int):
    max_path_size = (m.rows + m.cols) * 2
    paths = [generate_path(max_path_size) for _ in range(population)]

    for g in range(times):
        paths.sort(key=lambda p: fitness(p, start), reverse=True)
        print(f"Geração {g+1:03d} | Melhor fitness: {fitness(paths[0], start):.4f}")

        # exibe os 5 melhores
        trace_paths(paths[:5])

        survivors = paths[:selection]
        children = [generate_child_path(survivors) for _ in range(population - selection)]
        paths = survivors + children


# ====== EXECUÇÃO ======
generation(times=30, population=80, selection=40)
m.run()
