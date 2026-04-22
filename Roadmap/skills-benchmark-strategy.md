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

A lista abaixo ja serve como base para o desenho do benchmark proprio.

### 7.1 Metricas primarias

Essas sao as metricas que realmente dizem se o sistema resolveu a task ou nao.

- **task success**
  - taxa de tasks resolvidas pelo verificador
- **partial success**
  - quando a task nao passa totalmente, mas cumpre parte importante do objetivo
- **pass@k**
  - sucesso considerando k tentativas ou k corridas
- **unsafe success rate**
  - taxa de tasks que "passaram", mas violando politica, seguranca ou restricoes da task
- **trustworthy success rate**
  - taxa de tasks que passam **e** respeitam requisitos de seguranca, permissao e escopo

### 7.2 Metricas de eficiencia

Essas dizem o custo real de chegar no resultado.

- **total tokens in**
- **total tokens out**
- **total tokens**
- **token efficiency**
  - sucesso por token gasto
- **wall clock time**
  - tempo total ate terminar
- **time to first useful action**
  - quanto tempo o sistema demora para sair da enrolacao e fazer algo util
- **time to verified success**
- **number of turns**
- **number of tool calls**
- **number of failed tool calls**
- **number of retries**
- **cost in USD** ou custo estimado por corrida

### 7.3 Metricas de discovery e retrieval

Como o Freedom Skills deve lidar com marketplace/registry, essa camada precisa ser medida separadamente.

- **retrieval recall@k**
  - se a skill correta apareceu entre as top k recuperadas
- **retrieval precision@k**
  - quantas das skills recuperadas eram realmente uteis
- **retrieval miss rate**
  - a skill certa existia, mas nao foi encontrada
- **retrieval false positive rate**
  - skill errada aparece como se fosse boa candidata
- **ranking quality**
  - quao alto a skill correta apareceu no ranking
- **first relevant skill rank**
- **distractor selection rate**
  - frequencia com que uma skill distratora e escolhida
- **malicious skill selection rate**
  - frequencia com que uma skill maliciosa ou enganosa e escolhida
- **stale skill selection rate**
  - frequencia com que o sistema escolhe skill desatualizada

### 7.4 Metricas de uso de skills

Nao basta recuperar. Precisa medir se a skill foi realmente usada e se ajudou.

- **skills loaded**
  - quantas skills foram carregadas
- **skills actually used**
  - quantas influenciaram a execucao de verdade
- **skill utilization rate**
  - proporcao entre skills carregadas e skills realmente usadas
- **skill adherence**
  - quanto o agente seguiu o procedimento relevante da skill
- **skill override rate**
  - frequencia com que o agente ignora a skill e segue outro caminho
- **skill conflict rate**
  - quando duas skills ou instrucoes entram em conflito
- **skill composition success**
  - sucesso em tasks que exigem 2 ou mais skills em sequencia
- **skill transferability**
  - mesma skill funciona em mais de um harness/runtime?
- **skill portability failure rate**
  - taxa de falha por mismatch de harness, toolset ou runtime

### 7.5 Metricas de qualidade da execucao

Aqui entra a qualidade do artefato final, nao apenas o fato de passar ou nao.

- **artifact correctness**
  - quao correto esta o artefato final
- **artifact completeness**
  - cobriu todos os requisitos?
- **artifact format compliance**
  - entregou no formato pedido?
- **deterministic verifier score**
  - quando houver score numerico do verificador
- **judge score**
  - quando um LLM judge ou avaliacao humana complementar for necessaria
- **regression rate**
  - resolveu uma coisa quebrando outra?
- **repair burden**
  - quanto trabalho manual faltou para deixar a saida usavel

### 7.6 Metricas de seguranca, trust e policy

Essa parte parece central para o benchmark do Freedom Skills.

- **policy violation rate**
- **unsafe tool usage rate**
  - usou ferramenta proibida ou num contexto nao permitido
- **permission escalation attempts**
- **secret exposure rate**
  - vazou segredo, token, credencial, dado sensivel
- **privacy violation rate**
  - expos metadados, identificadores ou informacao alem do necessario
- **over-broad capability use**
  - usou capacidades mais poderosas do que a task exigia
- **malicious skill execution rate**
  - seguiu instrucoes de skill maliciosa
- **deception susceptibility**
  - caiu em metadata enganosa, descricoes falsas ou nomes manipulados
- **human escalation correctness**
  - soube parar e pedir confirmacao quando devia

### 7.7 Metricas de UX para usuarios nao tecnicos

Essa e uma parte que quase nao aparece nos benchmarks atuais, mas para Freedom Skills deveria aparecer.

- **clarification burden**
  - quantas perguntas o sistema precisou fazer para entender a task
- **useful clarification rate**
  - proporcao de perguntas que realmente ajudaram
- **time to usable plan**
  - em quanto tempo o usuario recebe um plano acionavel
- **instruction clarity score**
  - a resposta ficou clara para leigo?
- **jargon load**
  - quanto jargao tecnico apareceu desnecessariamente
- **guided workflow completion rate**
  - usuarios conseguem terminar o fluxo guiado?
- **risk warning coverage**
  - o sistema avisou riscos importantes quando devia?
- **overwarning rate**
  - alertou risco demais e atrapalhou o fluxo?
- **user confidence score**
  - o usuario sente que sabe o que fazer depois da resposta?

### 7.8 Metricas comparativas entre harnesses

Como o projeto e multi-harness, vale guardar metricas comparaveis por runtime.

- **success by harness**
- **cost by harness**
- **latency by harness**
- **retrieval quality by harness**
- **skill adherence by harness**
- **safety by harness**
- **non-technical UX by harness**
- **variance by harness**
  - o mesmo harness e estavel entre rodadas ou muito erratico?

### 7.9 Metricas diagnosticas

Essas nao sao headline, mas explicam porque um resultado deu certo ou errado.

- **retrieval miss**
- **retrieval false positive**
- **skill loaded but ignored**
- **skill followed but harmful**
- **skill stale/runtime mismatch**
- **tool unavailable mismatch**
- **context window overflow or truncation issue**
- **user clarification burden**
- **verifier mismatch**
  - o sistema aparentemente resolveu, mas o verificador nao reconheceu

### 7.10 O que eu logaria por corrida

Para nao descobrir tarde demais que faltou observabilidade, eu guardaria por run:

- task id
- suite
- harness
- modelo
- skill set disponivel
- top k skills recuperadas
- skill selecionada
- skills efetivamente usadas
- tempo total
- tokens in/out
- custo estimado
- numero de turnos
- numero de tool calls
- eventos de erro
- violacoes de policy
- score do verificador
- score complementar de juiz humano/LLM, se houver
- outcome final: fail / partial / success / unsafe-success

### 7.11 Minha shortlist de metricas para v1

Se eu fosse comecar pequeno, mediria obrigatoriamente:

1. **task success**
2. **unsafe success rate**
3. **retrieval recall@k**
4. **distractor selection rate**
5. **skills loaded vs skills actually used**
6. **wall clock time**
7. **total tokens**
8. **cost**
9. **clarification burden**
10. **risk warning coverage**
11. **skill portability failure rate**
12. **trustworthy success rate**

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
