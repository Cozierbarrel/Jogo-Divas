"""
Funções e classes auxiliares de interface gráfica (pygame): fontes,
cache de imagens, botões, barras de vida e utilitários de texto.
"""

import pygame

from dados import CORES_TIPO

# ---------------------------------------------------------------------------
# CORES GERAIS
# ---------------------------------------------------------------------------
BRANCO = (245, 245, 245)
PRETO = (15, 15, 20)
CINZA = (90, 90, 100)
CINZA_CLARO = (170, 170, 180)
VERDE = (90, 220, 120)
VERMELHO = (230, 80, 80)
AMARELO = (250, 210, 70)
AZUL_DESTAQUE = (90, 170, 255)
ROXO = (180, 120, 230)
PAINEL = (20, 20, 30, 190)        # painel translúcido (RGBA)
PAINEL_CLARO = (40, 40, 55, 210)  # painel translúcido mais claro


# ---------------------------------------------------------------------------
# FONTES
# ---------------------------------------------------------------------------
class Fontes:
    """Carrega e mantém as fontes usadas no jogo."""

    def __init__(self):
        nomes_candidatos = ["dejavusans", "arial", "freesans", "verdana", "notosans"]
        nome_escolhido = None
        disponiveis = pygame.font.get_fonts()
        for nome in nomes_candidatos:
            if nome in disponiveis:
                nome_escolhido = nome
                break

        def cria(tamanho, negrito=False):
            if nome_escolhido:
                f = pygame.font.SysFont(nome_escolhido, tamanho, bold=negrito)
            else:
                f = pygame.font.Font(None, tamanho)
            return f

        self.titulo = cria(54, negrito=True)
        self.subtitulo = cria(34, negrito=True)
        self.grande = cria(28, negrito=True)
        self.normal = cria(22)
        self.normal_negrito = cria(22, negrito=True)
        self.pequena = cria(18)
        self.minuscula = cria(15)


# ---------------------------------------------------------------------------
# CACHE DE IMAGENS
# ---------------------------------------------------------------------------
_cache_imagens = {}


def carregar_imagem(caminho):
    """Carrega uma imagem do disco com cache (retorna Surface original)."""
    if caminho not in _cache_imagens:
        try:
            img = pygame.image.load(caminho)
            img = img.convert_alpha()
        except Exception:
            # imagem de fallback (retângulo cinza) caso o arquivo não exista
            img = pygame.Surface((200, 200), pygame.SRCALPHA)
            img.fill((80, 80, 90, 255))
        _cache_imagens[caminho] = img
    return _cache_imagens[caminho]


def imagem_escalada(caminho, tamanho, suave=True):
    """Carrega (com cache) e devolve a imagem já escalada para `tamanho`."""
    chave = (caminho, tamanho, suave)
    if chave not in _cache_imagens:
        original = carregar_imagem(caminho)
        if suave:
            escalada = pygame.transform.smoothscale(original, tamanho)
        else:
            escalada = pygame.transform.scale(original, tamanho)
        _cache_imagens[chave] = escalada
    return _cache_imagens[chave]


def imagem_cobertura(caminho, tamanho):
    """Escala a imagem para cobrir totalmente `tamanho` (estilo
    `background-size: cover`), cortando o excesso e centralizando."""
    chave = ("cover", caminho, tamanho)
    if chave in _cache_imagens:
        return _cache_imagens[chave]

    original = carregar_imagem(caminho)
    ow, oh = original.get_size()
    tw, th = tamanho

    escala = max(tw / ow, th / oh)
    nova_w, nova_h = int(ow * escala) + 1, int(oh * escala) + 1
    escalada = pygame.transform.smoothscale(original, (nova_w, nova_h))

    superficie = pygame.Surface(tamanho, pygame.SRCALPHA)
    x = (tw - nova_w) // 2
    y = (th - nova_h) // 2
    superficie.blit(escalada, (x, y))

    _cache_imagens[chave] = superficie
    return superficie


