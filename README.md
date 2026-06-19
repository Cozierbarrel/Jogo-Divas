# Batalha das Divas - Edição Pernambuco 🎤🔥

Jogo de batalha por turnos feito em **Python + Pygame**, com tema musical
brasileiro. Monte uma party de 4 divas, enfrente inimigos gerados
aleatoriamente em um **loop infinito** cada vez mais difícil, e evolua
seus personagens entre as batalhas.

---

## 1. Como instalar e executar

Pré-requisito: **Python 3.8+**

```bash
pip install pygame
python3 main.py
```

O jogo é controlado **inteiramente com o mouse** (clique esquerdo).
Pressione `ESC` em qualquer momento para sair.

---

## 2. Estrutura dos arquivos

```
jogo_divas/
├── main.py          # tela, loop principal, eventos (pygame)
├── interface.py      # funções de desenho, fontes, botões (pygame)
├── batalha.py         # motor de batalha por turnos (sem pygame)
├── entidades.py       # personagens, inimigos, cálculo de dano (sem pygame)
├── dados.py           # tabelas de dados: stats, golpes, cenários, tipos
└── assets/
    ├── personagens/   # retratos das 6 divas jogáveis
    ├── cenarios/      # 5 cenários de Pernambuco (sorteados a cada batalha)
    └── inimigos/      # 5 "banners" de facções inimigas (capas de funk/sertanejo)
```

Mantenha a pasta `assets/` junto dos arquivos `.py` — os caminhos são
relativos à pasta do jogo.

---

## 3. Como jogar

1. **Tela inicial** → clique ou aperte ENTER.
2. **Seleção da party** → clique em 4 das 6 divas disponíveis (clique de
   novo para desmarcar) e depois em **"Confirmar party"**.
3. **Transição** → mostra o cenário e a facção inimiga da rodada. Clique
   para começar a lutar (ou aguarde ~2s).
4. **Batalha**:
   - A ordem dos turnos é definida pela **Velocidade (SPD)** de cada
     combatente (recalculada a cada rodada de turnos).
   - No seu turno, escolha **Atacar**, o **golpe especial** (se não
     estiver em cooldown) ou **Defender** (reduz o próximo dano sofrido
     à metade).
   - Se a ação exigir um alvo (ataque, golpe especial ou cura), os
     alvos válidos ficam destacados em laranja pulsante — clique em um
     deles. Há um botão "Cancelar" para voltar ao menu de ações.
   - As mensagens de batalha aparecem com efeito de revelação gradual no
     log central; clique em qualquer lugar para acelerar.
5. **Vitória** → escolha 1 dos 4 personagens para **evoluir**
   (+14 HP máx, +3 ATK, +2 DEF, +2 SPD) e siga para a próxima rodada.
   Os inimigos da próxima rodada serão mais fortes e podem vir em maior
   número (até 4).
6. **Derrota** → tela de Game Over com o resumo final dos níveis da sua
   party. Você pode montar uma **nova party** (volta para a seleção) ou
   voltar ao **menu principal**.
   
![Tela de Luta](https://github.com/Cozierbarrel/Jogo-Divas/blob/main/__pycache__/Tela%20Luta.png)

Imagem da Tela de Luta
---

## 4. Sistema de tipos (pedra-papel-tesoura)

| Ataque ↓ / Defesa →  | Letra | Vocal | Performance |
|-----------------------|-------|-------|-------------|
| **Letra**             | 1.0x  | **1.5x** | 0.7x     |
| **Vocal**             | 0.7x  | 1.0x  | **1.5x**    |
| **Performance**       | **1.5x** | 0.7x | 1.0x      |

- **Letra** vence **Vocal**
- **Vocal** vence **Performance**
- **Performance** vence **Letra**

O multiplicador é aplicado sobre o dano calculado a partir do `ATK` do
atacante, do multiplicador do golpe e da `DEF` do defensor.

---

## 5. Personagens jogáveis

| Diva | Tipo | HP | ATK | DEF | SPD | Perfil |
|------|------|----|-----|-----|-----|--------|
| **Liniker** | Vocal | 130 | 22 | 18 | 8 | Tanque vocal: alta defesa. Especial **"Zero"** carrega por 1 turno e libera um golpe devastador (x2.5) no turno seguinte. |
| **Anavitória** | Letra | 85 | 11 | 9 | 14 | Frágil, mas o ataque básico **"Trevo (Tu)"** acerta 2 vezes. Especial **"Cuidar"** cura um aliado. |
| **Anitta** | Performance | 100 | 17 | 12 | 20 | Dano consistente e muito ágil. Especial **"Envolver"** causa dano e aumenta sua própria velocidade por 2 turnos. |
| **Linn da Quebrada** | Letra | 105 | 15 | 13 | 12 | Dano equilibrado. Especial **"Pesadão"** cura um aliado (a maior cura do jogo). |
| **Luísa Sonza** | Vocal | 95 | 12 | 11 | 13 | Dano baixo, mas o especial **"Penhasco"** aplica **veneno** (dano contínuo por 3 turnos). |
| **Urias** | Performance | 65 | 23 | 7 | 22 | Maior ATK e SPD do jogo, porém o menor HP. Especial **"Cilada"** (x1.9) com cooldown curto. |

![Personagens](https://github.com/Cozierbarrel/Jogo-Divas/blob/main/__pycache__/Tela%20Personagens.png)

Os nomes dos golpes ("Zero", "Trevo (Tu)", "Envolver", "Bixa Travesty",
"Penhasco", "Single" etc.) são inspirados em músicas conhecidas de cada
artista.


---

## 6. Inimigos e cenários

- A cada batalha, uma das **5 facções inimigas** é sorteada (inspiradas
  em capas de funk/piseiro/sertanejo: *Diário de um Cafajeste*, *Famoso
  Imã*, *Relíquia do ZT*, *Peão Todo Tatuado*, *Eu Te Seguro*), que estão no topo do top 50 Brasil do Sporify, trazendo
  nomes de MCs/DJs/peões para os inimigos.
- Cada inimigo recebe **tipo aleatório**, atributos e **dois golpes
  gerados proceduralmente** (nomes combinando palavras como "Paredão",
  "Berro", "Trovão", "180 BPM" etc.). Golpes especiais de inimigos podem
  vir com **veneno embutido**, com chance crescente conforme a rodada.
- A cada rodada:
  - A quantidade de inimigos aumenta (1 → até 4).
  - Os atributos dos inimigos escalam em ~14% por rodada.
- 5 **cenários de Pernambuco** são sorteados como fundo de cada batalha:
  Auditório da UFRPE, Pátio de São Pedro (Recife Antigo), Palco do
  Lollapalooza Brasil, Forte das Cinco Pontas (Olinda) e as mesas do
  Recife Antigo.

---

## 7. Dicas de balanceamento

- Cuidar do tipo do seu time em relação ao tipo dos inimigos faz
  grande diferença (1.5x ou 0.7x de dano).
- **Defender** é útil para sobreviver a rodadas com vários inimigos
  enquanto aguarda cooldowns.
- Priorize evoluir personagens com pouco HP (como **Urias**) para que
  não sejam derrotados rapidamente nas rodadas mais avançadas.
- O veneno aplicado por **Luísa Sonza** é ótimo contra inimigos com
  muito HP, pois o dano continua mesmo se você atacar outro alvo.

Bom jogo e... que vença a melhor diva! 🏆

## Relatório de Desenvolvimento

[Link](https://docs.google.com/document/d/12vT5S_2EGP5LN3siTg2fU08G1UlTTrqcxUOaLQGH_h4/edit?usp=sharing)
