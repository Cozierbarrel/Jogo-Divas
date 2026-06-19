
"""
Define o Combatente (jogador ou inimigo) e as funções de fábrica que
criam personagens jogáveis (a partir de PERSONAGENS + bônus de evolução)
e inimigos gerados proceduralmente.
"""

import random

from dados import (
    PERSONAGENS, TIPOS, FACCOES_INIMIGAS,
    PREFIXOS_ATAQUE, SUFIXOS_ATAQUE, multiplicador_tipo,
)


class Combatente:

    def __init__(self, nome, tipo, hp_max, atk, defe, spd,
                 ataque_basico, especial=None, imagem=None,
                 eh_jogador=False, chave=None):
        self.nome = nome
        self.tipo = tipo

        self.hp_max = hp_max
        self.hp = hp_max
        self.atk = atk
        self.defe = defe
        self.spd = spd

        self.ataque_basico = ataque_basico
        self.especial = especial
        self.imagem = imagem
        self.eh_jogador = eh_jogador
        self.chave = chave  # chave do dicionário PERSONAGENS (apenas heróis)

        # ---- estado de batalha (reiniciado a cada batalha) ----
        self.vivo = True
        self.defendendo = False
        self.cooldown_especial = 0
        self.veneno_turnos = 0
        self.veneno_dano = 0
        self.buff_spd_turnos = 0
        self.buff_spd_mult = 1.0
        self.carregando = False
        self.alvo_carga = None

    # ------------------------------------------------------------------
    def spd_efetivo(self):
        if self.buff_spd_turnos > 0:
            return int(self.spd * self.buff_spd_mult)
        return self.spd

    def receber_dano(self, dano):
        if self.defendendo:
            dano = max(1, dano // 2)
        self.hp = max(0, self.hp - dano)
        if self.hp <= 0:
            self.vivo = False
        return dano

    def curar(self, valor):
        antes = self.hp
        self.hp = min(self.hp_max, self.hp + valor)
        return self.hp - antes

    def aplicar_veneno(self, dano, turnos):
        self.veneno_dano = dano
        self.veneno_turnos = turnos

    def tick_veneno(self):
        """Aplica o dano de veneno no início do turno do combatente."""
        if self.veneno_turnos > 0 and self.vivo:
            dano = min(self.hp, self.veneno_dano)
            self.hp -= dano
            self.veneno_turnos -= 1
            if self.hp <= 0:
                self.hp = 0
                self.vivo = False
            return dano
        return 0

    def porcentagem_hp(self):
        if self.hp_max <= 0:
            return 0
        return max(0.0, self.hp / self.hp_max)

    def reiniciar_para_nova_batalha(self):
        """Restaura HP/status para o início de uma nova batalha."""
        self.hp = self.hp_max
        self.vivo = True
        self.defendendo = False
        self.cooldown_especial = 0
        self.veneno_turnos = 0
        self.veneno_dano = 0
        self.buff_spd_turnos = 0
        self.buff_spd_mult = 1.0
        self.carregando = False
        self.alvo_carga = None


# ---------------------------------------------------------------------------
# FÁBRICA DE PERSONAGENS JOGÁVEIS
# ---------------------------------------------------------------------------
def criar_personagem(chave, bonus=None):
    """Cria um Combatente jogável a partir da chave em PERSONAGENS,
    aplicando os bônus acumulados de evolução (se houver)."""
    base = PERSONAGENS[chave]
    bonus = bonus or {"hp": 0, "atk": 0, "defe": 0, "spd": 0, "nivel": 1}

    hp_max = base["hp"] + bonus.get("hp", 0)
    atk = base["atk"] + bonus.get("atk", 0)
    defe = base["defe"] + bonus.get("defe", 0)
    spd = base["spd"] + bonus.get("spd", 0)

    return Combatente(
        nome=base["nome"],
        tipo=base["tipo"],
        hp_max=hp_max,
        atk=atk,
        defe=defe,
        spd=spd,
        ataque_basico=base["ataque_basico"],
        especial=base["especial"],
        imagem=base["imagem"],
        eh_jogador=True,
        chave=chave,
    )


def bonus_padrao():
    return {"hp": 0, "atk": 0, "defe": 0, "spd": 0, "nivel": 1}


def aplicar_evolucao(bonus):
    """Aumenta os atributos de evolução de um personagem.
    Retorna um dicionário com os incrementos aplicados (para exibir na UI)."""
    incrementos = {"hp": 14, "atk": 3, "defe": 2, "spd": 2}
    for atributo, valor in incrementos.items():
        bonus[atributo] += valor
    bonus["nivel"] += 1
    return incrementos


def aplicar_evolucao_personagem(personagem, bonus):
    """Aplica os incrementos de evolução diretamente em um Combatente
    já existente (mantendo a mesma instância) e atualiza o dicionário
    de bônus persistente. Retorna os incrementos aplicados."""
    incrementos = aplicar_evolucao(bonus)
    personagem.hp_max += incrementos["hp"]
    personagem.hp += incrementos["hp"]
    personagem.atk += incrementos["atk"]
    personagem.defe += incrementos["defe"]
    personagem.spd += incrementos["spd"]
    return incrementos


# ---------------------------------------------------------------------------
# GERAÇÃO PROCEDURAL DE INIMIGOS
# ---------------------------------------------------------------------------
def gerar_nome_ataque():
    return "{} {}".format(random.choice(PREFIXOS_ATAQUE),
                           random.choice(SUFIXOS_ATAQUE))


def gerar_ataques_inimigo(tipo_base, rodada):
    """Cria o ataque básico e o especial (com cooldown) de um inimigo,
    com nomes, tipos e multiplicadores aleatórios."""

    ataque_basico = {
        "nome": gerar_nome_ataque(),
        "tipo": tipo_base,
        "mult": round(random.uniform(0.85, 1.15), 2),
        "tipo_efeito": "dano",
    }

    tipo_especial = random.choice(TIPOS)
    especial = {
        "nome": gerar_nome_ataque(),
        "tipo": tipo_especial,
        "mult": round(random.uniform(1.2, 1.6), 2),
        "cooldown": 2,
        "tipo_efeito": "dano",
    }

    # Quanto mais avançada a rodada, maior a chance de o golpe especial
    # do inimigo vir com veneno embutido.
    chance_veneno = min(0.15 + (rodada - 1) * 0.04, 0.55)
    if random.random() < chance_veneno:
        especial["tipo_efeito"] = "veneno"
        especial["veneno_dano"] = max(3, int(4 + (rodada - 1) * 0.6))
        especial["veneno_turnos"] = 2

    return ataque_basico, especial


def gerar_inimigos(rodada):

    faccao = random.choice(FACCOES_INIMIGAS)

    quantidade = min(1 + (rodada - 1) // 2, 4)
    fator = 1 + (rodada - 1) * 0.14

    nomes_disponiveis = list(faccao["nomes"])
    random.shuffle(nomes_disponiveis)
    nomes_escolhidos = []
    while len(nomes_escolhidos) < quantidade:
        if nomes_disponiveis:
            nomes_escolhidos.append(nomes_disponiveis.pop())
        else:
            nomes_escolhidos.append(random.choice(faccao["nomes"]))

    inimigos = []
    for nome in nomes_escolhidos:
        tipo = random.choice(TIPOS)

        hp = int(random.randint(55, 85) * fator)
        atk = int(random.randint(9, 15) * fator)
        defe = int(random.randint(5, 11) * fator)
        spd = random.randint(7, 19)

        ataque_basico, especial = gerar_ataques_inimigo(tipo, rodada)

        inimigos.append(Combatente(
            nome=nome,
            tipo=tipo,
            hp_max=hp,
            atk=atk,
            defe=defe,
            spd=spd,
            ataque_basico=ataque_basico,
            especial=especial,
            imagem=None,
            eh_jogador=False,
        ))

    return faccao, inimigos


# ---------------------------------------------------------------------------
# CÁLCULO DE DANO
# ---------------------------------------------------------------------------
def calcular_dano(atacante, defensor, ataque):

    tipo_ataque = ataque.get("tipo", atacante.tipo)
    mult_tipo = multiplicador_tipo(tipo_ataque, defensor.tipo)

    base = atacante.atk * ataque.get("mult", 1.0)
    variancia = random.uniform(0.9, 1.1)
    reducao = defensor.defe * 0.4

    dano = base * variancia * mult_tipo - reducao
    dano = max(1, round(dano))
    return dano, mult_tipo
