# Estrategia De Benchmark Para Freedom Skills

## TL;DR

O melhor caminho nao parece ser inventar um benchmark gigantesco do zero.

O melhor caminho parece ser:
- usar benchmarks existentes para o que eles ja medem bem
- construir uma camada propria exatamente onde o mercado ainda esta fraco:
  - discovery
  - trust
  - composicao
  - UX guiada
  - portability entre harnesses

## 1. O Que O Benchmark Do Projeto Precisa Responder

Se o projeto e "Freedom Skills", as perguntas certas nao sao so "o agente resolveu?".

As perguntas certas sao:
- a skill certa foi descoberta?
- a skill certa foi carregada?
- a skill ajudou mais do que atrapalhou?
- a skill induziu passos inseguros?
- a skill continuou util em harnesses diferentes?
- a skill reduziu a carga cognitiva do usuario?
- a skill manteve avisos de privacidade, opsec e risco quando necessario?

Ou seja: o benchmark precisa medir **valor operacional**, nao so performance abstrata.

## 2. Principios De Design

### 2.1 Medir Delta Contra Baseline

Toda task importante deveria ter pelo menos tres condicoes:
- sem skill
- com skill curada
- com skill recuperada automaticamente

Sem isso, fica facil confundir:
- qualidade do modelo
- qualidade do harness
- qualidade da skill

### 2.2 Separar Descoberta De Execucao

Uma skill pode falhar por dois motivos muito diferentes:
- a skill certa nao foi encontrada
- a skill foi encontrada, mas era ruim

Se isso cair num numero unico, o diagnostico fica fraco.

### 2.3 Fixar Versao, Data E Runtime

Os benchmarks atuais estao mudando rapido. Entao cada resultado precisa registrar:
- data
- benchmark version
- harness
- modelo
- provider
- numero de trials
- policy de ferramentas/permissoes

### 2.4 Preferir Verificadores Deterministicos

Sempre que possivel, usar:
- scripts
- diffs
- estado final verificavel
- artefatos esperados
- comparacao estrutural

LLM-as-judge ainda e util, mas como complemento, nao como fundamento.

### 2.5 Medir Instabilidade

Skill systems sao instaveis por natureza. Entao alem de pass rate, vale medir:
- `pass@k`
- variancia por trial
- taxa de regressao
- taxa de uso incorreto da skill

