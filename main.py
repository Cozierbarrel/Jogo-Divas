# -*- coding: utf-8 -*-
"""
main.py
Batalha das Divas - Edição Pernambuco
"""

import math
import random

import pygame

from dados import (
    LARGURA_TELA, ALTURA_TELA, PERSONAGENS, ORDEM_PERSONAGENS,
    CORES_TIPO, TIPOS,
)
from entidades import (
    criar_personagem, bonus_padrao, aplicar_evolucao_personagem,
)
from batalha import Batalha
from interface import (
    Fontes, Botao, BRANCO, PRETO, CINZA, CINZA_CLARO, VERDE, VERMELHO,
    AMARELO, AZUL_DESTAQUE, ROXO, PAINEL, PAINEL_CLARO,
    desenhar_texto, desenhar_painel, desenhar_barra, cor_barra_hp,
    quebrar_texto, imagem_cobertura,
)

FPS = 60

EFEITO_LABEL = {
    "dano": "Dano",
    "cura": "Cura",
    "veneno": "Veneno",
    "buff_spd": "Agilidade",
    "carga": "Carga",
}


def iniciais_nome(nome):
    palavras = nome.split()
    if len(palavras) == 1:
        return palavras[0][:2].upper()
    return (palavras[0][0] + palavras[1][0]).upper()


def tipo_alvo_de_acao(combatente, tipo_acao):
    """Retorna 'inimigo', 'aliado' ou None (sem alvo) para a ação dada."""
    if tipo_acao == "atacar":
        return "inimigo"
    if tipo_acao == "especial":
        especial = combatente.especial
        if especial and especial.get("tipo_efeito") == "cura":
            return "aliado"
        return "inimigo"
    return None


# ---------------------------------------------------------------------------
# LAYOUT - constantes de posicionamento
# ---------------------------------------------------------------------------
# -- Seleção de personagens --
SEL_COLS = 3
SEL_CARD_W, SEL_CARD_H = 380, 250
SEL_GAP_X, SEL_GAP_Y = 25, 20
SEL_START_X = (LARGURA_TELA - (SEL_COLS * SEL_CARD_W + (SEL_COLS - 1) * SEL_GAP_X)) // 2
SEL_START_Y = 95

# -- Batalha --
BAT_TOPO_H = 70
BAT_PAINEL_X = 15
BAT_PAINEL_W = 320
BAT_CARD_H = 145
BAT_CARD_GAP = 8
BAT_INIMIGO_X = LARGURA_TELA - BAT_PAINEL_W - 15
BAT_CENTRO_X = BAT_PAINEL_X + BAT_PAINEL_W + 15
BAT_CENTRO_W = BAT_INIMIGO_X - BAT_CENTRO_X - 15

BAT_LOG_Y = BAT_TOPO_H + 10
BAT_LOG_H = 320
BAT_ACAO_Y = BAT_LOG_Y + BAT_LOG_H + 10
BAT_ACAO_H = ALTURA_TELA - BAT_ACAO_Y - 10

ACAO_BTN_W, ACAO_BTN_H = 175, 70
ACAO_BTN_GAP = 20

# -- Evolução --
EVO_CARD_W, EVO_CARD_H = 290, 360
EVO_GAP = 25
EVO_START_X = (LARGURA_TELA - (4 * EVO_CARD_W + 3 * EVO_GAP)) // 2
EVO_START_Y = 150


