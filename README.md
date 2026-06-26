# Batalha das Divas - Edição Pernambuco 🎤🔥

Jogo de batalha por turnos feito em **Python + Pygame**, com tema musical
brasileiro. Monte uma party de 4 divas, enfrente inimigos gerados
aleatoriamente em um **loop infinito** cada vez mais difícil, evolua
seus personagens entre as batalhas e enfrente **bosses épicos** a cada
5 rodadas.

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
├── main.py           # tela, loop principal, eventos (pygame)
├── interface.py      # funções de desenho, fontes, botões (pygame)
├── batalha.py        # motor de batalha por turnos (sem pygame)
├── entidades.py      # personagens, inimigos, bosses, cálculo de dano
├── dados.py          # tabelas de dados: stats, golpes, cenários, tipos, itens, bosses
└── assets/
    ├── personagens/  # retratos das 9 divas jogáveis
    ├── cenarios/     # 5 cenários de Pernambuco (sorteados a cada batalha)
    ├── inimigos/     # 5 "banners" de facções inimigas
    ├── bosses/       # retratos dos 5 bosses
    ├── itens/        # imagens dos 9 itens consumíveis
    └── sons/         # efeitos sonoros de Pabllo Vittar
```

Mantenha a pasta `assets/` junto dos arquivos `.py` — os caminhos são
relativos à pasta do jogo.

### Nomes esperados dos arquivos em `assets/`

**personagens/**
`liniker.png`, `anavitoria.png`, `anitta.png`, `linn.png`, `luisa.png`,
`urias.png`, `pabllo.png`, `gloria_groove.png`, `clarice_falcao.png`

**bosses/**
`neiff.png`, `oruam.png`, `belo.png`, `livinho.png`, `paiva.png`

**itens/**
`torta_amora.png`, `cha.png`, `pocao_rajadao.png`, `luva_ko.png`,
`puzzy.png`, `barquinho.png`, `coroa.png`, `pote_de_ouro.png`, `grammy.png`

**sons/**
`Pabllo_Especial.wav`, `Pabllo_dano.mp3`, `Pabllo_Cura.wav`

---

## 3. Como jogar

1. **Tela inicial** → clique ou aperte ENTER.
2. **Seleção da party** → clique em 4 das 9 divas disponíveis (clique de
   novo para desmarcar) e depois em **"Confirmar party"**. Use a
   **roda do mouse** ou as **setas ↑↓** para rolar a lista, ou arraste
   a scrollbar lateral.
3. **Transição** → mostra o cenário e a facção inimiga (ou o **boss**, em
   rodadas múltiplas de 5). Clique para começar a lutar.
4. **Batalha**:
   - A ordem dos turnos é definida pela **Velocidade (SPD)** de cada
     combatente (recalculada a cada rodada de turnos).
   - No seu turno, escolha **Atacar**, o **golpe especial** (se não
     estiver em cooldown) ou **Defender** (reduz o próximo dano sofrido
     à metade).
   - Se a ação exigir um alvo, os alvos válidos ficam destacados — clique
     em um deles. Há um botão "Cancelar" para voltar ao menu de ações.
   - Use o botão **🎒 Itens** para abrir o inventário e consumir um item
     durante o seu turno (gasta a ação do turno).
   - As mensagens de batalha aparecem com efeito de revelação gradual no
     log central; clique em qualquer lugar para acelerar.
5. **Vitória** → você recebe um **item aleatório** como recompensa e
   depois escolhe 1 dos 4 personagens para **evoluir**
   (+14 HP máx, +3 ATK, +2 DEF, +2 SPD). Bosses garantem itens raros.
6. **Derrota** → tela de Game Over com o resumo final dos níveis da sua
   party. Você pode montar uma **nova party** (volta para a seleção) ou
   voltar ao **menu principal**.

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
| **Pabllo Vittar** | Performance | 110 | 18 | 13 | 16 | Especial **"K.O. Vittar"** atinge TODOS os inimigos de uma vez. Possui sons únicos para dano, cura e especial. |
| **Gloria Groove** | Vocal | 105 | 16 | 14 | 11 | Especial **"DIVAAAAA 😍"** causa dano e **paralisa** o inimigo por 1 turno. |
| **Clarice Falcão** | Letra | 90 | 13 | 10 | 13 | Cada ataque básico **"Fui Fácil"** gera escudo de 5% do HP para todos. Especial **"Redoma"** cria escudos de 20%. |
| **Liniker** | Vocal | 130 | 22 | 18 | 8 | Tanque vocal: alta defesa. Especial **"Zero"** carrega 1 turno e libera golpe devastador (x2.5). |
| **Anavitória** | Letra | 85 | 11 | 9 | 14 | Ataque básico **"Trevo (Tu)"** acerta 2 vezes. Especial **"Cuidar"** cura um aliado. |
| **Anitta** | Performance | 100 | 17 | 12 | 20 | Muito ágil. Especial **"Envolver"** causa dano e aumenta velocidade por 2 turnos. |
| **Linn da Quebrada** | Letra | 105 | 15 | 13 | 12 | Especial **"Pesadão"** é a maior cura do jogo para os aliados. |
| **Luísa Sonza** | Vocal | 95 | 12 | 11 | 13 | Especial **"Penhasco"** aplica **veneno** (dano contínuo por 3 turnos). |
| **Urias** | Performance | 65 | 23 | 7 | 22 | Maior ATK e SPD do elenco, porém fragilíssima. Especial **"Cilada"** (x1.9) com cooldown curto. |

Os nomes dos golpes são inspirados em músicas conhecidas de cada artista.

---

## 6. Status de batalha

Além de HP, cada combatente pode ter os seguintes estados ativos:

| Status | Descrição |
|--------|-----------|
| **Veneno** | Perde HP fixo no início de cada turno por X rodadas. |
| **🛡 Escudo** | Absorve dano antes do HP. Exibido como barra azul e badge nos cards. |
| **DIVAAAAA 😍** | Paralisia: pula o turno completamente. Aplicado pela Gloria Groove. |
| **Carregando** | Não age neste turno; libera golpe devastador no próximo. |
| **Ágil** | Velocidade aumentada por X turnos (buff_spd). |
| **Defendendo** | Reduz o próximo dano recebido à metade. |

---

## 7. Itens consumíveis 🎒

Itens são ganhos como recompensa ao vencer batalhas e usados durante o
seu turno na batalha (gasta a ação). Abra o inventário com o botão
**🎒 Itens** no painel central.

| Item | Efeito | Alvo | Estoque máx |
|------|--------|------|-------------|
| 🍰 **Torta de Amora** | Cura 40% do HP máx | Aliado | 3 |
| 🍵 **Chá Revigorante** | Remove veneno e paralisia | Aliado | 3 |
| ⚡ **Poção Rajadão** | Zera o cooldown do especial | Aliado | 2 |
| 🥊 **Luva K.O.** | 60 de dano fixo (ignora defesa) | Inimigo | 2 |
| 🌸 **Puzzy** | Envenena por 4 turnos (15/turno) | Inimigo | 2 |
| 🚤 **Barquinho de Papel** | +50% velocidade para todo o time por 2 turnos | Time | 2 |
| 👑 **Coroa** | Escudo de 30% do HP máx para todo o time | Time | 2 |
| ✨ **Pote de Ouro** | Cura 100% do HP de toda a party | Time | 1 |
| 🏆 **Grammy** | +5 ATK, +3 DEF, +2 SPD **permanentes** num aliado | Aliado | 1 |

Itens comuns saem na maioria das vitórias; **Pote de Ouro** e **Grammy**
são raros e aparecem com mais frequência ao derrotar bosses.

---

## 8. Inimigos, bosses e cenários

### Facções inimigas
A cada batalha normal, uma das **5 facções** é sorteada (inspiradas em
capas de funk/piseiro/sertanejo do top 50 Brasil do Spotify):
*Diário de um Cafajeste*, *Famoso Imã*, *Relíquia do ZT*,
*Peão Todo Tatuado* e *Eu Te Seguro*.

Cada inimigo recebe **tipo aleatório**, atributos e dois golpes gerados
proceduralmente. A partir da **rodada 5**, inimigos podem aparecer com
**escudo próprio** no especial (chance crescente). A quantidade de
inimigos aumenta de 1 até 4 conforme as rodadas avançam, e os atributos
escalam ~14% por rodada.

### Bosses ⚠
A cada **múltiplo de 5 rodadas** um boss substitui a batalha normal.
A tela de transição fica vermelha pulsante e exibe a fala de entrada do
boss. Derrotá-lo garante um **item raro**.

| Rodada | Boss | Tipo | Destaque |
|--------|------|------|----------|
| 5 | **Neiff** | Performance | Especial atinge todos os heróis |
| 10 | **Oruam** | Letra | Veneno pesado (18 dano × 3 turnos) |
| 15 | **Belo** | Vocal | Alta DEF; especial gera 30% de escudo próprio |
| 20 | **MC Livinho** | Performance | Rapidíssimo; especial paralisa um herói |
| 25 | **Paiva** | Letra | O mais tanque (500 HP); especial de carga x3.0 |

O ciclo reinicia a partir da rodada 30 com +20% nos atributos a cada volta.

### Cenários
5 cenários de Pernambuco são sorteados como fundo:
Auditório da UFRPE, Pátio de São Pedro (Recife Antigo), Palco do
Lollapalooza Brasil, Forte das Cinco Pontas (Olinda) e Mesas do Recife Antigo.

---

## 9. Novas adições Release 2.0

- Sistema de Itens
- Novos personagens (Pabllo Vittar, Gloria Groove e Clarice falcão)
- Sistema de bosses (Neiff, Oruam, Belo, Mc Paiva e Mc Livinho)
- Implementação de Sons para Pabllo
- Novos efeitos (Escudo e Paralisia)

---

## Relatório de Desenvolvimento

[Link](https://docs.google.com/document/d/12vT5S_2EGP5LN3siTg2fU08G1UlTTrqcxUOaLQGH_h4/edit?usp=sharing)
