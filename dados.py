"""
Contém todos os dados estáticos do jogo: personagens jogáveis, tipos,
facções inimigas, cenários e vocabulário para geração procedural de
ataques inimigos.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

LARGURA_TELA = 1280
ALTURA_TELA = 720

# ---------------------------------------------------------------------------
# SISTEMA DE TIPOS (pedra-papel-tesoura)
#   Letra      vence  Vocal
#   Vocal      vence  Performance
#   Performance vence Letra
# ---------------------------------------------------------------------------
TIPOS = ["Letra", "Vocal", "Performance"]

VANTAGENS = {
    "Letra": "Vocal",
    "Vocal": "Performance",
    "Performance": "Letra",
}

CORES_TIPO = {
    "Letra": (90, 160, 255),        # azul
    "Vocal": (235, 90, 110),        # vermelho
    "Performance": (255, 200, 50),  # amarelo/dourado
}


def multiplicador_tipo(tipo_ataque, tipo_defensor):
    """Retorna o multiplicador de dano de acordo com o sistema de tipos."""
    if VANTAGENS.get(tipo_ataque) == tipo_defensor:
        return 1.5
    if VANTAGENS.get(tipo_defensor) == tipo_ataque:
        return 0.7
    return 1.0


# ---------------------------------------------------------------------------
# PERSONAGENS JOGÁVEIS
#
# tipo_efeito do especial pode ser:
#   "dano"      -> ataque comum (mais forte que o básico)
#   "cura"      -> cura um aliado escolhido (cura_percent * HP máx do aliado)
#   "veneno"    -> causa dano e envenena o alvo
#   "buff_spd"  -> causa dano e aumenta a própria velocidade por X turnos
#   "carga"     -> não causa dano neste turno; no próximo turno do
#                  personagem, libera um golpe devastador automaticamente
# ---------------------------------------------------------------------------
PERSONAGENS = {
    "liniker": {
        "nome": "Liniker",
        "tipo": "Vocal",
        "imagem": os.path.join(ASSETS_DIR, "personagens", "liniker.png"),
        "hp": 130, "atk": 22, "defe": 18, "spd": 8,
        "ataque_basico": {
            "nome": "Diáfano", "tipo": "Vocal", "mult": 1.0, "tipo_efeito": "dano",
        },
        "especial": {
            "nome": "Zero", "tipo": "Vocal", "mult": 2.5, "cooldown": 3,
            "tipo_efeito": "carga",
        },
        "descricao": "Voz potente e presença marcante. Defesa alta; o golpe "
                      "especial Zero é devastador, mas leva um turno para ser "
                      "preparado.",
    },
    "anavitoria": {
        "nome": "Anavitória",
        "tipo": "Letra",
        "imagem": os.path.join(ASSETS_DIR, "personagens", "anavitoria.png"),
        "hp": 85, "atk": 11, "defe": 9, "spd": 14,
        "ataque_basico": {
            "nome": "Trevo (Tu)", "tipo": "Letra", "mult": 0.65,
            "tipo_efeito": "dano", "golpes": 2,
        },
        "especial": {
            "nome": "Cuidar", "tipo": "Letra", "cooldown": 3,
            "tipo_efeito": "cura", "cura_percent": 0.32,
        },
        "descricao": "Letras suaves: o ataque básico acerta duas vezes, mas "
                      "com dano reduzido. Também sabe cuidar dos amigos com "
                      "a habilidade Cuidar.",
    },
    "anitta": {
        "nome": "Anitta",
        "tipo": "Performance",
        "imagem": os.path.join(ASSETS_DIR, "personagens", "anitta.png"),
        "hp": 100, "atk": 17, "defe": 12, "spd": 20,
        "ataque_basico": {
            "nome": "Bang", "tipo": "Performance", "mult": 1.0,
            "tipo_efeito": "dano",
        },
        "especial": {
            "nome": "Envolver", "tipo": "Performance", "mult": 1.6,
            "cooldown": 3, "tipo_efeito": "buff_spd",
            "buff_mult": 1.3, "buff_turnos": 2,
        },
        "descricao": "Performer extremamente ágil. Dano consistente e, com "
                      "Envolver, fica ainda mais rápida por alguns turnos.",
    },
    "linn": {
        "nome": "Linn da Quebrada",
        "tipo": "Letra",
        "imagem": os.path.join(ASSETS_DIR, "personagens", "linn.png"),
        "hp": 105, "atk": 15, "defe": 13, "spd": 12,
        "ataque_basico": {
            "nome": "Bixa Travesty", "tipo": "Letra", "mult": 1.0,
            "tipo_efeito": "dano",
        },
        "especial": {
            "nome": "Pesadão", "tipo": "Letra", "cooldown": 3,
            "tipo_efeito": "cura", "cura_percent": 0.38,
        },
        "descricao": "Letras de impacto e dano equilibrado. Pesadão é uma "
                      "habilidade de cura poderosa para os aliados.",
    },
    "luisa": {
        "nome": "Luísa Sonza",
        "tipo": "Vocal",
        "imagem": os.path.join(ASSETS_DIR, "personagens", "luisa.png"),
        "hp": 95, "atk": 12, "defe": 11, "spd": 13,
        "ataque_basico": {
            "nome": "Doidona", "tipo": "Vocal", "mult": 0.8,
            "tipo_efeito": "dano",
        },
        "especial": {
            "nome": "Penhasco", "tipo": "Vocal", "mult": 0.9,
            "cooldown": 3, "tipo_efeito": "veneno",
            "veneno_dano": 9, "veneno_turnos": 3,
        },
        "descricao": "Vocal afiado, porém de dano baixo. Penhasco aplica "
                      "veneno, causando dano contínuo ao oponente.",
    },
    "urias": {
        "nome": "Urias",
        "tipo": "Performance",
        "imagem": os.path.join(ASSETS_DIR, "personagens", "urias.png"),
        "hp": 65, "atk": 23, "defe": 7, "spd": 22,
        "ataque_basico": {
            "nome": "Single", "tipo": "Performance", "mult": 1.1,
            "tipo_efeito": "dano",
        },
        "especial": {
            "nome": "Cilada", "tipo": "Performance", "mult": 1.9,
            "cooldown": 2, "tipo_efeito": "dano",
        },
        "descricao": "Extremamente ágil e o maior dano do elenco, mas "
                      "fragilíssimo: poucos pontos de vida.",
    },
}

# Ordem fixa usada na tela de seleção
ORDEM_PERSONAGENS = ["liniker", "anavitoria", "anitta", "linn", "luisa", "urias"]


# ---------------------------------------------------------------------------
# CENÁRIOS DE BATALHA (Pernambuco)
# ---------------------------------------------------------------------------
CENARIOS = [
    {
        "nome": "Auditório da UFRPE",
        "imagem": os.path.join(ASSETS_DIR, "cenarios", "cenario1.jpg"),
    },
    {
        "nome": "Pátio de São Pedro - Recife Antigo",
        "imagem": os.path.join(ASSETS_DIR, "cenarios", "cenario2.jpg"),
    },
    {
        "nome": "Palco do Lollapalooza Brasil",
        "imagem": os.path.join(ASSETS_DIR, "cenarios", "cenario3.png"),
    },
    {
        "nome": "Forte das Cinco Pontas - Olinda",
        "imagem": os.path.join(ASSETS_DIR, "cenarios", "cenario4.jpg"),
    },
    {
        "nome": "Mesas do Recife Antigo",
        "imagem": os.path.join(ASSETS_DIR, "cenarios", "cenario5.jpg"),
    },
]


# ---------------------------------------------------------------------------
# FACÇÕES INIMIGAS - usadas para temar a batalha e nomear os adversários
# ---------------------------------------------------------------------------
FACCOES_INIMIGAS = [
    {
        "titulo": "Diário de um Cafajeste",
        "imagem": os.path.join(ASSETS_DIR, "inimigos", "inimigo5.jpg"),
        "nomes": ["DJ Oreia", "MC Lele JP", "MC Ryan SP", "MC Meno K",
                  "MC Negão Original", "MC Tuto"],
    },
    {
        "titulo": "Famoso Imã",
        "imagem": os.path.join(ASSETS_DIR, "inimigos", "inimigo4.jpg"),
        "nomes": ["MC Poze do Rodo", "MC Leozinho ZS", "DJ Gordinho da VF",
                  "O Poderoso Chatão"],
    },
    {
        "titulo": "Relíquia do ZT",
        "imagem": os.path.join(ASSETS_DIR, "inimigos", "inimigo3.jpg"),
        "nomes": ["MC Vinii", "MC Joãozinho VT", "MC Dyzin",
                  "MC FR da Norte", "DJ GLG"],
    },
    {
        "titulo": "Peão Todo Tatuado",
        "imagem": os.path.join(ASSETS_DIR, "inimigos", "inimigo2.png"),
        "nomes": ["Peão Tatuado", "Boiadeiro do Forró",
                  "Vaqueiro Apaixonado", "Sertanejo Raiz"],
    },
    {
        "titulo": "Eu Te Seguro",
        "imagem": os.path.join(ASSETS_DIR, "inimigos", "inimigo1.jpg"),
        "nomes": ["Panda", "Cantor da Sofrência",
                  "Romântico do Sertão", "Coração Apertado"],
    },
]


# ---------------------------------------------------------------------------
# VOCABULÁRIO PARA GERAÇÃO PROCEDURAL DE ATAQUES INIMIGOS
# ---------------------------------------------------------------------------
PREFIXOS_ATAQUE = [
    "Paredão", "Berro", "Trinca", "Refrão", "Grave", "Bonde", "Cria",
    "Quadradinho", "Embolada", "Mandela", "Tcheca", "Pancadão", "Repique",
    "Senta",
]

SUFIXOS_ATAQUE = [
    "Trovão", "do Bumbum", "Letal", "da Quebrada", "Profundo", "de Aço",
    "Sinistro", "do Grave", "Maluco", "Treme-Treme", "Desgovernado",
    "Sem Freio", "180 BPM", "da Madrugada",
]
