"""
Motor de batalha por turnos. a interface apenas chama os métodos públicos desta classe e 
lê `self.log` para mostrar mensagens na tela.
"""

import random

from entidades import gerar_inimigos, calcular_dano
from dados import CENARIOS


class Batalha:
    def __init__(self, party, rodada):
        self.party = party
        self.rodada = rodada

        # restaura HP/status de todos os heróis para a nova batalha
        for heroi in self.party:
            heroi.reiniciar_para_nova_batalha()

        self.faccao, self.inimigos = gerar_inimigos(rodada)
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

    def executar_acao_jogador(self, tipo_acao, alvo=None):
        """tipo_acao: 'atacar' | 'especial' | 'defender'"""
        atual = self.aguardando_jogador()
        if atual is None:
            return

        if tipo_acao == "defender":
            atual.defendendo = True
            self.log.append("{} se prepara para defender!".format(atual.nome))
        elif tipo_acao == "atacar":
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
            self.log.append("{} usa {} e recupera {} de HP de {}!".format(
                atacante.nome, especial["nome"], curado, alvo.nome))
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
