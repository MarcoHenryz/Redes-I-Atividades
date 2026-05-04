# Design: Slides — Computação Autônoma

**Data:** 2026-04-28  
**Autores:** Marco Antônio Cottorello Henry, Murilo de Souza Neves  
**Instituição:** UEL — Universidade Estadual de Londrina  
**Apresentação:** 20–30 minutos (~26 slides)

---

## Contexto

Geração de slides Beamer (LaTeX) para apresentação do trabalho "Computação Autônoma".  
Fonte: arquivos `.tex` em `texto/` + imagem `mape-k.png`.  
Template base: `slides/slides.tex` (tema Szeged).

**Restrições:**

- Tema Beamer: `Szeged` (manter)
- Idioma: Português
- Incluir imagens do paper: `mape-k.png` (figura MAPE-K) e diagrama TikZ de propriedades
- Slides com texto explicativo suficiente para guiar a fala (não apenas títulos de bullets)
- Auto-section ToC habilitado via `\AtBeginSection[]`
- Output: `slides/slides.tex` (substituir conteúdo atual)

---

## Estrutura de Slides

### Slide 1 — Capa (titlepage)

- Título: **COMPUTAÇÃO AUTÔNOMA**
- Autores: Marco Antônio Cottorello Henry, Murilo de Souza Neves
- Instituição: Universidade Estadual de Londrina
- Ano: 2026

---

### Seção 1: Introdução

_Auto-ToC gerado pelo Beamer antes desta seção._

**Slide 2 — A Crise da Complexidade**

- Sistemas modernos: distribuídos, heterogêneos, em nuvem
- TCO: até 80% em manutenção/administração (Sterritt, 2005)
- Erros humanos: principal causa de falhas em data centers
- Frase de apoio: "A complexidade ultrapassa a capacidade cognitiva humana"

**Slide 3 — A Resposta: IBM (2001)**

- Manifesto IBM: _"It's Time Systems Take Care of Themselves"_
- Analogia ao Sistema Nervoso Autônomo (SNA): funções vitais sem mente consciente
- Objetivo: sistemas gerenciam a si mesmos por diretrizes de alto nível
- Administrador define **o quê**, sistema decide **como**

**Slide 4 — Visão Geral do Paradigma**

- 4 propriedades Self-X: auto-config, auto-cura, auto-otimiz., auto-proteção
- Ciclo de controle: MAPE-K (Monitor → Analyse → Plan → Execute + Knowledge)
- "Estas são as bases do paradigma — detalhadas nas próximas seções"

---

### Seção 2: Histórico e Desenvolvimento

_Auto-ToC gerado pelo Beamer antes desta seção._

**Slide 5 — Projetos Precursores**

- Layout 2 colunas ou tabela resumida:
  - SAS (DARPA, 1997): roteamento ad-hoc adaptativo, 10.000 nós
  - DASADA (DARPA, 2000): probes/gauges, precursor do MAPE-K
  - IBM Manifesto (2001): formalização do termo e Self-X
  - SPS (DARPA, 2003): sistemas auto-regenerativos resistentes a ataques
  - ANTS (NASA, 2005): enxame autônomo para exploração espacial
- Texto de apoio: "Convergência independente para os mesmos princípios de auto-gestão"

**Slide 6 — Propriedades Self-X**

- Animação: cada propriedade aparece por vez (`<1->` etc.)
- **Auto-configuração:** sistema se instala e ajusta automaticamente; admin define metas, não passos
- **Auto-cura:** detecta, diagnostica e corrige falhas de HW/SW; tolera e reage a falhas
- **Auto-otimização:** busca contínua de eficiência; redistribui carga proativamente
- **Auto-proteção:** defende contra ataques e usuários que fazem mudanças prejudiciais; proativa e reativa

**Slide 7 — O Laço de Controle MAPE-K**

- Layout 2 colunas: imagem `mape-k.png` (esquerda) + bullets (direita)
- **Monitor:** coleta dados via sensores/probes (passivo e ativo)
- **Analyse:** analisa estado vs. metas; identifica discrepâncias
- **Plan:** define ações corretivas com base nas políticas
- **Execute:** aplica mudanças via efetores (granularidade grossa ou fina)
- **Knowledge:** base que suporta todas as fases — regras, histórico, modelos

**Slide 8 — Planejamento e Base de Conhecimento**

- Layout 2 colunas:
  - _Esquerda — Tipos de Políticas:_
    - ECA (Evento-Condição-Ação): simples, diretas, risco de conflito
    - Objetivo: define estado desejado, sistema planeja como atingir
    - Função de Utilidade: valor numérico por estado; otimiza sob incerteza
  - _Direita — Base de Conhecimento:_
    - Aprendizado por Reforço: aprende por tentativa/erro, sem modelo explícito
    - Redes Bayesianas: decisão probabilística sob incerteza
    - Modelos Arquiteturais: verifica validade de mudanças antes de executar

---

### Seção 3: Aplicações

_Auto-ToC gerado pelo Beamer antes desta seção._

**Slide 9 — Aplicação Clássica: NASA ANTS**

