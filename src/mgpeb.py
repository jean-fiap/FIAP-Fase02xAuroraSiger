"""
MGPEB - Modulo de Gerenciamento de Pouso e Estabilizacao de Base
Missao Aurora Siger | Fase 2 | FIAP

Prototipo em Python puro (sem bibliotecas externas) que:
  1. cadastra os modulos de pouso em estruturas lineares (lista, fila e pilha);
  2. localiza modulos com busca sequencial e busca binaria;
  3. reorganiza a fila de pouso com ordenacao por selecao e por insercao;
  4. autoriza, adia ou aborta pousos com regras booleanas (portas logicas);
  5. modela a altitude de descida com uma funcao quadratica.

Execucao: python3 src/mgpeb.py
"""

# =============================================================================
# 1. ESTRUTURAS LINEARES
# =============================================================================


class Fila:
    """Fila (FIFO): o primeiro modulo a entrar e o primeiro a ser atendido."""

    def __init__(self):
        self.itens = []

    def enfileirar(self, item):
        self.itens.append(item)          # entra no fim

    def desenfileirar(self):
        if self.vazia():
            return None
        return self.itens.pop(0)         # sai do inicio

    def primeiro(self):
        return None if self.vazia() else self.itens[0]

    def vazia(self):
        return len(self.itens) == 0

    def tamanho(self):
        return len(self.itens)


class Pilha:
    """Pilha (LIFO): o ultimo evento registrado e o primeiro a ser consultado."""

    def __init__(self):
        self.itens = []

    def empilhar(self, item):
        self.itens.append(item)          # entra no topo

    def desempilhar(self):
        if self.vazia():
            return None
        return self.itens.pop()          # sai do topo

    def topo(self):
        return None if self.vazia() else self.itens[-1]

    def vazia(self):
        return len(self.itens) == 0

    def tamanho(self):
        return len(self.itens)


# =============================================================================
# 2. CENARIO: MODULOS DE POUSO DA BASE AURORA
# =============================================================================
# Cada modulo e um dicionario com os atributos usados ao longo da atividade.
# prioridade: 1 (maxima) a 5 (minima) | combustivel em % | massa em toneladas
# criticidade da carga: ALTA, MEDIA ou BAIXA | chegada: minutos ate a orbita

MODULOS = [
    {"id": "M01", "nome": "Habitacao",      "carga": "HABITAT",   "prioridade": 1,
     "combustivel": 62.0, "massa": 18.5, "criticidade": "ALTA",  "chegada": 12,
     "sensores_ok": True,  "zona": "A"},
    {"id": "M02", "nome": "Energia",        "carga": "ENERGIA",   "prioridade": 1,
     "combustivel": 48.0, "massa": 14.2, "criticidade": "ALTA",  "chegada": 8,
     "sensores_ok": True,  "zona": "B"},
    {"id": "M03", "nome": "Laboratorio",    "carga": "CIENCIA",   "prioridade": 3,
     "combustivel": 71.5, "massa": 9.8,  "criticidade": "MEDIA", "chegada": 25,
     "sensores_ok": True,  "zona": "C"},
    {"id": "M04", "nome": "Logistica",      "carga": "LOGISTICA", "prioridade": 4,
     "combustivel": 23.0, "massa": 21.0, "criticidade": "BAIXA", "chegada": 15,
     "sensores_ok": True,  "zona": "A"},
    {"id": "M05", "nome": "Suporte Medico", "carga": "MEDICO",    "prioridade": 2,
     "combustivel": 55.0, "massa": 11.3, "criticidade": "ALTA",  "chegada": 20,
     "sensores_ok": False, "zona": "B"},
    {"id": "M06", "nome": "Comunicacoes",   "carga": "COMUNICACAO", "prioridade": 2,
     "combustivel": 30.0, "massa": 7.6,  "criticidade": "MEDIA", "chegada": 5,
     "sensores_ok": True,  "zona": "C"},
]

# Condicoes do ambiente de pouso (simuladas)
AMBIENTE = {
    "vento_kmh": 35.0,          # limite seguro: 60 km/h
    "tempestade_poeira": False,
    "zonas_livres": {"A": True, "B": True, "C": False},   # zona C ocupada
    "emergencia_base": False,
}

COMBUSTIVEL_MINIMO = 30.0   # % necessario para a manobra de descida
VENTO_MAXIMO = 60.0         # km/h


# =============================================================================
# 3. ALGORITMOS DE BUSCA
# =============================================================================


def busca_sequencial(lista, chave, valor):
    """Percorre a lista do inicio ao fim e devolve todos os modulos em que
    modulo[chave] == valor. Complexidade O(n)."""
    encontrados = []
    for modulo in lista:
        if modulo[chave] == valor:
            encontrados.append(modulo)
    return encontrados


def busca_extremo(lista, chave, menor=True):
    """Busca sequencial do menor (ou maior) valor de um atributo. O(n)."""
    if not lista:
        return None
    escolhido = lista[0]
    for modulo in lista[1:]:
        if menor and modulo[chave] < escolhido[chave]:
            escolhido = modulo
        if not menor and modulo[chave] > escolhido[chave]:
            escolhido = modulo
    return escolhido


