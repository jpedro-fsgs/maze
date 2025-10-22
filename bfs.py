from pyamaze import maze, agent, COLOR
import random
import tk_state_patch

m = maze(100, 100)
m.CreateMaze()
a = agent(m, filled=True, footprints=True)


def coord_in_direction(position, direction):
    r, c = position
    d = direction.upper()
    if d == 'N': return (r - 1, c)
    if d == 'S': return (r + 1, c)
    if d == 'E': return (r, c + 1)
    if d == 'W': return (r, c - 1)
    raise ValueError(f"Direção inválida: {direction}")


def bfs(maze_obj: maze, start, goal):
    queue = [start]
    visited: dict[tuple[int, int], tuple[tuple[int, int], str] | None] = {start: None}

    while queue:
        position = queue.pop(0)
        if position == goal:
            break
        for direction, can_move in maze_obj.maze_map[position].items():
            if can_move:
                next_pos = coord_in_direction(position, direction)
                if next_pos not in visited:
                    visited[next_pos] = (position, direction)
                    queue.append(next_pos)

    # Reconstruir caminho
    path = ''
    pos = goal
    while visited[pos] is not None:
        prev, dir_ = visited[pos]
        path = dir_ + path
        pos = prev
    return path







m.tracePath({a: bfs(m, a.position, (1,1))}, delay=5)

m.run()
