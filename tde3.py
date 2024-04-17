import os
import re

email_directory = '/home/bruno/Downloads/Amostra Enron - 2016'

class Grafo:
    def __init__(self):
        self.vertices = {}  # Dicionário para armazenar a lista de adjacências

    def add_edge(self, from_node, to_node, weight=1):
        if from_node not in self.vertices:
            self.vertices[from_node] = {}
        if to_node not in self.vertices:
            self.vertices[to_node] = {}
        if to_node in self.vertices[from_node]:
            self.vertices[from_node][to_node] += weight
        else:
            self.vertices[from_node][to_node] = weight

    def get_adjacency_list(self):
        return self.vertices

    def number_of_vertices(self):
        return len(self.vertices)

    def number_of_edges(self):
        return sum(len(adj) for adj in self.vertices.values())

    def top_out_degree(self):
        out_degree = {node: sum(self.vertices[node].values()) for node in self.vertices}
        return sorted(out_degree.items(), key=lambda item: item[1], reverse=True)[:20]

    def top_in_degree(self):
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
                    return True, visited[1:]  # Exclui o vértice inicial da lista de retornados

                # Adiciona ao final da fila todos os adjacentes não visitados
                queue.extend([v for v in self.vertices.get(vertex, {}) if v not in visited])

        return False, visited[1:]  # Exclui o vértice inicial da lista de retornados, se a busca falhar

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
    for sender, recipients in grafo.get_adjacency_list().items():
        for recipient, weight in recipients.items():
            file.write(f'{sender} -> {recipient}: {weight}\n')

#item 2
with open('/home/bruno/Downloads/qst_2_grafo_info.txt', 'w') as info_file:
    info_file.write(f'Número de vértices: {grafo.number_of_vertices()}\n')
    info_file.write(f'Número de arestas: {grafo.number_of_edges()}\n')
    info_file.write("\nTop 20 com maior grau de saída:\n")
    for node, degree in grafo.top_out_degree():
        info_file.write(f'{node}: {degree}\n')
    info_file.write("\nTop 20 com maior grau de entrada:\n")
    for node, degree in grafo.top_in_degree():
        info_file.write(f'{node}: {degree}\n')

#item 4
can_reach, visited_nodes = grafo.bfs_path('martin.cuilla@enron.com', 'phil2dogs@aol.com')
print("Pode alcançar:", can_reach)
print("Vértices visitados:", visited_nodes)
