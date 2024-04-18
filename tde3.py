import os
import re
import heapq
import time

email_directory = '/home/bruno/Downloads/Amostra Enron - 2016'

class Grafo:
    def __init__(self):
        self.vertices = {}

    def add_edge(self, from_node, to_node, weight=1):
        if from_node not in self.vertices:
            self.vertices[from_node] = {}
        if to_node not in self.vertices:
            self.vertices[to_node] = {}
        if to_node in self.vertices[from_node]:
            self.vertices[from_node][to_node] += weight
        else:
            self.vertices[from_node][to_node] = weight

    def get_adj_list(self):
        return self.vertices

    def nb_vertices(self):
        return len(self.vertices)

    def nb_edges(self):
        return sum(len(adj) for adj in self.vertices.values())

    def top_out(self):
        out_degree = {node: sum(self.vertices[node].values()) for node in self.vertices}
        return sorted(out_degree.items(), key=lambda item: item[1], reverse=True)[:20]

    def top_in(self):
        in_degree = {}
        for node in self.vertices:
            for target in self.vertices[node]:
                if target not in in_degree:
                    in_degree[target] = 0
                in_degree[target] += self.vertices[node][target]
        return sorted(in_degree.items(), key=lambda item: item[1], reverse=True)[:20]
    
    def bfs_path(self, start, goal):
        visited = []
        queue = [start]

        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                visited.append(vertex)
                if vertex == goal:
                    return True, visited[1:]
                
                queue.extend([v for v in self.vertices.get(vertex, {}) if v not in visited])

        return False, visited[1:]  
    
    def dijkstra(self, source_node, destination_node=None, max_distance=None, return_type='full'):
        distances = {vertex: float('infinity') for vertex in self.vertices}
        previous_vertices = {vertex: None for vertex in self.vertices}
        distances[source_node] = 0
        pq = [(0, source_node)]

        while pq:
            current_distance, current_vertex = heapq.heappop(pq)

            if destination_node and current_vertex == destination_node:
                if return_type == 'path':
                    return self.reconstruct_path(previous_vertices, destination_node), distances[destination_node]
                else:
                    return [], float('infinity')

            if max_distance is not None and current_distance > max_distance:
                continue

            for neighbor, weight in self.vertices.get(current_vertex, {}).items():
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_vertices[neighbor] = current_vertex
                    heapq.heappush(pq, (distance, neighbor))

        if return_type == 'full':
            return distances, previous_vertices
        elif return_type == 'distances':
            return distances
        else:
            return [], float('infinity') 

    
    def graph_diameter(self):
        max_distance = 0
        diameter_path = []
        for source in self.vertices:
            result = self.dijkstra(source)

            if isinstance(result, tuple) and len(result) == 2:
                distances, previous_vertices = result
            elif isinstance(result, dict):
                distances = result
                previous_vertices = {vertex: None for vertex in self.vertices}  
            else:
                continue 
            
            for target, distance in distances.items():
                if distance > max_distance and distance != float('infinity'):
                    max_distance = distance
                    if previous_vertices[target] is not None:
                        diameter_path = self.reconstruct_path(previous_vertices, target)

        return max_distance, diameter_path

    def reconstruct_path(self, previous, target):
        path = []
        step = target
        path_with_distances = []
        while step is not None and previous[step] is not None:
            next_step = previous[step]
            distance = self.vertices[next_step].get(step, 0)
            path_with_distances.append((step, distance))
            step = next_step

        path_with_distances.append((step, 0)) 
        path_with_distances.reverse() 
        return path_with_distances


def process_emails(directory, graph):
    from_pattern = re.compile(r'^From: (.+)$', re.M)
    to_pattern = re.compile(r'^To: (.+)$', re.M)

    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as email_file:
                content = email_file.read()
                from_match = from_pattern.search(content)
                to_match = to_pattern.search(content)

                if from_match and to_match and to_match.group(1).strip():
                    sender = from_match.group(1).strip().lower()
                    recipients = to_match.group(1).split(',')
                    recipients = [recipient.strip().lower() for recipient in recipients if recipient.strip()]

                    if sender and any(recipients):
                        for recipient in recipients:
                            graph.add_edge(sender, recipient)

    return graph

grafo = Grafo()
process_emails(email_directory, grafo)

#item 1
with open('/home/bruno/Downloads/qst1_grafo_email.txt', 'w') as file:
    for sender, recipients in grafo.get_adj_list().items():
        for recipient, weight in recipients.items():
            file.write(f'{sender} -> {recipient}: {weight}\n')
    print("item 1 salvo em txt")

#item 2
with open('/home/bruno/Downloads/qst_2_grafo_info.txt', 'w') as file:
    file.write(f'Número de vértices: {grafo.nb_vertices()}\n')
    file.write(f'Número de arestas: {grafo.nb_edges()}\n')
    file.write("\nTop 20 com maior grau de saída:\n")
    for node, degree in grafo.top_out():
        file.write(f'{node}: {degree}\n')
    file.write("\nTop 20 com maior grau de entrada:\n")
    for node, degree in grafo.top_in():
        file.write(f'{node}: {degree}\n')
    print("item 2 salvo em txt")

#item 4
can_reach, visited_nodes = grafo.bfs_path('pilar.ramirez@enron.com', 'theresa.branney@enron.com')
with open('/home/bruno/Downloads/qst_4_bfs.txt', 'w') as file:
    file.write(f"Pode alcançar?: {can_reach}\n")
    file.write("Vertices visitados:\n")
    for node in visited_nodes:
        file.write(f"{node}\n")
    print("item 4 salvo em txt")

#item 5        
with open('/home/bruno/Downloads/qst5_dijkstra.txt', 'w') as file:
    # Teste com uma distancia max
    """distances = grafo.dijkstra('martin.cuilla@enron.com', max_distance=1, return_type='distances')
    file.write("Vertices dentro da distancia 1: " + str(distances) + "\n\n")"""

    # Teste para um caminho especifico entre nos
    path, distance = grafo.dijkstra('martin.cuilla@enron.com', 'william.kasemervisz@enron.com', return_type='path')
    file.write("Caminho ate o no especifico: " + str(path) + "\n")
    file.write("Distancia ate o no especifico: " + str(distance) + "\n")
    print("Item 5 salvo em txt")

    
#item 6
diameter_length, diameter_path = grafo.graph_diameter()
with open('/home/bruno/Downloads/qst6_diametro.txt', 'w') as file:
    file.write(f"Diametro do grafo: {diameter_length}\n")
    file.write("Caminho do diametro:\n")
    for node in diameter_path:
        file.write(f"{node}\n")
    print("Item 6 salvo em txt")


