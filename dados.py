import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

LARGURA_TELA = 1280
ALTURA_TELA = 720


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



PERSONAGENS = {
    "pabllo": {
        "nome": "Pabllo Vittar",
        "tipo": "Performance",
        "imagem": os.path.join(ASSETS_DIR, "personagens", "pabllo.png"),
        "hp": 110, "atk": 18, "defe": 13, "spd": 16,
        "ataque_basico": {
            "nome": "Não Paro Não", "tipo": "Performance", "mult": 1.0,
            "tipo_efeito": "dano",
        },
        "especial": {
            "nome": "K.O. Vittar", "tipo": "Performance", "mult": 1.3,
            "cooldown": 4, "tipo_efeito": "dano_todos",
            "som_especial": os.path.join(ASSETS_DIR, "sons", "Pabllo_Especial.wav"),
        },
        "som_dano": os.path.join(ASSETS_DIR, "sons", "Pabllo_dano.mp3"),
        "som_cura": os.path.join(ASSETS_DIR, "sons", "Pabllo_Cura.wav"),
        "descricao": "Rainha da Performance! Seu especial 'K.O. Vittar' atinge "
                      "TODOS os inimigos ao mesmo tempo com dano multiplicado. "
                      "Também possui sons únicos para dano e cura.",
    },
    "gloria": {
        "nome": "Gloria Groove",
        "tipo": "Vocal",
        "imagem": os.path.join(ASSETS_DIR, "personagens", "gloria_groove.png"),
        "hp": 105, "atk": 16, "defe": 14, "spd": 11,
        "ataque_basico": {
            "nome": "Coisa Boa", "tipo": "Vocal", "mult": 1.0,
            "tipo_efeito": "dano",
        },
        "especial": {
            "nome": "DIVAAAAA", "tipo": "Vocal", "mult": 1.1,
            "cooldown": 3, "tipo_efeito": "paralisar",
            "paralisia_turnos": 1,
        },
        "descricao": "Vocal poderoso e presença de diva! O especial 'DIVAAAAA' "
                      "paralisa um inimigo por 1 turno além de causar dano — "
                      "o alvo não pode agir enquanto estiver sob o efeito.",
    },
    "clarice": {
        "nome": "Clarice Falcão",
        "tipo": "Letra",
        "imagem": os.path.join(ASSETS_DIR, "personagens", "clarice_falcao.png"),
        "hp": 90, "atk": 13, "defe": 10, "spd": 13,
        "ataque_basico": {
            "nome": "Fui Fácil", "tipo": "Letra", "mult": 0.85,
            "tipo_efeito": "escudo_time",
            "escudo_percent": 0.05,
        },
        "especial": {
            "nome": "Redoma", "tipo": "Letra", "cooldown": 3,
            "tipo_efeito": "escudo_time",
            "escudo_percent": 0.20,
        },
        "descricao": "Letras inteligentes e protetora do time! Cada ataque básico "
                      "gera um escudo de 5% do HP máximo para todos os aliados. "
                      "O especial 'Redoma' cria escudos de 20% do HP máx de cada um.",
    },
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
ORDEM_PERSONAGENS = ["pabllo", "gloria", "clarice", "liniker", "anavitoria", "anitta", "linn", "luisa", "urias"]



# Cenários

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



# IInimigos

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


BOSS_RODADA = 5  

BOSSES = [
    {
        "chave": "neiff",
        "nome": "Neiff",
        "imagem": os.path.join(ASSETS_DIR, "bosses", "neiff.png"),
        "tipo": "Performance",
        "hp": 380, "atk": 28, "defe": 18, "spd": 20,
        "ataque_basico": {
            "nome": "Flow Mortal", "tipo": "Performance", "mult": 1.1, "tipo_efeito": "dano",
        },
        "especial": {
            "nome": "Neiff Total", "tipo": "Performance", "mult": 1.5,
            "cooldown": 3, "tipo_efeito": "dano_todos",
        },
        "fala_entrada": "Vocês acham que podem me vencer? Neiff não perde pra ninguém!",
        "fala_derrota": "Impossível... fui derrubado pelas divas...",
    },
    {
        "chave": "oruam",
        "nome": "Oruam",
        "imagem": os.path.join(ASSETS_DIR, "bosses", "oruam.png"),
        "tipo": "Letra",
        "hp": 420, "atk": 32, "defe": 14, "spd": 18,
        "ataque_basico": {
            "nome": "Letra de Favela", "tipo": "Letra", "mult": 1.2, "tipo_efeito": "dano",
        },
        "especial": {
            "nome": "Baile do Oruam", "tipo": "Letra", "mult": 1.0,
            "cooldown": 3, "tipo_efeito": "veneno",
            "veneno_dano": 18, "veneno_turnos": 3,
        },
        "fala_entrada": "Chegou o filho do Macarrão! Prepara o choro.",
        "fala_derrota": "Respeita as divas, mano...",
    },
    {
        "chave": "belo",
        "nome": "Belo",
        "imagem": os.path.join(ASSETS_DIR, "bosses", "belo.png"),
        "tipo": "Vocal",
        "hp": 460, "atk": 24, "defe": 26, "spd": 10,
        "ataque_basico": {
            "nome": "Sorriso Maroto", "tipo": "Vocal", "mult": 1.0, "tipo_efeito": "dano",
        },
        "especial": {
            "nome": "Escudo do Charme", "tipo": "Vocal", "cooldown": 3,
            "tipo_efeito": "escudo_proprio", "escudo_percent": 0.30,
        },
        "fala_entrada": "Belo está aqui e não vai embora fácil não, moçada!",
        "fala_derrota": "As divas sempre vencem... que voz poderosa.",
    },
    {
        "chave": "livinho",
        "nome": "MC Livinho",
        "imagem": os.path.join(ASSETS_DIR, "bosses", "livinho.png"),
        "tipo": "Performance",
        "hp": 350, "atk": 30, "defe": 16, "spd": 26,
        "ataque_basico": {
            "nome": "Cheguei", "tipo": "Performance", "mult": 1.0, "tipo_efeito": "dano",
        },
        "especial": {
            "nome": "Pesadelo Funk", "tipo": "Performance", "mult": 1.6,
            "cooldown": 2, "tipo_efeito": "paralisar", "paralisia_turnos": 1,
        },
        "fala_entrada": "Livinho no beat! Vou paralisar vocês todas!",
        "fala_derrota": "Eita... fui travado pelas divas.",
    },
    {
        "chave": "paiva",
        "nome": "Paiva",
        "imagem": os.path.join(ASSETS_DIR, "bosses", "paiva.png"),
        "tipo": "Letra",
        "hp": 500, "atk": 26, "defe": 22, "spd": 14,
        "ataque_basico": {
            "nome": "Estocada Paiva", "tipo": "Letra", "mult": 1.1,
            "tipo_efeito": "dano", "golpes": 2,
        },
        "especial": {
            "nome": "Carga Total Paiva", "tipo": "Letra", "mult": 3.0,
            "cooldown": 4, "tipo_efeito": "carga",
        },
        "fala_entrada": "Sou o boss final! Nenhuma diva me derruba!",
        "fala_derrota": "As divas são imbatíveis... respeito.",
    },
]

def boss_da_rodada(rodada):
    """Retorna o dicionário do boss se a rodada for múltipla de BOSS_RODADA, senão None."""
    if rodada % BOSS_RODADA == 0:
        idx = (rodada // BOSS_RODADA - 1) % len(BOSSES)
        return BOSSES[idx]
    return None


ITENS = {
    "torta_amora": {
        "nome": "Torta de Amora",
        "imagem": os.path.join(ASSETS_DIR, "itens", "torta_amora.png"),
        "descricao": "Cura 40% do HP máx de um aliado. Deliciosa e nutritiva.",
        "tipo_efeito": "cura",
        "cura_percent": 0.40,
        "alvo": "aliado",
        "max_estoque": 3,
    },
    "cha": {
        "nome": "Chá Revigorante",
        "imagem": os.path.join(ASSETS_DIR, "itens", "cha.png"),
        "descricao": "Remove veneno e paralisia de um aliado.",
        "tipo_efeito": "antidoto",
        "alvo": "aliado",
        "max_estoque": 3,
    },
    "pocao_rajadao": {
        "nome": "Poção Rajadão",
        "imagem": os.path.join(ASSETS_DIR, "itens", "pocao_rajadao.png"),
        "descricao": "Zera o cooldown do especial de um aliado imediatamente.",
        "tipo_efeito": "reset_cooldown",
        "alvo": "aliado",
        "max_estoque": 2,
    },
    "luva_ko": {
        "nome": "Luva K.O.",
        "imagem": os.path.join(ASSETS_DIR, "itens", "luva_ko.png"),
        "descricao": "Causa dano fixo de 60 pontos a um inimigo. Sem defesa.",
        "tipo_efeito": "dano_fixo",
        "dano": 60,
        "alvo": "inimigo",
        "max_estoque": 2,
    },
    "puzzy": {
        "nome": "Puzzy",
        "imagem": os.path.join(ASSETS_DIR, "itens", "puzzy.png"),
        "descricao": "Envenena um inimigo por 4 turnos (15 de dano/turno).",
        "tipo_efeito": "veneno",
        "veneno_dano": 15,
        "veneno_turnos": 4,
        "alvo": "inimigo",
        "max_estoque": 2,
    },
    "barquinho": {
        "nome": "Barquinho de Papel",
        "imagem": os.path.join(ASSETS_DIR, "itens", "barquinho.png"),
        "descricao": "Aumenta a velocidade de todos os aliados em 50% por 2 turnos.",
        "tipo_efeito": "buff_spd_time",
        "buff_mult": 1.5,
        "buff_turnos": 2,
        "alvo": "time",
        "max_estoque": 2,
    },
    "coroa": {
        "nome": "Coroa",
        "imagem": os.path.join(ASSETS_DIR, "itens", "coroa.png"),
        "descricao": "Cria um escudo de 30% do HP máx para todos os aliados.",
        "tipo_efeito": "escudo_time",
        "escudo_percent": 0.30,
        "alvo": "time",
        "max_estoque": 2,
    },
    "pote_de_ouro": {
        "nome": "Pote de Ouro",
        "imagem": os.path.join(ASSETS_DIR, "itens", "pote_de_ouro.png"),
        "descricao": "Cura completamente toda a party (100% do HP máx).",
        "tipo_efeito": "cura_total",
        "alvo": "time",
        "max_estoque": 1,
    },
    "grammy": {
        "nome": "Grammy",
        "imagem": os.path.join(ASSETS_DIR, "itens", "grammy.png"),
        "descricao": "Aumenta ATK+5, DEF+3 e SPD+2 de um aliado permanentemente.",
        "tipo_efeito": "buff_permanente",
        "bonus_atk": 5, "bonus_defe": 3, "bonus_spd": 2,
        "alvo": "aliado",
        "max_estoque": 1,
    },
}

ORDEM_ITENS = [
    "torta_amora", "cha", "pocao_rajadao", "luva_ko",
    "puzzy", "barquinho", "coroa", "pote_de_ouro", "grammy",
]

ITENS_COMUNS  = ["torta_amora", "cha", "pocao_rajadao", "luva_ko", "puzzy", "barquinho", "coroa"]
ITENS_RAROS   = ["pote_de_ouro", "grammy"]