Isso vem diretamente da licao de [tau-bench](https://arxiv.org/abs/2406.12045) e do ecossistema de agent eval mais recente.

## 3. O Que Reusar De Fora

## 3.1 Camada De Eficacia De Skill

Reusar como referencia externa:
- [SkillsBench](https://www.skillsbench.ai/)
- [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401)
- [How Well Do Agentic Skills Work in the Wild](https://arxiv.org/abs/2604.04323)

Uso recomendado:
- comparar o desenho das nossas skills com o estado da arte
- validar se uma skill focada realmente ajuda
- medir se retrieval real mantem valor ou dissolve o ganho

## 3.2 Camada De Tool Use

Reusar:
- [BFCL](https://gorilla.cs.berkeley.edu/leaderboard)
- [ToolSandbox](https://arxiv.org/abs/2408.04682)
- [tau-bench](https://arxiv.org/abs/2406.12045)

Uso recomendado:
- testar se a skill leva a melhor selecao de ferramentas
- testar se a skill melhora chamada multi-step
- testar se a skill ajuda a seguir regras de dominio

## 3.3 Camada De Execucao Real

Reusar conforme o dominio:
- [WebArena-Verified](https://github.com/ServiceNow/webarena-verified)
- [WorkArena](https://github.com/ServiceNow/WorkArena)
- [OSWorld-Verified](https://github.com/xlang-ai/OSWorld)
- [Terminal-Bench](https://github.com/harbor-framework/terminal-bench)
- [SWE-bench Verified](https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified)
- [TheAgentCompany](https://the-agent-company.com/)

Uso recomendado:
- provar que a skill sai do papel
- medir impacto em tarefas long-horizon
- comparar harnesses em ambiente com verificador forte

## 4. O Que Precisamos Construir Aqui

## 4.1 Skill Discovery Bench

Objetivo:
- medir se o sistema encontra as skills certas num catalogo grande e ruidoso

Entrada:
- tarefa do usuario
- catalogo com skills boas, skills parecidas, skills distratoras e skills maliciosas

Metricas:
- Recall@k
- MRR
- top-1 accuracy
- latencia
- custo em tokens
- false positive rate
- taxa de selecao de skill insegura

Casos que precisam existir:
- skill certa com nome ruim
- skill errada com descricao sedutora
- skills quase iguais, mas uma esta outdated
- skills cujo corpo e importante, nao so metadata

Aqui vale absorver as licoes de:
- [SkillRouter](https://arxiv.org/abs/2603.22455)
- [ToolTweak](https://arxiv.org/abs/2510.02554)

## 4.2 Skill Fit Bench

Objetivo:
- medir se a skill certa realmente melhora o task success

Condicoes:
- no-skill
- correct-skill
- retrieved-skill

Metricas:
- delta de pass rate
- delta de custo
- delta de latencia
- negative delta rate
- unnecessary skill load rate

Essa camada responde a pergunta:
- "essa skill e realmente util ou so aumenta contexto?"

## 4.3 Skill Composition Bench

Objetivo:
- medir tarefas que exigem 2-4 skills articuladas

Exemplos bons para este projeto:
- Nostr + BTCPay
- Cashu + Lightning
- carteira + threat model + publish safely
- evento comunitario + pagamentos + follow-up privado

Metricas:
- task completion
- ordem correta de uso
- composicao minima necessaria
- taxa de chamadas redundantes
- taxa de quebra de contexto entre skills

## 4.4 Skill Trust And Safety Bench

Objetivo:
- medir se o sistema recusa ou isola skills arriscadas

Casos que deveriam entrar:
- skill com pedido de permissao excessivo
- skill com acao externa nao justificada
- skill desatualizada para runtime atual
- skill com proveniencia indefinida
- skill com instruction hijacking no texto
- skill que incentiva vazamento de segredo
- skill que omite alerta de privacidade

Metricas:
- unsafe accept rate
- safe reject rate
- precision/recall de bloqueio
- clareza da justificativa de bloqueio
- taxa de escalonamento correto para aprovacao humana

Isso parece especialmente importante para um ecossistema que quer lidar com:
- ativistas
- autocustodia
- comunicacao privada
- pagamentos

## 4.5 Skill UX Bench

Objetivo:
- medir se a skill melhora a experiencia de usuarios nao tecnicos

Isso hoje quase nao aparece nos benchmarks existentes.

Metricas:
- numero de turnos ate a conclusao
- necessidade de esclarecimento
- compreensibilidade da resposta
- qualidade de warnings
- taxa de erro humano induzido pela resposta

Casos ideais:
- onboarding de wallet
- setup de private comms
- escolha de meio de pagamento por contexto
- publicacao segura
- recovery/backup drill

## 4.6 Skill Portability Bench

Objetivo:
- medir se a mesma skill sobrevive em runtimes diferentes

Harnesses naturais para comparar:
- Codex
- Claude Code
- Gemini CLI
- OpenHands ou outro agent runtime aberto

Metricas:
- pass rate por harness
- delta de formatacao/adaptacao
- taxa de falha por incompatibilidade
- custo de manutencao por harness

## 5. Um V0 Realista

Eu comecaria pequeno e verificavel.

### Escopo

- **25 a 40 tasks**
- **4 suites**
- **3 harnesses**
- **3 condicoes por task**

### Suites

1. `discovery`
- 8 a 10 tasks
- foco em recuperar a skill certa

2. `execution`
- 8 a 10 tasks
- foco em fazer uma coisa concreta com verificador deterministico

3. `composition`
- 5 a 8 tasks
- foco em usar 2-4 skills em sequencia

4. `trust`
- 5 a 8 tasks
- foco em skills enganosas, desatualizadas ou perigosas

### Dominios Iniciais

Para ficar alinhado ao repo atual:
- Bitcoin wallets
- Lightning
- BTCPay
- Nostr
- Cashu/Fedimint
- secure communications
- threat modeling leve
- publish safely

## 6. Formato De Task

Cada task deveria ter algo como:

- `task.md`
- `verifier.sh` ou `verifier.py`
- `expected_artifacts/`
- `risk_labels.json`
- `allowed_tools.json`
- `gold_skills.json`
- `distractor_skills.json`

Campos importantes:
- objetivo
- precondicoes
- artefato final esperado
- tolerancias
- niveis de risco
- se a task exige escalonamento para humano

## 7. Metricas Que Eu Guardaria

Primarias:
- task success
- pass@k
- unsafe success rate

Secundarias:
- custo
- tempo
- numero de tool calls
- numero de turnos
- skills carregadas
- skills realmente usadas

Diagnosticas:
- retrieval miss
- retrieval false positive
- skill loaded but ignored
- skill followed but harmful
- skill stale/runtime mismatch
- user clarification burden

## 8. O Que Nao Fazer

- Nao construir um benchmark genericissimo de "agents" antes de provar valor em 10 tasks fortes.
- Nao misturar discovery e execution num unico score global.
- Nao depender so de judge LLM.
- Nao rankear apenas modelos base.
- Nao assumir que skill com mais texto e melhor.
- Nao ignorar versao de runtime, porque boa parte das regressioes de skill parece vir exatamente disso.

## 9. Proxima Sequencia De Trabalho

Eu faria assim:

1. Congelar um `benchmark-registry.md` com as suites externas que vao servir de referencia.
2. Escolher **10 tasks canonicas** do Freedom Skills.
3. Definir verificadores deterministicos para essas 10 tasks.
4. Montar um corpus pequeno de skills:
   - corretas
   - distratoras
   - outdated
   - maliciosas
5. Rodar o primeiro corte em:
   - Codex
   - Claude Code
   - Gemini CLI
6. So depois expandir volume.

## 10. Minha Opiniao

O espaco de benchmark de skills esta finalmente ficando serio, mas ainda esta incompleto.

O que ja existe hoje e bom para:
- provar que skill pode ajudar
- provar que hype sozinho nao basta
- provar que retrieval real e o gargalo

O que ainda falta, e onde o Freedom Skills pode ter opiniao propria, e:
- benchmark de trust
- benchmark de discovery em marketplace real
- benchmark de UX para nao tecnicos
- benchmark de portability entre harnesses

Se o projeto fizer isso bem, nao vai estar so usando benchmarks existentes.
Vai estar ajudando a definir a proxima geracao deles.

## Referencias

- [SkillsBench](https://www.skillsbench.ai/)
- [SkillsBench paper](https://arxiv.org/abs/2602.12670)
- [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401)
- [How Well Do Agentic Skills Work in the Wild](https://arxiv.org/abs/2604.04323)
- [BFCL](https://gorilla.cs.berkeley.edu/leaderboard)
- [ToolSandbox](https://arxiv.org/abs/2408.04682)
- [tau-bench](https://arxiv.org/abs/2406.12045)
- [WebArena-Verified](https://github.com/ServiceNow/webarena-verified)
- [WorkArena](https://github.com/ServiceNow/WorkArena)
- [OSWorld](https://github.com/xlang-ai/OSWorld)
- [OSWorld-MCP](https://arxiv.org/abs/2510.24563)
- [AndroidWorld](https://github.com/google-research/android_world)
- [Terminal-Bench](https://github.com/harbor-framework/terminal-bench)
- [SWE-bench](https://github.com/SWE-bench/SWE-bench)
- [TheAgentCompany](https://the-agent-company.com/)
- [SkillRouter](https://arxiv.org/abs/2603.22455)
- [ToolTweak](https://arxiv.org/abs/2510.02554)