def busca_binaria(lista_ordenada, chave, valor):
    """Busca binaria em uma lista JA ORDENADA pela chave. Divide o intervalo
    pela metade a cada passo. Complexidade O(log n)."""
    inicio, fim = 0, len(lista_ordenada) - 1
    while inicio <= fim:
        meio = (inicio + fim) // 2
        atual = lista_ordenada[meio][chave]
        if atual == valor:
            return lista_ordenada[meio]
        if atual < valor:
            inicio = meio + 1
        else:
            fim = meio - 1
    return None


# =============================================================================
# 4. ALGORITMOS DE ORDENACAO
# =============================================================================


def ordenacao_selecao(lista, chave, crescente=True):
    """Ordenacao por selecao: a cada passo escolhe o menor (ou maior) elemento
    restante e o coloca na posicao correta. Complexidade O(n^2).
    Devolve uma nova lista, sem alterar a original."""
    itens = lista[:]
    n = len(itens)
    for i in range(n):
        indice_escolhido = i
        for j in range(i + 1, n):
            if crescente and itens[j][chave] < itens[indice_escolhido][chave]:
                indice_escolhido = j
            if not crescente and itens[j][chave] > itens[indice_escolhido][chave]:
                indice_escolhido = j
        itens[i], itens[indice_escolhido] = itens[indice_escolhido], itens[i]
    return itens


def ordenacao_insercao(lista, chave):
    """Ordenacao por insercao (crescente): insere cada elemento na posicao
    correta da parte ja ordenada. Complexidade O(n^2), mas muito eficiente
    para listas pequenas ou quase ordenadas, como a fila de pouso."""
    itens = lista[:]
    for i in range(1, len(itens)):
        atual = itens[i]
        j = i - 1
        while j >= 0 and itens[j][chave] > atual[chave]:
            itens[j + 1] = itens[j]
            j -= 1
        itens[j + 1] = atual
    return itens


# =============================================================================
# 5. REGRAS DE DECISAO (FUNCOES BOOLEANAS / PORTAS LOGICAS)
# =============================================================================
# Entradas booleanas:
#   C = combustivel suficiente          A = atmosfera segura
#   Z = zona de pouso livre             S = sensores integros
#   E = emergencia na base
#
# AUTORIZAR = C AND A AND Z AND S AND NOT E
# ADIAR     = NOT AUTORIZAR AND C      (tem combustivel para aguardar em orbita)
# ABORTAR   = NOT C                    (nao pode aguardar: desviar para orbita de seguranca)


def avaliar_pouso(modulo, ambiente):
    """Aplica as funcoes booleanas e devolve (decisao, motivos)."""
    C = modulo["combustivel"] >= COMBUSTIVEL_MINIMO
    A = (ambiente["vento_kmh"] <= VENTO_MAXIMO) and (not ambiente["tempestade_poeira"])
    Z = ambiente["zonas_livres"].get(modulo["zona"], False)
    S = modulo["sensores_ok"]
    E = ambiente["emergencia_base"]

    autorizar = C and A and Z and S and (not E)

    motivos = []
    if not C:
        motivos.append("combustivel abaixo do minimo")
    if not A:
        motivos.append("atmosfera insegura")
    if not Z:
        motivos.append("zona " + modulo["zona"] + " ocupada")
    if not S:
        motivos.append("falha nos sensores")
    if E:
        motivos.append("emergencia na base")

    # Estrutura condicional que espelha as funcoes booleanas acima
    if autorizar:
        return "AUTORIZADO", motivos
    elif C:
        return "ADIADO", motivos
    else:
        return "ABORTADO", motivos


# =============================================================================
# 6. MODELAGEM MATEMATICA: ALTITUDE DURANTE A DESCIDA
# =============================================================================
# h(t) = h0 - v0*t - (g/2)*t^2   (funcao quadratica)
#   h0 = altitude inicial (m)   v0 = velocidade vertical inicial (m/s)
#   g  = gravidade de Marte = 3,71 m/s^2

GRAVIDADE_MARTE = 3.71


def altitude(t, h0, v0):
    """Altitude (m) no instante t (s) durante a descida sem frenagem."""
    return h0 - v0 * t - (GRAVIDADE_MARTE / 2.0) * t * t


def instante_retrofoguetes(h0, v0, h_retro, passo=0.1):
    """Primeiro instante em que a altitude cai ate h_retro (varredura simples,
    sem bibliotecas). Devolve (t, altitude)."""
    t = 0.0
    while altitude(t, h0, v0) > h_retro:
        t += passo
    return round(t, 1), round(altitude(t, h0, v0), 1)


# =============================================================================
# 7. SIMULACAO PRINCIPAL
# =============================================================================


def linha(titulo):
    print("\n" + "=" * 70)
    print(" " + titulo)
    print("=" * 70)


def resumo(m):
    return (f"{m['id']} {m['nome']:<15} prio={m['prioridade']} comb={m['combustivel']:>5.1f}% "
            f"massa={m['massa']:>4.1f}t crit={m['criticidade']:<5} chegada=T+{m['chegada']:>2}min")


