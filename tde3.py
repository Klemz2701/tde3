import os
import re
import heapq

dir_emails = '/home/bruno/Downloads/Amostra Enron - 2016'

class Grafo:
    def __init__(self):
        self.verts = {}

    def add_aresta(self, de, para, peso=1):
        if de not in self.verts:
            self.verts[de] = {}
        if para not in self.verts:
            self.verts[para] = {}
        if para in self.verts[de]:
            self.verts[de][para] += peso
        else:
            self.verts[de][para] = peso

    def lista_adj(self):
        return self.verts

    def num_verts(self):
        return len(self.verts)

    def num_arestas(self):
        return sum(len(adj) for adj in self.verts.values())

    def top_saida(self):
        grau_saida = {node: sum(self.verts[node].values()) for node in self.verts}
        return sorted(grau_saida.items(), key=lambda item: item[1], reverse=True)[:20]

    def top_entrada(self):
        grau_entrada = {}
        for node in self.verts:
            for alvo in self.verts[node]:
                if alvo not in grau_entrada:
                    grau_entrada[alvo] = 0
                grau_entrada[alvo] += self.verts[node][alvo]
        return sorted(grau_entrada.items(), key=lambda item: item[1], reverse=True)[:20]
    
    def caminho_bfs(self, inicio, meta):
        visitados = []
        fila = [inicio]

        while fila:
            vert = fila.pop(0)
            if vert not in visitados:
                visitados.append(vert)
                if vert == meta:
                    return True, visitados[1:]
                
                fila.extend([v for v in self.verts.get(vert, {}) if v not in visitados])

        return False, visitados[1:]
    
    def eh_euleriano(self):
        cont = 0
        verts_impares = []
        for node, arestas in self.verts.items():
            grau = sum(arestas.values())
            if grau % 2 != 0:
                cont += 1
                verts_impares.append(node)

        if cont == 0:
            return True, "O grafo é Euleriano."
        else:
            return False, f"O grafo não é Euleriano devido a vértices de grau ímpar: {verts_impares}"

    def dijkstra(self, origem, destino=None, dist_max=None, tipo_ret='completo'):
        dists = {vert: float('infinity') for vert in self.verts}
        prevs = {vert: None for vert in self.verts}
        dists[origem] = 0
        pq = [(0, origem)]

        while pq:
            dist_atual, vert_atual = heapq.heappop(pq)

            if destino and vert_atual == destino:
                if tipo_ret == 'caminho':
                    return self.reconstroi_caminho(prevs, destino), dists[destino]
                else:
                    return [], float('infinity')

            if dist_max is not None and dist_atual > dist_max:
                continue

            for vizinho, peso in self.verts.get(vert_atual, {}).items():
                dist = dist_atual + peso
                if dist < dists[vizinho]:
                    dists[vizinho] = dist
                    prevs[vizinho] = vert_atual
                    heapq.heappush(pq, (dist, vizinho))

        if tipo_ret == 'completo':
            return dists, prevs
        elif tipo_ret == 'dists':
            return dists
        else:
            return [], float('infinity') 
    
    def diamentro_grafo(self):
        dist_maxima = 0
        caminho_diam = []
        for orig in self.verts:
            res = self.dijkstra(orig)

            if isinstance(res, tuple) and len(res) == 2:
                dists, prevs = res
            elif isinstance(res, dict):
                dists = res
                prevs = {vert: None for vert in self.verts}  
            else:
                continue 
            
            for alvo, dist in dists.items():
                if dist > dist_maxima and dist != float('infinity'):
                    dist_maxima = dist
                    if prevs[alvo] is not None:
                        caminho_diam = self.reconstroi_caminho(prevs, alvo)

        return dist_maxima, caminho_diam

    def reconstroi_caminho(self, anteriores, alvo):
        caminho = []
        passo = alvo
        caminho_com_dist = []
        while passo is not None and anteriores[passo] is not None:
            prox_passo = anteriores[passo]
            dist = self.verts[prox_passo].get(passo, 0)
            caminho_com_dist.append((passo, dist))
            passo = prox_passo

        caminho_com_dist.append((passo, 0)) 
        caminho_com_dist.reverse() 
        return caminho_com_dist