# ---------------------------------------------------------------------------
# TEXTO
# ---------------------------------------------------------------------------
def desenhar_texto(tela, texto, fonte, cor, pos, centro=False, sombra=False):
    if sombra:
        superficie_sombra = fonte.render(texto, True, (0, 0, 0))
        if centro:
            rect_s = superficie_sombra.get_rect(center=(pos[0] + 2, pos[1] + 2))
        else:
            rect_s = superficie_sombra.get_rect(topleft=(pos[0] + 2, pos[1] + 2))
        tela.blit(superficie_sombra, rect_s)

    superficie = fonte.render(texto, True, cor)
    if centro:
        rect = superficie.get_rect(center=pos)
    else:
        rect = superficie.get_rect(topleft=pos)
    tela.blit(superficie, rect)
    return rect


def quebrar_texto(texto, fonte, largura_max):
    """Quebra `texto` em várias linhas para que cada uma caiba em
    `largura_max` pixels com a fonte fornecida."""
    palavras = texto.split(" ")
    linhas = []
    linha_atual = ""
    for palavra in palavras:
        teste = (linha_atual + " " + palavra).strip()
        if fonte.size(teste)[0] <= largura_max:
            linha_atual = teste
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)
    return linhas


# ---------------------------------------------------------------------------
# PAINÉIS / RETÂNGULOS
# ---------------------------------------------------------------------------
def desenhar_painel(tela, rect, cor=PAINEL, borda_cor=None, borda_largura=2,
                     raio=10):
    superficie = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(superficie, cor, superficie.get_rect(), border_radius=raio)
    tela.blit(superficie, rect.topleft)
    if borda_cor:
        pygame.draw.rect(tela, borda_cor, rect, borda_largura, border_radius=raio)


# ---------------------------------------------------------------------------
# BARRA DE VIDA / RECURSOS
# ---------------------------------------------------------------------------
def desenhar_barra(tela, x, y, largura, altura, fracao, cor_frente,
                    cor_fundo=(50, 50, 60), borda_cor=(230, 230, 230)):
    fracao = max(0.0, min(1.0, fracao))
    pygame.draw.rect(tela, cor_fundo, (x, y, largura, altura), border_radius=4)
    if fracao > 0:
        pygame.draw.rect(tela, cor_frente, (x, y, int(largura * fracao), altura),
                          border_radius=4)
    pygame.draw.rect(tela, borda_cor, (x, y, largura, altura), 1, border_radius=4)


def cor_barra_hp(fracao):
    if fracao > 0.5:
        return VERDE
    if fracao > 0.2:
        return AMARELO
    return VERMELHO


# ---------------------------------------------------------------------------
# BOTÕES
# ---------------------------------------------------------------------------
class Botao:
    def __init__(self, rect, texto, cor=(60, 70, 100), cor_hover=(90, 105, 150),
                 cor_texto=BRANCO, ativo=True, sub_texto=None):
        self.rect = pygame.Rect(rect)
        self.texto = texto
        self.sub_texto = sub_texto
        self.cor = cor
        self.cor_hover = cor_hover
        self.cor_texto = cor_texto
        self.ativo = ativo

    def desenhar(self, tela, fonte, mouse_pos, fonte_pequena=None):
        sobre = self.rect.collidepoint(mouse_pos)
        if not self.ativo:
            cor = (45, 45, 55)
            cor_texto = (120, 120, 130)
        else:
            cor = self.cor_hover if sobre else self.cor
            cor_texto = self.cor_texto

        pygame.draw.rect(tela, cor, self.rect, border_radius=10)
        pygame.draw.rect(tela, (15, 15, 20), self.rect, 2, border_radius=10)

        if self.sub_texto and fonte_pequena:
            desenhar_texto(tela, self.texto, fonte, cor_texto,
                            (self.rect.centerx, self.rect.centery - 11), centro=True)
            desenhar_texto(tela, self.sub_texto, fonte_pequena, cor_texto,
                            (self.rect.centerx, self.rect.centery + 13), centro=True)
        else:
            desenhar_texto(tela, self.texto, fonte, cor_texto,
                            self.rect.center, centro=True)

    def clicado(self, pos_mouse):
        return self.ativo and self.rect.collidepoint(pos_mouse)