def main():
    linha("MGPEB | MODULOS CADASTRADOS (lista)")
    for m in MODULOS:
        print("  " + resumo(m))

    # ---- Buscas --------------------------------------------------------------
    linha("BUSCAS")
    menor_comb = busca_extremo(MODULOS, "combustivel", menor=True)
    print(f"  Menor combustivel (busca sequencial): {menor_comb['id']} {menor_comb['nome']} "
          f"({menor_comb['combustivel']}%)")
    maior_prio = busca_extremo(MODULOS, "prioridade", menor=True)   # 1 = maxima
    print(f"  Maior prioridade (busca sequencial):  {maior_prio['id']} {maior_prio['nome']} "
          f"(prioridade {maior_prio['prioridade']})")
    criticos = busca_sequencial(MODULOS, "criticidade", "ALTA")
    print("  Carga de criticidade ALTA:            " + ", ".join(m["id"] for m in criticos))
    por_id = ordenacao_insercao(MODULOS, "id")
    achado = busca_binaria(por_id, "id", "M05")
    print(f"  Busca binaria por id M05:             {achado['nome']}")

    # ---- Ordenacao da fila de pouso -----------------------------------------
    linha("ORDENACAO DA FILA DE POUSO")
    por_chegada = ordenacao_insercao(MODULOS, "chegada")
    print("  Por ordem de chegada (insercao):  " + " -> ".join(m["id"] for m in por_chegada))
    por_prioridade = ordenacao_selecao(MODULOS, "prioridade")
    print("  Por prioridade (selecao):         " + " -> ".join(m["id"] for m in por_prioridade))
    por_combustivel = ordenacao_selecao(MODULOS, "combustivel")
    print("  Por combustivel, menor primeiro:  " + " -> ".join(m["id"] for m in por_combustivel))

    # Criterio final do MGPEB: prioridade; em empate, menor combustivel primeiro.
    # Como a insercao e estavel, ordenar por combustivel e depois por prioridade
    # preserva a ordem de combustivel dentro de cada prioridade.
    fila_final = ordenacao_insercao(ordenacao_insercao(MODULOS, "combustivel"), "prioridade")
    print("  Fila final (prioridade, depois combustivel): "
          + " -> ".join(m["id"] for m in fila_final))

    # ---- Fila principal e listas auxiliares ---------------------------------
    linha("AUTORIZACAO DE POUSO (fila + regras booleanas)")
    fila = Fila()
    for m in fila_final:
        fila.enfileirar(m)
    pousados, em_espera, em_alerta = [], [], []
    eventos = Pilha()

    print(f"  Ambiente: vento={AMBIENTE['vento_kmh']} km/h, tempestade={AMBIENTE['tempestade_poeira']}, "
          f"zonas livres={[z for z, livre in AMBIENTE['zonas_livres'].items() if livre]}")
    while not fila.vazia():
        m = fila.desenfileirar()
        decisao, motivos = avaliar_pouso(m, AMBIENTE)
        eventos.empilhar((m["id"], decisao))
        if decisao == "AUTORIZADO":
            pousados.append(m)
            AMBIENTE["zonas_livres"][m["zona"]] = False    # zona passa a ocupada
            print(f"  [OK]  {m['id']} {m['nome']:<15} AUTORIZADO  (zona {m['zona']})")
        elif decisao == "ADIADO":
            em_espera.append(m)
            print(f"  [..]  {m['id']} {m['nome']:<15} ADIADO      ({'; '.join(motivos)})")
        else:
            em_alerta.append(m)
            print(f"  [!!]  {m['id']} {m['nome']:<15} ABORTADO    ({'; '.join(motivos)})")

    print(f"\n  Pousados:   {[m['id'] for m in pousados]}")
    print(f"  Em espera:  {[m['id'] for m in em_espera]}")
    print(f"  Em alerta:  {[m['id'] for m in em_alerta]}")

    # ---- Pilha de eventos (auditoria) ---------------------------------------
    linha("REGISTRO DE EVENTOS (pilha, do mais recente ao mais antigo)")
    print(f"  Ultimo evento (topo): {eventos.topo()}")
    while not eventos.vazia():
        print("  " + str(eventos.desempilhar()))

    # ---- Modelo matematico ---------------------------------------------------
    linha("MODELO: ALTITUDE DURANTE A DESCIDA  h(t) = h0 - v0*t - (g/2)*t^2")
    h0, v0, h_retro = 2000.0, 60.0, 500.0
    print(f"  h0={h0:.0f} m, v0={v0:.0f} m/s, g={GRAVIDADE_MARTE} m/s^2, acionamento em h={h_retro:.0f} m")
    for t in (0, 5, 10, 15, 20):
        print(f"  t={t:>2} s -> h={altitude(t, h0, v0):>8.1f} m")
    t_r, h_r = instante_retrofoguetes(h0, v0, h_retro)
    print(f"  Retrofoguetes devem acionar em t={t_r} s (h={h_r} m)")
    print("\nSimulacao concluida.")


if __name__ == "__main__":
    main()
