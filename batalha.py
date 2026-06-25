"""
Motor de batalha por turnos. a interface apenas chama os métodos públicos desta classe e 
lê `self.log` para mostrar mensagens na tela.
"""

import random

import pygame

from entidades import gerar_inimigos, calcular_dano, criar_boss
from dados import CENARIOS, boss_da_rodada

# ---------------------------------------------------------------------------
# Utilitário de som
# ---------------------------------------------------------------------------
_cache_sons = {}


def _tocar_som(caminho):
    """Toca um arquivo de som sem bloquear; usa cache para evitar recarregamentos."""
    if not caminho:
        return
    try:
        if caminho not in _cache_sons:
            _cache_sons[caminho] = pygame.mixer.Sound(caminho)
        _cache_sons[caminho].play()
    except Exception:
        pass  # sem som não interrompe o jogo


class Batalha:
    def __init__(self, party, rodada):
        self.party = party
        self.rodada = rodada

        # restaura HP/status de todos os heróis para a nova batalha
        for heroi in self.party:
            heroi.reiniciar_para_nova_batalha()

        # verifica se é rodada de boss
        dados_boss = boss_da_rodada(rodada)
        self.eh_rodada_boss = dados_boss is not None

        if self.eh_rodada_boss:
            fator = 1.0 + (rodada // 5 - 1) * 0.20  # +20% a cada ciclo de bosses
            boss = criar_boss(dados_boss, fator_escala=fator)
            self.faccao = {
                "titulo": "BOSS: {}".format(boss.nome),
                "imagem": boss.imagem,
            }
            self.inimigos = [boss]
            self.dados_boss = dados_boss
        else:
            self.faccao, self.inimigos = gerar_inimigos(rodada)
            self.dados_boss = None

        self.cenario = random.choice(CENARIOS)

        self.log = []
        self.terminada = False
        self.vitoria = False

        self.ordem = []
        self.turno_idx = -1

        self._nova_rodada_interna()
        self.avancar_turno()

    def todos_combatentes(self):
        return self.party + self.inimigos

    def _nova_rodada_interna(self):
        vivos = [c for c in self.todos_combatentes() if c.vivo]
        # ordena por velocidade efetiva (decrescente); pequeno
        # desempate aleatório para não ficar sempre na mesma ordem
        self.ordem = sorted(vivos, key=lambda c: (c.spd_efetivo(), random.random()),
                             reverse=True)
        self.turno_idx = -1

    def _checar_fim(self):
        if all(not i.vivo for i in self.inimigos):
            self.terminada = True
            self.vitoria = True
            return True
        if all(not p.vivo for p in self.party):
            self.terminada = True
            self.vitoria = False
            return True
        return False

    def aguardando_jogador(self):
        if self.terminada:
            return None
        if self.turno_idx < 0 or self.turno_idx >= len(self.ordem):
            return None
        atual = self.ordem[self.turno_idx]
        if atual.eh_jogador and atual.vivo:
            return atual
        return None

    def inimigos_vivos(self):
        return [i for i in self.inimigos if i.vivo]

    def party_vivos(self):
        return [p for p in self.party if p.vivo]

    def avancar_turno(self):
        self.turno_idx += 1

        seguranca = 0
        while True:
            seguranca += 1
            if seguranca > 500:
                # válvula de segurança contra loops infinitos por bug
                return

            if self._checar_fim():
                return

            if self.turno_idx >= len(self.ordem):
                self._nova_rodada_interna()
                self.turno_idx = 0
                if not self.ordem:
                    return

            atual = self.ordem[self.turno_idx]

            if not atual.vivo:
                self.turno_idx += 1
                continue

            # ---- veneno (no início do turno do combatente) ----
            dano_veneno = atual.tick_veneno()
            if dano_veneno > 0:
                self.log.append(
                    "{} sofre {} de dano por veneno!".format(atual.nome, dano_veneno))
                if not atual.vivo:
                    self.log.append("{} foi derrotado(a) pelo veneno!".format(atual.nome))
                    if self._checar_fim():
                        return
                    self.turno_idx += 1
                    continue

            # ---- paralisia (DIVAAAAA) ----
            if atual.paralisia_turnos > 0:
                atual.paralisia_turnos -= 1
                self.log.append("{} está paralisado(a) e não pode agir! ({} turno(s) restantes)".format(
                    atual.nome, atual.paralisia_turnos))
                self.turno_idx += 1
                continue

            if atual.carregando:
                self._liberar_carga(atual)
                if self._checar_fim():
                    return
                self.turno_idx += 1
                continue

            if atual.cooldown_especial > 0:
                atual.cooldown_especial -= 1
            if atual.buff_spd_turnos > 0:
                atual.buff_spd_turnos -= 1
            atual.defendendo = False

            if atual.eh_jogador:
                return  # espera ação do jogador

            # ---- turno automático do inimigo ----
            self._executar_turno_inimigo(atual)
            if self._checar_fim():
                return
            self.turno_idx += 1
            continue

    def usar_item(self, chave_item, dados_item, alvo=None):
        """Aplica o efeito de um item consumível. Retorna True se aplicado com sucesso."""
        efeito = dados_item["tipo_efeito"]

        if efeito == "cura":
            if alvo is None or not alvo.vivo:
                return False
            valor = int(alvo.hp_max * dados_item.get("cura_percent", 0.4))
            curado = alvo.curar(valor)
            if alvo.eh_jogador and getattr(alvo, "som_cura", None):
                _tocar_som(alvo.som_cura)
            self.log.append("🍰 Usou {} em {}: recuperou {} de HP!".format(
                dados_item["nome"], alvo.nome, curado))
            return True

        elif efeito == "antidoto":
            if alvo is None or not alvo.vivo:
                return False
            alvo.veneno_turnos = 0
            alvo.veneno_dano = 0
            alvo.paralisia_turnos = 0
            self.log.append("🍵 Usou {} em {}: veneno e paralisia removidos!".format(
                dados_item["nome"], alvo.nome))
            return True

        elif efeito == "reset_cooldown":
            if alvo is None or not alvo.vivo:
                return False
            alvo.cooldown_especial = 0
            self.log.append("⚡ Usou {} em {}: especial pronto para usar!".format(
                dados_item["nome"], alvo.nome))
            return True

        elif efeito == "dano_fixo":
            if alvo is None or not alvo.vivo:
                return False
            dano = dados_item.get("dano", 60)
            alvo.hp = max(0, alvo.hp - dano)
            if alvo.hp <= 0:
                alvo.vivo = False
                self.log.append("🥊 Usou {} em {}: {} de dano fixo! {} foi derrotado(a)!".format(
                    dados_item["nome"], alvo.nome, dano, alvo.nome))
            else:
                self.log.append("🥊 Usou {} em {}: {} de dano fixo!".format(
                    dados_item["nome"], alvo.nome, dano))
            self._checar_fim()
            return True

        elif efeito == "veneno":
            if alvo is None or not alvo.vivo:
                return False
            alvo.aplicar_veneno(dados_item.get("veneno_dano", 15),
                                 dados_item.get("veneno_turnos", 4))
            self.log.append("🌸 Usou {} em {}: envenenado(a) por {} turnos!".format(
                dados_item["nome"], alvo.nome, dados_item.get("veneno_turnos", 4)))
            return True

        elif efeito == "buff_spd_time":
            aliados_vivos = self.party_vivos()
            mult = dados_item.get("buff_mult", 1.5)
            turnos = dados_item.get("buff_turnos", 2)
            for aliado in aliados_vivos:
                aliado.buff_spd_turnos = turnos
                aliado.buff_spd_mult = mult
            self.log.append("🚤 Usou {}: todo o time ficou muito mais ágil por {} turnos!".format(
                dados_item["nome"], turnos))
            return True

        elif efeito == "escudo_time":
            aliados_vivos = self.party_vivos()
            percent = dados_item.get("escudo_percent", 0.30)
            partes = []
            for aliado in aliados_vivos:
                val = max(1, int(aliado.hp_max * percent))
                aliado.adicionar_escudo(val)
                partes.append("{} (+{})".format(aliado.nome, val))
            self.log.append("👑 Usou {}: escudos criados — {}!".format(
                dados_item["nome"], ", ".join(partes)))
            return True

        elif efeito == "cura_total":
            aliados_vivos = self.party_vivos()
            for aliado in aliados_vivos:
                aliado.curar(aliado.hp_max)
            self.log.append("✨ Usou {}: toda a party foi completamente curada!".format(
                dados_item["nome"]))
            return True

        elif efeito == "buff_permanente":
            if alvo is None or not alvo.vivo:
                return False
            alvo.atk  += dados_item.get("bonus_atk", 5)
            alvo.defe += dados_item.get("bonus_defe", 3)
            alvo.spd  += dados_item.get("bonus_spd", 2)
            self.log.append("🏆 Usou {} em {}: +{} ATK, +{} DEF, +{} SPD permanentes!".format(
                dados_item["nome"], alvo.nome,
                dados_item.get("bonus_atk", 5),
                dados_item.get("bonus_defe", 3),
                dados_item.get("bonus_spd", 2)))
            return True

        return False

    def executar_acao_jogador(self, tipo_acao, alvo=None):
        """tipo_acao: 'atacar' | 'especial' | 'defender'"""
        atual = self.aguardando_jogador()
        if atual is None:
            return

        if tipo_acao == "defender":
            atual.defendendo = True
            self.log.append("{} se prepara para defender!".format(atual.nome))
        elif tipo_acao == "atacar":
            efeito_basico = atual.ataque_basico.get("tipo_efeito", "dano")
            if efeito_basico == "escudo_time":
                # Clarice: ataque básico gera escudo + dano em inimigo aleatório
                if alvo is not None:
                    self._executar_ataque(atual, atual.ataque_basico, alvo)
                self._aplicar_escudo_time(atual, atual.ataque_basico.get("escudo_percent", 0.05))
            else:
                self._executar_ataque(atual, atual.ataque_basico, alvo)
        elif tipo_acao == "especial":
            self._executar_especial(atual, alvo)

        if self._checar_fim():
            return
        self.avancar_turno()

    # ------------------------------------------------------------------
    # execução de ações
    # ------------------------------------------------------------------
    def _executar_ataque(self, atacante, ataque, alvo):
        if alvo is None or not alvo.vivo:
            return 0

        golpes = ataque.get("golpes", 1)
        total = 0
        for i in range(golpes):
            if not alvo.vivo:
                break
            dano, mult = calcular_dano(atacante, alvo, ataque)
            recebido = alvo.receber_dano(dano)
            total += recebido

            # som de dano do herói (apenas se recebeu dano real)
            if recebido > 0 and alvo.eh_jogador and getattr(alvo, "som_dano", None):
                _tocar_som(alvo.som_dano)

            sufixo = ""
            if mult > 1.0:
                sufixo = " Efetivo!"
            elif mult < 1.0:
                sufixo = " Pouco eficaz..."

            if golpes > 1:
                self.log.append("{} usa {} (golpe {}/{}) em {}: {} de dano!{}".format(
                    atacante.nome, ataque["nome"], i + 1, golpes, alvo.nome, recebido, sufixo))
            else:
                self.log.append("{} usa {} em {}: {} de dano!{}".format(
                    atacante.nome, ataque["nome"], alvo.nome, recebido, sufixo))

            if not alvo.vivo:
                self.log.append("{} foi derrotado(a)!".format(alvo.nome))
                break
        return total

    def _executar_especial(self, atacante, alvo):
        especial = atacante.especial
        if especial is None:
            return
        efeito = especial.get("tipo_efeito", "dano")

        if efeito == "cura":
            if alvo is None or not alvo.vivo:
                alvo = atacante
            valor = int(alvo.hp_max * especial.get("cura_percent", 0.3))
            curado = alvo.curar(valor)
            # som de cura do herói alvo
            if alvo.eh_jogador and getattr(alvo, "som_cura", None):
                _tocar_som(alvo.som_cura)
            self.log.append("{} usa {} e recupera {} de HP de {}!".format(
                atacante.nome, especial["nome"], curado, alvo.nome))
            atacante.cooldown_especial = especial["cooldown"]

        elif efeito == "dano_todos":
            # Pabllo Vittar: atinge todos os inimigos simultaneamente
            oponentes = self.inimigos if atacante.eh_jogador else self.party
            alvos_vivos = [o for o in oponentes if o.vivo]
            if not alvos_vivos:
                return
            som_especial = especial.get("som_especial")
            if som_especial:
                _tocar_som(som_especial)
            self.log.append("{} usa {} em TODOS os inimigos!".format(
                atacante.nome, especial["nome"]))
            for alvo_i in alvos_vivos:
                self._executar_ataque(atacante, especial, alvo_i)
            atacante.cooldown_especial = especial["cooldown"]

        elif efeito == "paralisar":
            # Gloria Groove: causa dano e paralisa o alvo
            if alvo is None or not alvo.vivo:
                return
            self._executar_ataque(atacante, especial, alvo)
            if alvo.vivo and not alvo.eh_jogador:
                turnos = especial.get("paralisia_turnos", 1)
                alvo.aplicar_paralisia(turnos)
                self.log.append("{} está PARALISADO(A) pelo efeito DIVAAAAA! 😍".format(alvo.nome))
            atacante.cooldown_especial = especial["cooldown"]

        elif efeito == "escudo_time":
            # Clarice Falcão: cria escudo para todo o time aliado
            aliados = self.party if atacante.eh_jogador else self.inimigos
            aliados_vivos = [a for a in aliados if a.vivo]
            percent = especial.get("escudo_percent", 0.05)
            nomes_com_escudo = []
            for aliado in aliados_vivos:
                valor_escudo = max(1, int(aliado.hp_max * percent))
                aliado.adicionar_escudo(valor_escudo)
                nomes_com_escudo.append("{} (+{})".format(aliado.nome, valor_escudo))
            self.log.append("{} usa {} — Escudos criados: {}!".format(
                atacante.nome, especial["nome"], ", ".join(nomes_com_escudo)))
            if "cooldown" in especial:
                atacante.cooldown_especial = especial["cooldown"]

        elif efeito == "escudo_proprio":
            # Inimigos avançados: cria escudo para si mesmo
            percent = especial.get("escudo_percent", 0.15)
            valor_escudo = max(1, int(atacante.hp_max * percent))
            atacante.adicionar_escudo(valor_escudo)
            self.log.append("{} usa {} e ganha um escudo de {}!".format(
                atacante.nome, especial["nome"], valor_escudo))
            atacante.cooldown_especial = especial["cooldown"]

        elif efeito == "carga":
            atacante.carregando = True
            atacante.alvo_carga = alvo
            self.log.append("{} começa a se preparar para {}...".format(
                atacante.nome, especial["nome"]))

        elif efeito == "buff_spd":
            self._executar_ataque(atacante, especial, alvo)
            atacante.buff_spd_turnos = especial.get("buff_turnos", 2)
            atacante.buff_spd_mult = especial.get("buff_mult", 1.3)
            self.log.append("{} fica muito mais ágil!".format(atacante.nome))
            atacante.cooldown_especial = especial["cooldown"]

        elif efeito == "veneno":
            self._executar_ataque(atacante, especial, alvo)
            if alvo is not None and alvo.vivo:
                alvo.aplicar_veneno(especial.get("veneno_dano", 5),
                                     especial.get("veneno_turnos", 3))
                self.log.append("{} está envenenado(a)!".format(alvo.nome))
            atacante.cooldown_especial = especial["cooldown"]

        else: 
            self._executar_ataque(atacante, especial, alvo)
            atacante.cooldown_especial = especial["cooldown"]

    def _liberar_carga(self, atacante):
        especial = atacante.especial
        alvo = atacante.alvo_carga

        if alvo is None or not alvo.vivo:
            oponentes = self.inimigos if atacante.eh_jogador else self.party
            vivos = [o for o in oponentes if o.vivo]
            if not vivos:
                atacante.carregando = False
                atacante.alvo_carga = None
                return
            alvo = random.choice(vivos)

        self.log.append("{} libera {}!!!".format(atacante.nome, especial["nome"]))
        self._executar_ataque(atacante, especial, alvo)
        atacante.carregando = False
        atacante.alvo_carga = None
        atacante.cooldown_especial = especial["cooldown"]

    def _aplicar_escudo_time(self, atacante, percent):
        """Aplica escudo a todos os aliados vivos do atacante."""
        aliados = self.party if atacante.eh_jogador else self.inimigos
        aliados_vivos = [a for a in aliados if a.vivo]
        partes = []
        for aliado in aliados_vivos:
            valor = max(1, int(aliado.hp_max * percent))
            aliado.adicionar_escudo(valor)
            partes.append("{} (+{})".format(aliado.nome, valor))
        if partes:
            self.log.append("{} cria mini-escudos para o time: {}!".format(
                atacante.nome, ", ".join(partes)))

    def _executar_turno_inimigo(self, inimigo):
        alvos_possiveis = self.party_vivos()
        if not alvos_possiveis:
            return
        alvo = random.choice(alvos_possiveis)

        usar_especial = (inimigo.especial is not None and
                         inimigo.cooldown_especial == 0 and
                         random.random() < 0.5)

        if usar_especial:
            self._executar_especial(inimigo, alvo)
        else:
            self._executar_ataque(inimigo, inimigo.ataque_basico, alvo)