def processa_emails(diretorio, grafo):
    padrao_de = re.compile(r'^From: (.+)$', re.M)
    padrao_para = re.compile(r'^To: (.+)$', re.M)

    for raiz, dirs, arqs in os.walk(diretorio):
        for arq in arqs:
            caminho_arq = os.path.join(raiz, arq)
            with open(caminho_arq, 'r', encoding='utf-8', errors='ignore') as arq_email:
                conteudo = arq_email.read()
                match_de = padrao_de.search(conteudo)
                match_para = padrao_para.search(conteudo)

                if match_de and match_para and match_para.group(1).strip():
                    remetente = match_de.group(1).strip().lower()
                    destinatarios = match_para.group(1).split(',')
                    destinatarios = [dest.strip().lower() for dest in destinatarios if dest.strip()]

                    if remetente and any(destinatarios):
                        for dest in destinatarios:
                            grafo.add_aresta(remetente, dest)

    return grafo

grafo = Grafo()
processa_emails(dir_emails, grafo)

# Exemplos de uso dos métodos do grafo

#item 1
with open('/home/bruno/Downloads/qst1_grafo_email.txt', 'w') as arquivo:
    for remetente, destinatarios in grafo.lista_adj().items():
        for destinatario, peso in destinatarios.items():
            arquivo.write(f'{remetente} -> {destinatario}: {peso}\n')
    print("item 1 salvo em txt")

#item 2
with open('/home/bruno/Downloads/qst_2_grafo_info.txt', 'w') as arquivo:
    arquivo.write(f'Número de vértices: {grafo.num_verts()}\n')
    arquivo.write(f'Número de arestas: {grafo.num_arestas()}\n')
    arquivo.write("\nTop 20 com maior grau de saída:\n")
    for node, grau in grafo.top_saida():
        arquivo.write(f'{node}: {grau}\n')
    arquivo.write("\nTop 20 com maior grau de entrada:\n")
    for node, grau in grafo.top_entrada():
        arquivo.write(f'{node}: {grau}\n')
    print("item 2 salvo em txt")

#item3
euleriano, msg_euleriano = grafo.eh_euleriano()
with open('/home/bruno/Downloads/qst_3_euleriano.txt', 'w') as arquivo:
    arquivo.write("Verificação para saber se o grafo é Euleriano:\n")
    arquivo.write(f"Conforme solicitado, retornando TRUE ou FALSE, o grafo é Euleriano? {euleriano}\n")
    arquivo.write(f"Mensagem: {msg_euleriano}\n")
    print("item 3 salvo em txt")

#item 4
pode_alcancar, nos_visitados = grafo.caminho_bfs('pilar.ramirez@enron.com', 'theresa.branney@enron.com')
with open('/home/bruno/Downloads/qst_4_bfs.txt', 'w') as arquivo:
    arquivo.write(f"Pode alcançar?: {pode_alcancar}\n")
    arquivo.write("Vertices visitados:\n")
    for node in nos_visitados:
        arquivo.write(f"{node}\n")
    print("item 4 salvo em txt")

#item 5        
with open('/home/bruno/Downloads/qst5_dijkstra.txt', 'w') as arquivo:
    # Teste com uma distância máxima
    """dists = grafo.dijkstra('martin.cuilla@enron.com', dist_max=3, tipo_ret='dists')
    arquivo.write("Vertices dentro da distância 1: " + str(dists) + "\n\n")"""

    # Teste para um caminho específico entre nós
    caminho, distancia = grafo.dijkstra('martin.cuilla@enron.com', 'william.kasemervisz@enron.com', tipo_ret='caminho')
    arquivo.write("Caminho até o nó específico: " + str(caminho) + "\n")
    arquivo.write("Distância até o nó específico: " + str(distancia) + "\n")
    print("Item 5 salvo em txt")

#item 6
comprimento_diam, caminho_diam = grafo.diamentro_grafo()
with open('/home/bruno/Downloads/qst6_diametro.txt', 'w') as arquivo:
    arquivo.write(f"Diametro do grafo: {comprimento_diam}\n")
    arquivo.write("Caminho do diametro:\n")
    for node in caminho_diam:
        arquivo.write(f"{node}\n")
    print("Item 6 salvo em txt")