class Jogo:
    def __init__(self, fontes):
        self.fontes = fontes
        self.estado = "menu"

        self.rodada = 1
        self.bonus = {}
        self.ordem_selecao = []  # chaves escolhidas na tela de seleção
        self.party = []

        self.batalha = None
        self.log_exibido = 0
        self.timer_log = 0.0
        self.intervalo_log = 0.55

        self.alvo_pendente = None  # None | "atacar" | "especial"
        self.evolucao_resultado = None  # (chave, incrementos) após escolha

        self.tempo_total = 0.0

    # ------------------------------------------------------------------
    # FLUXO ENTRE TELAS
    # ------------------------------------------------------------------
    def ir_para_selecao(self):
        self.ordem_selecao = []
        self.estado = "selecao"

    def iniciar_jogo(self):
        self.rodada = 1
        self.bonus = {chave: bonus_padrao() for chave in self.ordem_selecao}
        self.party = [criar_personagem(chave, self.bonus[chave])
                       for chave in self.ordem_selecao]
        self.preparar_nova_batalha()

    def preparar_nova_batalha(self):
        self.batalha = Batalha(self.party, self.rodada)
        self.log_exibido = 0
        self.timer_log = 0.0
        self.alvo_pendente = None
        self.estado = "transicao"
        self.timer_transicao = 0.0

    def reiniciar_jogo(self):
        self.rodada = 1
        self.bonus = {}
        self.party = []
        self.ordem_selecao = []
        self.batalha = None
        self.estado = "menu"

    # ------------------------------------------------------------------
    # ATUALIZAÇÃO
    # ------------------------------------------------------------------
    def atualizar(self, dt):
        self.tempo_total += dt

        if self.estado == "transicao":
            self.timer_transicao += dt
            if self.timer_transicao > 2.2:
                self.estado = "batalha"

        elif self.estado == "batalha" and self.batalha is not None:
            total = len(self.batalha.log)
            if self.log_exibido < total:
                self.timer_log += dt
                if self.timer_log >= self.intervalo_log:
                    self.timer_log = 0.0
                    self.log_exibido += 1

    # ------------------------------------------------------------------
    # EVENTOS
    # ------------------------------------------------------------------
    def processar_evento(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            pos = evento.pos
            if self.estado == "menu":
                self.ir_para_selecao()
            elif self.estado == "selecao":
                self.clique_selecao(pos)
            elif self.estado == "transicao":
                self.estado = "batalha"
            elif self.estado == "batalha":
                self.clique_batalha(pos)
            elif self.estado == "evolucao":
                self.clique_evolucao(pos)
            elif self.estado == "gameover":
                self.clique_gameover(pos)

        elif evento.type == pygame.KEYDOWN:
            if evento.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.estado == "menu":
                    self.ir_para_selecao()
                elif self.estado == "transicao":
                    self.estado = "batalha"

    # ------------------------------------------------------------------
    # TELA: MENU
    # ------------------------------------------------------------------
    def desenhar_menu(self, tela):
        fundo = imagem_cobertura(
            PERSONAGENS["anitta"]["imagem"], (LARGURA_TELA, ALTURA_TELA))
        tela.blit(fundo, (0, 0))
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 190))
        tela.blit(overlay, (0, 0))

        desenhar_texto(tela, "BATALHA DAS DIVAS", self.fontes.titulo, AMARELO,
                        (LARGURA_TELA // 2, 210), centro=True, sombra=True)
        desenhar_texto(tela, "Edição Pernambuco", self.fontes.subtitulo, BRANCO,
                        (LARGURA_TELA // 2, 270), centro=True, sombra=True)

        linhas = [
            "Monte sua party com 4 das 6 estrelas disponíveis e enfrente",
            "ondas infinitas de inimigos gerados aleatoriamente!",
            "",
            "Sistema de tipos: Letra > Vocal > Performance > Letra",
            "",
            "Vença batalhas para evoluir seus personagens e fique cada",
            "vez mais forte. Boa sorte!",
        ]
        y = 360
        for linha in linhas:
            if linha:
                desenhar_texto(tela, linha, self.fontes.normal, CINZA_CLARO,
                                (LARGURA_TELA // 2, y), centro=True, sombra=True)
            y += 32

        pulso = 0.5 + 0.5 * math.sin(self.tempo_total * 3)
        cor = (int(255 * pulso), int(255 * pulso), int(255 * pulso))
        desenhar_texto(tela, "Clique ou pressione ENTER para começar",
                        self.fontes.grande, cor,
                        (LARGURA_TELA // 2, ALTURA_TELA - 70), centro=True, sombra=True)

    # ------------------------------------------------------------------
    # TELA: SELEÇÃO DE PERSONAGENS
    # ------------------------------------------------------------------
    def _rect_card_selecao(self, indice):
        col = indice % SEL_COLS
        row = indice // SEL_COLS
        x = SEL_START_X + col * (SEL_CARD_W + SEL_GAP_X)
        y = SEL_START_Y + row * (SEL_CARD_H + SEL_GAP_Y)
        return pygame.Rect(x, y, SEL_CARD_W, SEL_CARD_H)

    def _rect_confirmar_selecao(self):
        w, h = 260, 60
        return pygame.Rect((LARGURA_TELA - w) // 2, SEL_START_Y + 2 * SEL_CARD_H + SEL_GAP_Y + 20, w, h)

    def desenhar_selecao(self, tela):
        tela.fill((25, 25, 35))

        desenhar_texto(tela, "Escolha sua party (4 personagens)",
                        self.fontes.subtitulo, BRANCO,
                        (LARGURA_TELA // 2, 40), centro=True, sombra=True)
        desenhar_texto(tela, "Selecionados: {}/4".format(len(self.ordem_selecao)),
                        self.fontes.normal, AMARELO,
                        (LARGURA_TELA // 2, 75), centro=True)

        for i, chave in enumerate(ORDEM_PERSONAGENS):
            dados_p = PERSONAGENS[chave]
            rect = self._rect_card_selecao(i)
            selecionado = chave in self.ordem_selecao

            cor_tipo = CORES_TIPO[dados_p["tipo"]]
            cor_borda = AMARELO if selecionado else cor_tipo
            espessura = 4 if selecionado else 2

            desenhar_painel(tela, rect, cor=(35, 35, 50, 230),
                             borda_cor=cor_borda, borda_largura=espessura, raio=14)

            # retrato
            ret_img = imagem_cobertura(dados_p["imagem"], (110, 130))
            img_pos = (rect.x + 15, rect.y + 15)
            tela.blit(ret_img, img_pos)
            pygame.draw.rect(tela, cor_tipo, (img_pos[0], img_pos[1], 110, 130), 2)

            tx = rect.x + 140
            desenhar_texto(tela, dados_p["nome"], self.fontes.grande, BRANCO,
                            (tx, rect.y + 15))

            # selo de tipo
            selo_rect = pygame.Rect(tx, rect.y + 50, 120, 26)
            pygame.draw.rect(tela, cor_tipo, selo_rect, border_radius=6)
            desenhar_texto(tela, dados_p["tipo"], self.fontes.pequena, PRETO,
                            selo_rect.center, centro=True)

            # status base
            desenhar_texto(
                tela,
                "HP {}  ATK {}  DEF {}  SPD {}".format(
                    dados_p["hp"], dados_p["atk"], dados_p["defe"], dados_p["spd"]),
                self.fontes.pequena, CINZA_CLARO, (tx, rect.y + 85))

            ab = dados_p["ataque_basico"]
            es = dados_p["especial"]
            desenhar_texto(
                tela, "Básico: {} ({})".format(ab["nome"], ab["tipo"]),
                self.fontes.minuscula, CINZA_CLARO, (tx, rect.y + 112))
            desenhar_texto(
                tela, "Especial: {} - {}".format(es["nome"], EFEITO_LABEL.get(es.get("tipo_efeito"), "")),
                self.fontes.minuscula, CINZA_CLARO, (tx, rect.y + 132))

            # descrição
            linhas = quebrar_texto(dados_p["descricao"], self.fontes.minuscula, SEL_CARD_W - 30)
            yy = rect.y + 155
            for linha in linhas[:4]:
                desenhar_texto(tela, linha, self.fontes.minuscula, (210, 210, 220),
                                (rect.x + 15, yy))
                yy += 18

        # botão confirmar
        rect_confirmar = self._rect_confirmar_selecao()
        ativo = len(self.ordem_selecao) == 4
        botao = Botao(rect_confirmar, "Confirmar party",
                       cor=(70, 150, 90) if ativo else (60, 60, 70),
                       cor_hover=(90, 190, 110), ativo=ativo)
        botao.desenhar(tela, self.fontes.grande, pygame.mouse.get_pos())

    def clique_selecao(self, pos):
        for i, chave in enumerate(ORDEM_PERSONAGENS):
            rect = self._rect_card_selecao(i)
            if rect.collidepoint(pos):
                if chave in self.ordem_selecao:
                    self.ordem_selecao.remove(chave)
                elif len(self.ordem_selecao) < 4:
                    self.ordem_selecao.append(chave)
                return

        if len(self.ordem_selecao) == 4 and self._rect_confirmar_selecao().collidepoint(pos):
            self.iniciar_jogo()

    # ------------------------------------------------------------------
    # TELA: TRANSIÇÃO ENTRE BATALHAS
    # ------------------------------------------------------------------
    def desenhar_transicao(self, tela):
        b = self.batalha
        fundo = imagem_cobertura(b.cenario["imagem"], (LARGURA_TELA, ALTURA_TELA))
        tela.blit(fundo, (0, 0))
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 165))
        tela.blit(overlay, (0, 0))

        desenhar_texto(tela, "Rodada {}".format(self.rodada), self.fontes.titulo,
                        AMARELO, (LARGURA_TELA // 2, 180), centro=True, sombra=True)
        desenhar_texto(tela, b.cenario["nome"], self.fontes.subtitulo, BRANCO,
                        (LARGURA_TELA // 2, 250), centro=True, sombra=True)

        # banner da facção inimiga
        banner = imagem_cobertura(b.faccao["imagem"], (260, 260))
        banner_rect = banner.get_rect(center=(LARGURA_TELA // 2, 410))
        tela.blit(banner, banner_rect)
        pygame.draw.rect(tela, VERMELHO, banner_rect, 3)

        desenhar_texto(tela, "Inimigos aproximando-se:", self.fontes.normal, BRANCO,
                        (LARGURA_TELA // 2, banner_rect.bottom + 30), centro=True, sombra=True)

        nomes = ", ".join(i.nome for i in b.inimigos)
        for linha in quebrar_texto(nomes, self.fontes.normal, LARGURA_TELA - 200):
            desenhar_texto(tela, linha, self.fontes.normal, VERMELHO,
                            (LARGURA_TELA // 2, banner_rect.bottom + 65), centro=True, sombra=True)

        pulso = 0.5 + 0.5 * math.sin(self.tempo_total * 3)
        cor = (int(255 * pulso), int(255 * pulso), int(255 * pulso))
        desenhar_texto(tela, "Clique para lutar!", self.fontes.grande, cor,
                        (LARGURA_TELA // 2, ALTURA_TELA - 50), centro=True, sombra=True)

    # ------------------------------------------------------------------
    # TELA: BATALHA
    # ------------------------------------------------------------------
    def _rect_card_party(self, indice):
        y = BAT_TOPO_H + 10 + indice * (BAT_CARD_H + BAT_CARD_GAP)
        return pygame.Rect(BAT_PAINEL_X, y, BAT_PAINEL_W, BAT_CARD_H)

    def _rect_card_inimigo(self, indice, total):
        area_total_h = 4 * BAT_CARD_H + 3 * BAT_CARD_GAP
        grupo_h = total * BAT_CARD_H + (total - 1) * BAT_CARD_GAP
        offset = max(0, (area_total_h - grupo_h) // 2)
        y = BAT_TOPO_H + 10 + offset + indice * (BAT_CARD_H + BAT_CARD_GAP)
        return pygame.Rect(BAT_INIMIGO_X, y, BAT_PAINEL_W, BAT_CARD_H)

    def _rects_botoes_acao(self):
        total_w = 3 * ACAO_BTN_W + 2 * ACAO_BTN_GAP
        start_x = BAT_CENTRO_X + (BAT_CENTRO_W - total_w) // 2
        y = BAT_ACAO_Y + 70
        rects = []
        for i in range(3):
            rects.append(pygame.Rect(start_x + i * (ACAO_BTN_W + ACAO_BTN_GAP), y,
                                      ACAO_BTN_W, ACAO_BTN_H))
        return rects

    def _rect_cancelar_alvo(self):
        w, h = 200, 50
        x = BAT_CENTRO_X + (BAT_CENTRO_W - w) // 2
        y = BAT_ACAO_Y + 150
        return pygame.Rect(x, y, w, h)

    def _rect_botao_continuar_batalha(self):
        w, h = 260, 60
        return pygame.Rect((LARGURA_TELA - w) // 2, ALTURA_TELA // 2 + 60, w, h)

    def _desenhar_card_combatente(self, tela, rect, combatente, eh_jogador,
                                    destaque_turno=False, destaque_alvo=False):
        if not combatente.vivo:
            cor_fundo = (30, 30, 35, 180)
        else:
            cor_fundo = (35, 35, 50, 215)

        borda_cor = (90, 90, 100)
        borda_largura = 2
        if destaque_alvo and combatente.vivo:
            pulso = 0.5 + 0.5 * math.sin(self.tempo_total * 6)
            tom = int(150 + 105 * pulso)
            borda_cor = (255, tom, 40)
            borda_largura = 4
        elif destaque_turno:
            borda_cor = AMARELO
            borda_largura = 4

        desenhar_painel(tela, rect, cor=cor_fundo, borda_cor=borda_cor,
                         borda_largura=borda_largura, raio=10)

        cor_tipo = CORES_TIPO[combatente.tipo]

        if eh_jogador and combatente.imagem:
            img = imagem_cobertura(combatente.imagem, (85, 95))
            tela.blit(img, (rect.x + 10, rect.y + 10))
            pygame.draw.rect(tela, cor_tipo, (rect.x + 10, rect.y + 10, 85, 95), 2)
            tx = rect.x + 105
        else:
            centro = (rect.x + 52, rect.y + 57)
            pygame.draw.circle(tela, cor_tipo, centro, 42)
            pygame.draw.circle(tela, PRETO, centro, 42, 2)
            desenhar_texto(tela, iniciais_nome(combatente.nome),
                            self.fontes.grande, PRETO, centro, centro=True)
            tx = rect.x + 105

        cor_nome = BRANCO if combatente.vivo else (130, 130, 130)
        nome_exibido = combatente.nome
        if len(nome_exibido) > 18:
            nome_exibido = nome_exibido[:17] + "…"
        desenhar_texto(tela, nome_exibido, self.fontes.normal_negrito, cor_nome,
                        (tx, rect.y + 8))

        selo_rect = pygame.Rect(tx, rect.y + 38, 100, 22)
        pygame.draw.rect(tela, cor_tipo, selo_rect, border_radius=5)
        desenhar_texto(tela, combatente.tipo, self.fontes.minuscula, PRETO,
                        selo_rect.center, centro=True)

        # barra de HP
        frac = combatente.porcentagem_hp()
        barra_largura = rect.width - (tx - rect.x) - 15
        desenhar_barra(tela, tx, rect.y + 68, barra_largura, 16, frac,
                        cor_barra_hp(frac))
        desenhar_texto(tela, "{}/{}".format(combatente.hp, combatente.hp_max),
                        self.fontes.minuscula, BRANCO, (tx + 4, rect.y + 67))

        # status extras
        status_textos = []
        if not combatente.vivo:
            status_textos.append(("Derrotado", (160, 60, 60)))
        else:
            if combatente.defendendo:
                status_textos.append(("Defendendo", AZUL_DESTAQUE))
            if combatente.veneno_turnos > 0:
                status_textos.append(("Veneno x{}".format(combatente.veneno_turnos), (170, 90, 230)))
            if combatente.buff_spd_turnos > 0:
                status_textos.append(("Ágil x{}".format(combatente.buff_spd_turnos), VERDE))
            if combatente.carregando:
                status_textos.append(("Carregando...", AMARELO))
            if eh_jogador and combatente.cooldown_especial > 0:
                status_textos.append(("CD especial: {}".format(combatente.cooldown_especial), CINZA_CLARO))

        sx = tx
        sy = rect.y + 95
        for texto, cor in status_textos[:2]:
            largura = self.fontes.minuscula.size(texto)[0] + 12
            pygame.draw.rect(tela, (0, 0, 0, 140), (sx, sy, largura, 20), border_radius=5)
            desenhar_texto(tela, texto, self.fontes.minuscula, cor, (sx + 6, sy + 2))
            sx += largura + 8

    def desenhar_batalha(self, tela):
        b = self.batalha
        fundo = imagem_cobertura(b.cenario["imagem"], (LARGURA_TELA, ALTURA_TELA))
        tela.blit(fundo, (0, 0))
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 145))
        tela.blit(overlay, (0, 0))

        # ---- barra superior ----
        desenhar_painel(tela, pygame.Rect(0, 0, LARGURA_TELA, BAT_TOPO_H),
                         cor=(15, 15, 25, 220), raio=0)
        desenhar_texto(tela, "Rodada {}".format(self.rodada), self.fontes.grande,
                        AMARELO, (20, BAT_TOPO_H // 2), centro=False)
        desenhar_texto(tela, b.cenario["nome"], self.fontes.normal, BRANCO,
                        (LARGURA_TELA // 2, BAT_TOPO_H // 2), centro=True)

        banner = imagem_cobertura(b.faccao["imagem"], (50, 50))
        banner_x = LARGURA_TELA - 20 - 50
        tela.blit(banner, (banner_x, 10))
        pygame.draw.rect(tela, VERMELHO, (banner_x, 10, 50, 50), 2)
        desenhar_texto(tela, b.faccao["titulo"], self.fontes.pequena, VERMELHO,
                        (banner_x - 10, BAT_TOPO_H // 2), centro=False)

        atual = b.aguardando_jogador() if self.log_exibido >= len(b.log) else None

        # ---- painel da party ----
        for i, heroi in enumerate(self.party):
            rect = self._rect_card_party(i)
            destaque_turno = (atual is heroi)
            destaque_alvo = (self.alvo_pendente is not None and atual is not None and
                             tipo_alvo_de_acao(atual, self.alvo_pendente) == "aliado" and
                             heroi.vivo)
            self._desenhar_card_combatente(tela, rect, heroi, True,
                                            destaque_turno, destaque_alvo)

        # ---- painel dos inimigos ----
        total_inimigos = len(b.inimigos)
        for i, inimigo in enumerate(b.inimigos):
            rect = self._rect_card_inimigo(i, total_inimigos)
            destaque_alvo = (self.alvo_pendente is not None and atual is not None and
                             tipo_alvo_de_acao(atual, self.alvo_pendente) == "inimigo" and
                             inimigo.vivo)
            self._desenhar_card_combatente(tela, rect, inimigo, False,
                                            False, destaque_alvo)

        # ---- painel central: log de batalha ----
        log_rect = pygame.Rect(BAT_CENTRO_X, BAT_LOG_Y, BAT_CENTRO_W, BAT_LOG_H)
        desenhar_painel(tela, log_rect, cor=(15, 15, 25, 200),
                         borda_cor=(90, 90, 110), raio=12)
        desenhar_texto(tela, "Log da batalha", self.fontes.normal_negrito, AMARELO,
                        (log_rect.x + 15, log_rect.y + 10))

        mensagens = b.log[:self.log_exibido]
        max_linhas = (BAT_LOG_H - 55) // 26
        visiveis = []
        for msg in mensagens:
            visiveis.extend(quebrar_texto(msg, self.fontes.pequena, BAT_CENTRO_W - 30))
        visiveis = visiveis[-max_linhas:]
        yy = log_rect.y + 45
        for linha in visiveis:
            desenhar_texto(tela, linha, self.fontes.pequena, (225, 225, 230),
                            (log_rect.x + 15, yy))
            yy += 26

        # ---- painel central: ações ----
        acao_rect = pygame.Rect(BAT_CENTRO_X, BAT_ACAO_Y, BAT_CENTRO_W, BAT_ACAO_H)
        desenhar_painel(tela, acao_rect, cor=(15, 15, 25, 200),
                         borda_cor=(90, 90, 110), raio=12)

        if b.terminada and self.log_exibido >= len(b.log):
            if b.vitoria:
                texto = "VITÓRIA!"
                cor = VERDE
                texto_botao = "Continuar"
            else:
                texto = "DERROTA..."
                cor = VERMELHO
                texto_botao = "Ver resultado"

            overlay2 = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
            overlay2.fill((0, 0, 0, 130))
            tela.blit(overlay2, (0, 0))
            desenhar_texto(tela, texto, self.fontes.titulo, cor,
                            (LARGURA_TELA // 2, ALTURA_TELA // 2 - 30), centro=True, sombra=True)
            botao = Botao(self._rect_botao_continuar_batalha(), texto_botao,
                           cor=(70, 150, 90) if b.vitoria else (150, 70, 70),
                           cor_hover=(90, 190, 110) if b.vitoria else (190, 90, 90))
            botao.desenhar(tela, self.fontes.grande, pygame.mouse.get_pos())
            return

        if self.log_exibido < len(b.log):
            desenhar_texto(tela, "...", self.fontes.subtitulo, CINZA_CLARO,
                            (acao_rect.centerx, acao_rect.y + 35), centro=True)
            return

        if atual is None:
            return

        cor_tipo = CORES_TIPO[atual.tipo]
        desenhar_texto(tela, "Turno de {}".format(atual.nome), self.fontes.grande,
                        cor_tipo, (acao_rect.centerx, acao_rect.y + 30), centro=True, sombra=True)

        if self.alvo_pendente is not None:
            tipo_alvo = tipo_alvo_de_acao(atual, self.alvo_pendente)
            texto_alvo = ("Escolha um aliado para curar" if tipo_alvo == "aliado"
                           else "Escolha um inimigo como alvo")
            desenhar_texto(tela, texto_alvo, self.fontes.normal, AMARELO,
                            (acao_rect.centerx, acao_rect.y + 80), centro=True)

            botao_cancelar = Botao(self._rect_cancelar_alvo(), "Cancelar",
                                    cor=(110, 60, 60), cor_hover=(150, 80, 80))
            botao_cancelar.desenhar(tela, self.fontes.normal, pygame.mouse.get_pos())
            return

        # botões de ação
        rects = self._rects_botoes_acao()
        especial = atual.especial
        especial_pronto = especial is not None and atual.cooldown_especial == 0

        if especial is not None:
            sub_especial = "Pronto!" if especial_pronto else "CD: {}".format(atual.cooldown_especial)
            nome_especial = especial["nome"]
        else:
            sub_especial = "--"
            nome_especial = "(sem especial)"

        info_botoes = [
            ("atacar", "Atacar", atual.ataque_basico["nome"], True),
            ("especial", nome_especial, sub_especial, especial_pronto),
            ("defender", "Defender", "Reduz dano", True),
        ]

        for (tipo_acao, nome, sub, ativo), rect in zip(info_botoes, rects):
            if tipo_acao == "atacar":
                cor = (60, 90, 150)
                cor_hover = (85, 120, 190)
            elif tipo_acao == "especial":
                cor = (110, 60, 140) if ativo else (60, 60, 70)
                cor_hover = (150, 90, 190)
            else:
                cor = (70, 110, 80)
                cor_hover = (95, 150, 105)

            botao = Botao(rect, nome, cor=cor, cor_hover=cor_hover,
                           ativo=ativo, sub_texto=sub)
            botao.desenhar(tela, self.fontes.normal_negrito, pygame.mouse.get_pos(),
                            fonte_pequena=self.fontes.minuscula)

    # ------------------------------------------------------------------
    def _alvo_no_clique(self, pos, tipo_acao, atual):
        b = self.batalha
        tipo_alvo = tipo_alvo_de_acao(atual, tipo_acao)

        if tipo_alvo == "inimigo":
            for i, inimigo in enumerate(b.inimigos):
                if inimigo.vivo and self._rect_card_inimigo(i, len(b.inimigos)).collidepoint(pos):
                    return inimigo
        elif tipo_alvo == "aliado":
            for i, heroi in enumerate(self.party):
                if heroi.vivo and self._rect_card_party(i).collidepoint(pos):
                    return heroi
        return None

    def _escolher_acao(self, atual, tipo_acao):
        b = self.batalha
        if tipo_acao == "defender":
            b.executar_acao_jogador("defender", None)
            return

        tipo_alvo = tipo_alvo_de_acao(atual, tipo_acao)
        if tipo_alvo == "inimigo":
            candidatos = b.inimigos_vivos()
        else:
            candidatos = b.party_vivos()

        if len(candidatos) == 1:
            b.executar_acao_jogador(tipo_acao, candidatos[0])
        elif len(candidatos) > 1:
            self.alvo_pendente = tipo_acao
        else:
            # sem alvo válido (não deveria ocorrer)
            self.alvo_pendente = None

    def clique_batalha(self, pos):
        b = self.batalha
        if b is None:
            return

        if b.terminada and self.log_exibido >= len(b.log):
            if self._rect_botao_continuar_batalha().collidepoint(pos):
                if b.vitoria:
                    self.evolucao_resultado = None
                    self.estado = "evolucao"
                else:
                    self.estado = "gameover"
            return

        if self.log_exibido < len(b.log):
            self.log_exibido = len(b.log)
            return

        atual = b.aguardando_jogador()
        if atual is None:
            return

        if self.alvo_pendente is not None:
            if self._rect_cancelar_alvo().collidepoint(pos):
                self.alvo_pendente = None
                return
            alvo = self._alvo_no_clique(pos, self.alvo_pendente, atual)
            if alvo is not None:
                b.executar_acao_jogador(self.alvo_pendente, alvo)
                self.alvo_pendente = None
            return

        rects = self._rects_botoes_acao()
        especial_pronto = (atual.especial is not None and atual.cooldown_especial == 0)
        ativos = [True, especial_pronto, True]
        nomes_acao = ["atacar", "especial", "defender"]

        for nome_acao, ativo, rect in zip(nomes_acao, ativos, rects):
            if ativo and rect.collidepoint(pos):
                self._escolher_acao(atual, nome_acao)
                return

    # ------------------------------------------------------------------
    # TELA: EVOLUÇÃO
    # ------------------------------------------------------------------
    def _rect_card_evolucao(self, indice):
        x = EVO_START_X + indice * (EVO_CARD_W + EVO_GAP)
        return pygame.Rect(x, EVO_START_Y, EVO_CARD_W, EVO_CARD_H)

    def _rect_continuar_evolucao(self):
        w, h = 260, 60
        return pygame.Rect((LARGURA_TELA - w) // 2, ALTURA_TELA - 90, w, h)

    def desenhar_evolucao(self, tela):
        fundo = imagem_cobertura(self.batalha.cenario["imagem"], (LARGURA_TELA, ALTURA_TELA))
        tela.blit(fundo, (0, 0))
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 180))
        tela.blit(overlay, (0, 0))

        desenhar_texto(tela, "Vitória na Rodada {}!".format(self.rodada),
                        self.fontes.titulo, VERDE, (LARGURA_TELA // 2, 60), centro=True, sombra=True)

        if self.evolucao_resultado is None:
            desenhar_texto(tela, "Escolha um personagem para evoluir",
                            self.fontes.subtitulo, BRANCO,
                            (LARGURA_TELA // 2, 110), centro=True, sombra=True)

            for i, heroi in enumerate(self.party):
                rect = self._rect_card_evolucao(i)
                cor_tipo = CORES_TIPO[heroi.tipo]
                desenhar_painel(tela, rect, cor=(35, 35, 50, 230),
                                 borda_cor=cor_tipo, borda_largura=3, raio=14)

                img = imagem_cobertura(heroi.imagem, (EVO_CARD_W - 30, 140))
                tela.blit(img, (rect.x + 15, rect.y + 15))
                pygame.draw.rect(tela, cor_tipo, (rect.x + 15, rect.y + 15, EVO_CARD_W - 30, 140), 2)

                desenhar_texto(tela, heroi.nome, self.fontes.grande, BRANCO,
                                (rect.centerx, rect.y + 175), centro=True)

                nivel = self.bonus[heroi.chave]["nivel"]
                desenhar_texto(tela, "Nível {}".format(nivel), self.fontes.normal,
                                AMARELO, (rect.centerx, rect.y + 205), centro=True)

                stats = [
                    "HP: {}".format(heroi.hp_max),
                    "ATK: {}".format(heroi.atk),
                    "DEF: {}".format(heroi.defe),
                    "SPD: {}".format(heroi.spd),
                ]
                yy = rect.y + 235
                for s in stats:
                    desenhar_texto(tela, s, self.fontes.normal, CINZA_CLARO,
                                    (rect.centerx, yy), centro=True)
                    yy += 26

                desenhar_texto(tela, "Clique para evoluir!", self.fontes.pequena, VERDE,
                                (rect.centerx, rect.bottom - 15), centro=True)
        else:
            chave, incrementos = self.evolucao_resultado
            heroi = next(p for p in self.party if p.chave == chave)
            desenhar_texto(tela, "{} evoluiu para o nível {}!".format(
                heroi.nome, self.bonus[chave]["nivel"]),
                self.fontes.subtitulo, AMARELO, (LARGURA_TELA // 2, 230), centro=True, sombra=True)

            texto_inc = "+{} HP   +{} ATK   +{} DEF   +{} SPD".format(
                incrementos["hp"], incrementos["atk"], incrementos["defe"], incrementos["spd"])
            desenhar_texto(tela, texto_inc, self.fontes.grande, VERDE,
                            (LARGURA_TELA // 2, 290), centro=True, sombra=True)

            stats = [
                "HP máx: {}".format(heroi.hp_max),
                "ATK: {}".format(heroi.atk),
                "DEF: {}".format(heroi.defe),
                "SPD: {}".format(heroi.spd),
            ]
            yy = 350
            for s in stats:
                desenhar_texto(tela, s, self.fontes.normal, BRANCO,
                                (LARGURA_TELA // 2, yy), centro=True)
                yy += 30

            botao = Botao(self._rect_continuar_evolucao(), "Próxima rodada",
                           cor=(70, 150, 90), cor_hover=(90, 190, 110))
            botao.desenhar(tela, self.fontes.grande, pygame.mouse.get_pos())

    def clique_evolucao(self, pos):
        if self.evolucao_resultado is None:
            for i, heroi in enumerate(self.party):
                rect = self._rect_card_evolucao(i)
                if rect.collidepoint(pos):
                    incrementos = aplicar_evolucao_personagem(heroi, self.bonus[heroi.chave])
                    self.evolucao_resultado = (heroi.chave, incrementos)
                    return
        else:
            if self._rect_continuar_evolucao().collidepoint(pos):
                self.rodada += 1
                self.preparar_nova_batalha()

    # ------------------------------------------------------------------
    # TELA: GAME OVER
    # ------------------------------------------------------------------
    def _rect_botao_gameover(self, indice):
        w, h = 280, 60
        x = LARGURA_TELA // 2 - w - 15 if indice == 0 else LARGURA_TELA // 2 + 15
        y = ALTURA_TELA - 130
        return pygame.Rect(x, y, w, h)

    def desenhar_gameover(self, tela):
        if self.batalha is not None:
            fundo = imagem_cobertura(self.batalha.cenario["imagem"], (LARGURA_TELA, ALTURA_TELA))
            tela.blit(fundo, (0, 0))
        else:
            tela.fill((20, 10, 10))
        overlay = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
        overlay.fill((20, 0, 0, 190))
        tela.blit(overlay, (0, 0))

        desenhar_texto(tela, "FIM DE JOGO", self.fontes.titulo, VERMELHO,
                        (LARGURA_TELA // 2, 160), centro=True, sombra=True)
        desenhar_texto(tela, "Sua party caiu na Rodada {}".format(self.rodada),
                        self.fontes.subtitulo, BRANCO,
                        (LARGURA_TELA // 2, 230), centro=True, sombra=True)

        yy = 300
        desenhar_texto(tela, "Níveis finais da party:", self.fontes.normal, AMARELO,
                        (LARGURA_TELA // 2, yy), centro=True)
        yy += 40
        for heroi in self.party:
            nivel = self.bonus.get(heroi.chave, {}).get("nivel", 1)
            desenhar_texto(tela, "{} - Nível {}".format(heroi.nome, nivel),
                            self.fontes.normal, CINZA_CLARO,
                            (LARGURA_TELA // 2, yy), centro=True)
            yy += 30

        botao1 = Botao(self._rect_botao_gameover(0), "Nova party",
                        cor=(70, 110, 150), cor_hover=(95, 145, 195))
        botao2 = Botao(self._rect_botao_gameover(1), "Menu principal",
                        cor=(110, 70, 70), cor_hover=(150, 95, 95))
        botao1.desenhar(tela, self.fontes.grande, pygame.mouse.get_pos())
        botao2.desenhar(tela, self.fontes.grande, pygame.mouse.get_pos())

    def clique_gameover(self, pos):
        if self._rect_botao_gameover(0).collidepoint(pos):
            self.reiniciar_jogo()
            self.ir_para_selecao()
        elif self._rect_botao_gameover(1).collidepoint(pos):
            self.reiniciar_jogo()

    # ------------------------------------------------------------------
    # DESENHO PRINCIPAL
    # ------------------------------------------------------------------
    def desenhar(self, tela):
        if self.estado == "menu":
            self.desenhar_menu(tela)
        elif self.estado == "selecao":
            self.desenhar_selecao(tela)
        elif self.estado == "transicao":
            self.desenhar_transicao(tela)
        elif self.estado == "batalha":
            self.desenhar_batalha(tela)
        elif self.estado == "evolucao":
            self.desenhar_evolucao(tela)
        elif self.estado == "gameover":
            self.desenhar_gameover(tela)


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Batalha das Divas - Edição Pernambuco")
    relogio = pygame.time.Clock()
    fontes = Fontes()
    jogo = Jogo(fontes)

    rodando = True
    while rodando:
        dt = relogio.tick(FPS) / 1000.0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                rodando = False
            else:
                jogo.processar_evento(evento)

        jogo.atualizar(dt)
        jogo.desenhar(tela)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