- Layout 2 colunas:
  - _Contexto:_ 1.000 nanoespaçonaves, cinturão de asteróides, 60–70% perda esperada; atraso de comunicação Terra inviabiliza controle manual
  - _Self-X manifestadas:_
    - Auto-cura: sobreviventes redistribuem papéis automaticamente
    - Auto-configuração: cada nave determina posição e rota na frota
    - Auto-otimização: prioriza asteróides com base em dados coletados
    - Auto-proteção: evita colisões, gerencia consumo de energia
- Texto de apoio: "MAPE-K distribuído — cada nave executa ciclo local; comportamento global emergente"

**Slide 10 — Aplicação Clássica: IBM Project eLiza**

- Maior investimento individual da divisão de servidores IBM à época
- Linha eServer (zSeries, pSeries, iSeries, xSeries) como plataforma
- Auto-config: HW e middleware se reconfiguram na inicialização e em runtime
- Auto-otimização: IRD (Intelligent Resource Director) redistribui carga entre LPARs
- Auto-cura: System Automation for OS/390 — detecta falhas e aciona recuperação sem humano
- Auto-proteção: detecção de intrusão integrada ao SO
- Texto de apoio: "Provou que Self-X é viável em sistemas de missão crítica real"

**Slide 11 — Aplicação Moderna: Cloud Computing**

- Data centers: milhares de servidores, milhões de VMs/containers
- Auto-otimização: MAPE-K monitora CPU/memória/rede → auto-scaling sem humano
- Auto-cura: falha de nó → migração automática de VMs para servidores saudáveis
- Economia: consolida cargas em baixa demanda, desliga servidores ociosos
- Texto de apoio: "Decisões em milissegundos — escala humana impossível"

**Slide 12 — Aplicação Moderna: IoT e Sistemas Pervasivos**

- Desafio: heterogeneidade + volatilidade (Smart Cities, Smart Grids, hospitais)
- Auto-configuração: novos sensores descobrem vizinhos e registram serviços automaticamente (plug-and-play)
- Auto-proteção: IA detecta tráfego anômalo → quarentena automática de dispositivos comprometidos
- Texto de apoio: "Sem autonomia, custo de configurar milhões de dispositivos seria proibitivo"

---

### Seção 4: Estado da Arte

_Auto-ToC gerado pelo Beamer antes desta seção._

**Slide 13 — Avanços: IA e Cloud-Native**

- Transição: automação reativa (regras estáticas) → autonomia preditiva (ML)
- Bloco 1 — **AIOps:** ingere terabytes de métricas/logs em tempo real; modelos preditivos antecipam falhas horas antes; sistema age preventivamente
- Bloco 2 — **Kubernetes + Service Mesh:** auto-config via descoberta de serviços; auto-cura em nível de rede (redireciona tráfego em ms quando container falha)

**Slide 14 — Desafios em Aberto**

- Items numerados:
  1. **Verificação Formal e Estabilidade:** ML é "caixa-preta"; difícil provar corretude; pesquisa usa autômatos, Redes de Petri, cálculo de processos
  2. **Interoperabilidade:** soluções atuais em silos; falta protocolo padrão entre gerentes autônomos de fornecedores distintos
  3. **Tradução de Políticas de Alto Nível:** objetivos de negócio ("maximizar lucro") ainda exigem engenheiro para traduzir em configurações de baixo nível
- Texto de apoio: "Fronteira: tornar autonomia não só inteligente, mas verificável, interpretável e interoperável"

---

### Seção 5: Conclusão

_Auto-ToC gerado pelo Beamer antes desta seção._

**Slide 15 — Conclusão**

- Ponto de inflexão: escalabilidade inseparável da automação de gestão
- MAPE-K + Self-X: base madura para Cloud e IoT
- Autonomia reduz TCO e erro humano — viabilidade econômica comprovada
- Barreira: confiança + verificação formal ainda em aberto
- Tendência: convergência com métodos formais e ML interpretável
- Frase final: "De sistemas que 'fazem o que mandamos' para sistemas que 'fazem o que queremos'"

**Slide 16 — Referências e Agradecimentos**

- Principais referências (IBM 2001, Kephart 2003, Sterritt 2005, Lalanda 2013)
- "Obrigado!"

---

## Notas Técnicas

- Arquivo output: `slides/slides.tex` (substituir completamente)
- Copiar `mape-k.png` para `slides/` ou usar path relativo `../texto/mape-k.png`
- Diagrama TikZ de propriedades: recriar versão simplificada inline no slide (ou omitir se muito verboso)
- Pacotes necessários além do beamer: `tikz`, `booktabs` (tabela projetos), `graphicx`
- Encoding: UTF-8 com `\usepackage[utf8]{inputenc}`
- Usar `\usepackage[brazil]{babel}` para português
- `\AtBeginSection[]` mantido do template original
- Animações com `\item<N->` no slide Self-X
- Blocos com `\begin{block}{}`, `\begin{exampleblock}{}` no slide Estado da Arte

---

## Total de Slides

| Tipo             | Quantidade |
| ---------------- | ---------- |
| Capa             | 1          |
| Auto-section ToC | 5          |
| Conteúdo         | 15         |
| **Total**        | **~21**    |

Ritmo: ~1.4 min/slide para 30 min. Dentro da janela de 20–30 min.
