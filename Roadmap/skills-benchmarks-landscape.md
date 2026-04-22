# Benchmarks De Skills Em 2026

## TL;DR

Hoje existem poucos benchmarks que medem **skills** diretamente, e quase todos sao de 2026.

- Os tres mais importantes sao:
  - [SkillsBench](https://www.skillsbench.ai/)
  - [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401)
  - [How Well Do Agentic Skills Work in the Wild](https://arxiv.org/abs/2604.04323)
- O resto do ecossistema mede capacidades adjacentes: function calling, tool use, web agents, terminal agents, GUI agents e software engineering.
- Ainda **nao parece existir** um benchmark forte que combine:
  - descoberta de skill
  - qualidade da skill
  - composicao de multiplas skills
  - safety/trust/provenance
  - UX para usuarios nao tecnicos
  - comparacao cross-harness

Minha leitura: para o Freedom Skills, o caminho certo nao e esperar um benchmark pronto. E **compor o que ja existe** e construir a camada que falta.

## 1. Benchmarks Que Medem Skills Diretamente

| Benchmark | Status | O que mede | O que aprendi |
| --- | --- | --- | --- |
| [SkillsBench](https://www.skillsbench.ai/) / [paper](https://arxiv.org/abs/2602.12670) / [repo](https://github.com/benchflow-ai/skillsbench) | Fev 2026, ativo | Utilidade de skills em tarefas multi-dominio | E o benchmark mais importante hoje para skills em geral |
| [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401) / [repo](https://github.com/GeniusHTX/SWE-Skills-Bench) | Mar 2026 | Utilidade marginal de skills em software engineering real | Mostra que muita skill publica quase nao ajuda |
| [How Well Do Agentic Skills Work in the Wild](https://arxiv.org/abs/2604.04323) / [repo](https://github.com/UCSB-NLP-Chang/Skill-Usage) | Abr 2026 | Skill retrieval e uso em cenarios mais realistas | Mostra que o ganho de skill cai bastante quando a selecao deixa de ser idealizada |

### 1.1 SkillsBench

Fonte principal:
- [Paper no arXiv](https://arxiv.org/abs/2602.12670)
- [Site oficial](https://www.skillsbench.ai/)
- [Repo oficial](https://github.com/benchflow-ai/skillsbench)

Pontos centrais:
- O paper apresenta **86 tasks em 11 dominios**, com verificadores deterministicos.
- Cada task e avaliada em tres condicoes:
  - sem skills
  - com skills curadas
  - com skills auto-geradas
- O resultado principal do paper: skills curadas sobem a pass rate media em **+16.2 pontos percentuais**, mas o ganho varia muito por dominio.
- O mesmo paper diz que **skills auto-geradas nao trazem ganho medio**, o que e um sinal importante: o agente ainda nao e bom em escrever por conta propria a memoria procedural de que ele se beneficiaria depois.
- O paper tambem argumenta que skills focadas, com **2-3 modulos**, funcionam melhor do que documentacao ampla e enciclopedica.

Leitura pratica:
- Skills podem ajudar bastante.
- Mas a ajuda nao e uniforme.
- O formato da skill importa.
- "Mais contexto" nao e o mesmo que "melhor skill".

Observacao importante de versao:
- O [paper](https://arxiv.org/abs/2602.12670) fala em **86 tasks**.
- O [site oficial](https://www.skillsbench.ai/) hoje mostra leaderboard publica em **84 tasks**.
- O [repo](https://github.com/benchflow-ai/skillsbench) tambem fala de benchmark ativo e tarefas publicas, mas sem cravar o mesmo numero do abstract.

Minha inferencia:
- O benchmark ainda esta evoluindo e o numero de tasks publicas/ativas mudou entre paper, repo e leaderboard.
- Para qualquer comparacao seria obrigatorio registrar **data e versao**.

Snapshot util do site em 2026-04-22:
- `Codex + GPT-5.2`: **30.6% sem skills -> 44.7% com skills**
- `Claude Code + Opus 4.6`: **30.6% -> 44.5%**
- `Claude Code + Opus 4.5`: **22.0% -> 45.3%**
- `Gemini CLI + Gemini 3 Flash`: **31.3% -> 48.7%**

O ponto mais importante aqui nao e o ranking em si. E que o site ja esta se posicionando como benchmark de **agent + harness + model + skill**, nao so de modelo base.

### 1.2 SWE-Skills-Bench

Fonte principal:
- [Paper no arXiv](https://arxiv.org/abs/2603.15401)
- [Repo oficial](https://github.com/GeniusHTX/SWE-Skills-Bench)

Pontos centrais:
- Benchmark requirement-driven focado em software engineering real.
- O paper emparelha **49 skills publicas** com repositorios GitHub reais, fixados em commits especificos.
- O abstract reporta **~565 task instances em 6 subdominios**.
- A avaliacao e pareada:
  - com skill
  - sem skill
- O resultado principal e bem mais sobrio do que o hype de mercado:
  - **39 de 49** skills nao melhoram a pass rate
  - ganho medio de apenas **+1.2 pp**
  - so **7** skills especializadas produzem ganho relevante
  - **3** pioram o desempenho
  - overhead de tokens vai de economia modesta ate **+451%** sem melhoria correspondente

Leitura pratica:
- Skill em engenharia de software nao pode ser tratada como magia.
- Skill generica, velha ou fora de contexto pode:
  - nao ajudar
  - aumentar custo
  - atrapalhar

Para o Freedom Skills, essa e talvez a licao mais importante de todo o levantamento:
- skill boa nao e "mais prompt"
- skill boa e **contexto procedural certo, no momento certo, para o runtime certo**

### 1.3 How Well Do Agentic Skills Work in the Wild

Fonte principal:
- [Paper no arXiv](https://arxiv.org/abs/2604.04323)
- [Repo oficial](https://github.com/UCSB-NLP-Chang/Skill-Usage)

Pontos centrais:
- Esse trabalho faz a pergunta mais proxima do mundo real:
  - o que acontece quando o agente precisa **procurar**, **selecionar** e **adaptar** skills sozinho?
- O repo usa:
  - `SkillsBench` com **84 tasks**
  - `Terminal-Bench 2.0` com **89 tasks**
  - um conjunto de **34 mil skills reais**
- O paper avalia varios cenarios:
  - skills force-loaded
  - skills curadas
  - skills curadas com distractors
  - retrieval top-k em repositorio grande
  - refinement query-specific
  - refinement query-agnostic

Resultado principal:
- O ganho de skills **degrada consistentemente** quando o setup fica mais realista.
- Ou seja:
  - no laboratorio a skill parece otima
  - no marketplace real, com ruido e selecao imperfeita, o ganho some ou cai muito
- O abstract destaca que refinamento **query-specific** recupera parte relevante desse valor.
- No `Terminal-Bench 2.0`, o paper reporta melhoria de **57.7% para 65.5%** para Claude Opus 4.6 com query-specific refinement.

Leitura pratica:
- A parte dificil nao e so escrever a skill.
- A parte dificil e:
  - encontrar a skill certa
  - nao cair em falsos positivos
  - adaptar a skill ao caso concreto
  - lidar com skills imperfeitas

Isso encaixa muito com o problema real de um registry de skills.

## 2. Benchmarks Adjacentes Que Importam Muito

Eles nao medem "skills" diretamente, mas medem capacidades sem as quais um ecossistema de skills nao fecha.

## 2.1 Function Calling E Tool Use

| Benchmark | Fonte | O que mede | Relevancia para skills |
| --- | --- | --- | --- |
| [BFCL V4](https://gorilla.cs.berkeley.edu/leaderboard) / [repo](https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard) | Berkeley/Gorilla | function calling executavel, multi-turn, web search, memory, format sensitivity | skill sem invocacao correta de ferramenta vira papel |
| [ToolTalk](https://arxiv.org/abs/2311.10775) | paper | multi-step tool usage em dialogo | bom para skills conversacionais |
| [ToolSandbox](https://arxiv.org/abs/2408.04682) / [repo](https://github.com/apple/ToolSandbox) | Apple | tool use stateful, conversational e interactive | bom para medir dependencias de estado e informacao insuficiente |
| [tau-bench](https://arxiv.org/abs/2406.12045) | paper | interacao tool-agent-user com politicas de dominio | bom para skills que precisam seguir regras |
| [tau2-bench](https://arxiv.org/abs/2506.07982) | paper | dual-control, onde usuario e agente tambem agem | bom para skills guiadas para nao tecnicos |
| [API-Bank](https://arxiv.org/abs/2304.08244) | paper | benchmark mais antigo de tool-augmented LLMs | util como baseline historico |

Leitura pratica:
- BFCL e a melhor referencia para **tool invocation**.
- tau-bench e mais proximo de **policy-following em fluxo real**.
- ToolSandbox e util para medir onde a skill depende de estado acumulado, nomes canonicos, precondicoes e informacao faltante.

## 2.2 Web Agents

| Benchmark | Fonte | O que mede | Relevancia para skills |
| --- | --- | --- | --- |
| [WebArena](https://webarena.dev/) / [paper](https://arxiv.org/abs/2307.13854) / [repo](https://github.com/web-arena-x/webarena) | Carnegie Mellon et al. | tarefas web realistas em ambiente self-hosted | boa base para skills web reproduziveis |
| [VisualWebArena](https://jykoh.com/vwa) / [paper](https://arxiv.org/abs/2401.13649) / [repo](https://github.com/web-arena-x/visualwebarena) | CMU et al. | tarefas web visualmente ancoradas | importante para skills que dependem de UI, nao so DOM |
| [AssistantBench](https://arxiv.org/abs/2407.15711) | paper | tasks web realistas e demoradas | bom para medir utilidade real, nao so navegacao curta |
| [WorkArena](https://github.com/ServiceNow/WorkArena) / [paper](https://arxiv.org/abs/2403.07718) | ServiceNow | rotina de knowledge work em ServiceNow | excelente para skills de escritorio/ops |
| [WorkArena++](https://arxiv.org/abs/2407.05291) | paper | composicao, planejamento, memoria | util para composition benchmarks |
| [WebArena-Verified](https://github.com/ServiceNow/webarena-verified) | ServiceNow, 2025-2026 | versao auditada, scoring offline e deterministico | boa referencia para "verified release" de benchmark |

Pontos uteis:
- O [paper do WebArena](https://arxiv.org/abs/2307.13854) reporta melhor agente GPT-4-based com **14.41%** vs **78.24% humano**.
- O [repo do WebArena](https://github.com/web-arena-x/webarena) fala de **812 examples** na avaliacao end-to-end.
- O [repo do VisualWebArena](https://github.com/web-arena-x/visualwebarena) fala em **910 tasks** no conjunto completo.
- O [repo do WorkArena](https://github.com/ServiceNow/WorkArena) fala em **19.912 instancias unicas de 33 tasks atomicas**, e o `WorkArena++` com **682 tasks** composicionais.
- O [repo do WebArena-Verified](https://github.com/ServiceNow/webarena-verified) destaca um subset hard de **258 tasks** e avaliacao offline deterministica.

## 2.3 GUI, Desktop E Mobile

| Benchmark | Fonte | O que mede | Relevancia para skills |
| --- | --- | --- | --- |
| [OSWorld](https://os-world.github.io/) / [paper](https://arxiv.org/abs/2404.07972) / [repo](https://github.com/xlang-ai/OSWorld) | xlang-ai et al. | open-ended tasks em computadores reais | skills que dependem de apps reais e fluxos cross-app |
| [OSWorld-Verified](https://github.com/xlang-ai/OSWorld) | update de 2025 | versao corrigida/verified | referencia para benchmark endurecido apos feedback da comunidade |
| [OSWorld-MCP](https://arxiv.org/abs/2510.24563) | paper | GUI + invocacao MCP | muito relevante se skills forem acopladas a ferramentas MCP |
| [AndroidWorld](https://google-research.github.io/android_world/) / [paper](https://arxiv.org/abs/2405.14573) / [repo](https://github.com/google-research/android_world) | Google Research | benchmark dinamico em Android | skills mobile e tarefas de onboarding no celular |
| [MobileWorld](https://github.com/Tongyi-MAI/MobileWorld) | repo/paper | benchmark mobile online com MCP | interessante como direcao emergente |

Pontos uteis:
- O [repo do AndroidWorld](https://github.com/google-research/android_world) fala em **116 tasks em 20 apps** e milhoes de variacoes parametrizadas.
- O [repo do OSWorld](https://github.com/xlang-ai/OSWorld) destaca o lancamento de **OSWorld-Verified** em **2025-07-28**.
- O [abstract do OSWorld-MCP](https://arxiv.org/abs/2510.24563) fala em **158 ferramentas validadas em 7 apps** e evidencia que MCP tools costumam melhorar o sucesso, mas a taxa de invocacao correta ainda e baixa.

## 2.4 Terminal, Coding E Software Engineering

| Benchmark | Fonte | O que mede | Relevancia para skills |
| --- | --- | --- | --- |
| [Terminal-Bench](https://github.com/harbor-framework/terminal-bench) / [paper](https://arxiv.org/abs/2601.11868) | Harbor/Laude | tarefas reais em terminal | benchmark forte para skill operacional |
| [SWE-bench](https://github.com/SWE-bench/SWE-bench) / [paper](https://arxiv.org/abs/2310.06770) | Princeton et al. | resolucao de issues reais em GitHub | baseline principal para skills de coding |
| [SWE-bench Verified](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified) | Princeton/OpenAI Preparedness | subset resolvivel validado por humanos | melhor controle de qualidade |
| [SWE-bench Multimodal](https://arxiv.org/abs/2410.03859) | paper/repo | tarefas com componente visual em software | util para skills de frontend ou GUI dev |
| [TheAgentCompany](https://the-agent-company.com/) / [paper](https://arxiv.org/abs/2412.14161) / [repo](https://github.com/TheAgentCompany/TheAgentCompany) | CMU et al. | tarefas profissionais consequenciais | bom para benchmark de "digital worker" |

Pontos uteis:
- O [repo do Terminal-Bench](https://github.com/harbor-framework/terminal-bench) diz que o benchmark ainda esta em **beta** com **~100 tasks**.
- O [repo do Skill-Usage](https://github.com/UCSB-NLP-Chang/Skill-Usage) usa `Terminal-Bench 2.0` com **89 tasks**.
- O [repo do SWE-bench](https://github.com/SWE-bench/SWE-bench) destaca `SWE-bench Verified` como subset de **500 problemas** validado por engenheiros.
- O [repo do TheAgentCompany](https://github.com/TheAgentCompany/TheAgentCompany) fala em **175 task images** dentro de uma empresa simulada.

Leitura pratica:
- Se o Freedom Skills quiser provar valor em runtime real, `Terminal-Bench`, `SWE-bench Verified` e `TheAgentCompany` sao as referencias mais fortes do lado de "fazer de verdade".

## 2.5 Assistants Generalistas E Lifelong Learning

| Benchmark | Fonte | O que mede | Relevancia para skills |
| --- | --- | --- | --- |
| [GAIA](https://arxiv.org/abs/2311.12983) | paper / dataset | assistentes gerais com web, multimodalidade e tool use | bom benchmark de utilidade geral |
| [AgentBench](https://arxiv.org/abs/2308.03688) | paper / repo | LLMs como agentes em 8 ambientes | bom baseline historico |
| [LifelongAgentBench](https://arxiv.org/abs/2505.11942) | paper | lifelong learning em tarefas interdependentes | relevante para bibliotecas de skills que aprendem ao longo do tempo |

Pontos uteis:
- O [paper do GAIA](https://arxiv.org/abs/2311.12983) apresenta **466 questoes** e reporta **92% humano vs 15% GPT-4 com plugins** na epoca.
- O [paper do AgentBench](https://arxiv.org/abs/2308.03688) cobre **8 ambientes**.
- O [paper do LifelongAgentBench](https://arxiv.org/abs/2505.11942) e um dos poucos que trata explicitamente de **tarefas skill-grounded e interdependentes**.

## 3. O Que Ainda Falta No Mercado

Mesmo somando tudo acima, ainda faltam partes importantes para um ecossistema serio de skills.

### 3.1 Descoberta E Roteamento De Skills

Ainda ha pouco benchmark convincente para:
- recuperar a skill certa em repositorios enormes
- distinguir skills parecidas mas semanticamente diferentes
- avaliar metadata enganosa ou insuficiente

Dois trabalhos adjacentes importam aqui:
- [SkillRouter](https://arxiv.org/abs/2603.22455): estuda roteamento em **~80k skills e 75 queries verificadas por especialistas**
- [Semantic Tool Discovery for MCP](https://arxiv.org/abs/2603.20313): trabalha descoberta semantica de ferramentas MCP

### 3.2 Trust, Safety E Manipulacao De Ranking

Tambem falta benchmark forte para:
- skill maliciosa
- skill outdated
- skill com capabilities excessivas
- skill description manipulada para ser escolhida indevidamente

Trabalho adjacente importante:
- [ToolTweak](https://arxiv.org/abs/2510.02554): mostra que nomes e descricoes de tools podem enviesar fortemente a selecao

Isso importa muito para qualquer marketplace ou registry.

### 3.3 UX Para Nao Tecnicos

Quase nenhum benchmark atual mede bem:
- se a skill reduz ambiguidade
- se a skill melhora onboarding
- se o agente avisa sobre risco e privacidade na hora certa
- se a resposta fica mais compreensivel para um usuario leigo

Para o Freedom Skills, isso parece central, nao periferico.

## 4. O Que Isso Implica Para O Freedom Skills

Minha leitura atual:

- Se a pergunta for "ja existe benchmark de skills?" a resposta curta e:
  - **sim, mas ainda sao poucos e novos**
- Se a pergunta for "ja existe benchmark pronto para o tipo de sistema que queremos?" a resposta e:
  - **nao**

O que existe hoje cobre bem:
- eficacia local de skills
- tool use
- execucao em web/OS/terminal
- coding agents

O que ainda falta e exatamente a parte mais interessante para esse projeto:
- discovery
- trust
- portability entre harnesses
- composicao multi-skill
- UX guiada e segura

Por isso faz sentido usar os benchmarks existentes como base comparativa e construir uma camada propria por cima.

O documento complementar com essa proposta esta em [skills-benchmark-strategy.md](./skills-benchmark-strategy.md).

## Fontes

### Benchmarks diretos de skills
- [SkillsBench site](https://www.skillsbench.ai/)
- [SkillsBench paper](https://arxiv.org/abs/2602.12670)
- [SkillsBench repo](https://github.com/benchflow-ai/skillsbench)
- [SWE-Skills-Bench paper](https://arxiv.org/abs/2603.15401)
- [SWE-Skills-Bench repo](https://github.com/GeniusHTX/SWE-Skills-Bench)
- [How Well Do Agentic Skills Work in the Wild](https://arxiv.org/abs/2604.04323)
- [Skill-Usage repo](https://github.com/UCSB-NLP-Chang/Skill-Usage)

### Tool use e function calling
- [BFCL leaderboard](https://gorilla.cs.berkeley.edu/leaderboard)
- [BFCL repo](https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard)
- [ToolTalk](https://arxiv.org/abs/2311.10775)
- [ToolSandbox](https://arxiv.org/abs/2408.04682)
- [tau-bench](https://arxiv.org/abs/2406.12045)
- [tau2-bench](https://arxiv.org/abs/2506.07982)
- [API-Bank](https://arxiv.org/abs/2304.08244)

### Web, GUI, terminal e coding
- [WebArena](https://arxiv.org/abs/2307.13854)
- [WebArena repo](https://github.com/web-arena-x/webarena)
- [VisualWebArena](https://arxiv.org/abs/2401.13649)
- [VisualWebArena repo](https://github.com/web-arena-x/visualwebarena)
- [AssistantBench](https://arxiv.org/abs/2407.15711)
- [WorkArena repo](https://github.com/ServiceNow/WorkArena)
- [WorkArena paper](https://arxiv.org/abs/2403.07718)
- [WorkArena++ paper](https://arxiv.org/abs/2407.05291)
- [WebArena-Verified repo](https://github.com/ServiceNow/webarena-verified)
- [OSWorld paper](https://arxiv.org/abs/2404.07972)
- [OSWorld repo](https://github.com/xlang-ai/OSWorld)
- [OSWorld-MCP paper](https://arxiv.org/abs/2510.24563)
- [AndroidWorld paper](https://arxiv.org/abs/2405.14573)
- [AndroidWorld repo](https://github.com/google-research/android_world)
- [MobileWorld repo](https://github.com/Tongyi-MAI/MobileWorld)
- [Terminal-Bench repo](https://github.com/harbor-framework/terminal-bench)
- [Terminal-Bench paper](https://arxiv.org/abs/2601.11868)
- [SWE-bench repo](https://github.com/SWE-bench/SWE-bench)
- [SWE-bench paper](https://arxiv.org/abs/2310.06770)
- [SWE-bench Multimodal](https://arxiv.org/abs/2410.03859)
- [TheAgentCompany paper](https://arxiv.org/abs/2412.14161)
- [TheAgentCompany repo](https://github.com/TheAgentCompany/TheAgentCompany)

### Assistants gerais, memoria e discovery
- [GAIA](https://arxiv.org/abs/2311.12983)
- [AgentBench](https://arxiv.org/abs/2308.03688)
- [LifelongAgentBench](https://arxiv.org/abs/2505.11942)
- [SkillRouter](https://arxiv.org/abs/2603.22455)
- [Semantic Tool Discovery for MCP](https://arxiv.org/abs/2603.20313)
- [ToolTweak](https://arxiv.org/abs/2510.02554)
