# Algoritmo de descoberta e compartilhamento de skills

Este documento ignora transporte, protocolo e rede social. A pergunta aqui e:

> Como deveria funcionar um bom sistema de descoberta, recomendacao, compartilhamento e confianca para skills?

A resposta curta: um bom sistema nao e uma lista ordenada por popularidade. Ele e um pipeline de decisao que combina **intencao do usuario**, **compatibilidade tecnica**, **qualidade observada**, **risco**, **confianca social/organizacional** e **politica local**.

## 1. O que o sistema precisa resolver

Um usuario nao quer "achar skills". Ele quer:

- resolver uma tarefa agora
- evitar instalar lixo
- evitar instalar algo perigoso
- entender por que uma skill e recomendada
- compartilhar uma skill util com pouco atrito
- confiar que atualizacoes nao trocaram uma ferramenta boa por uma bomba

Entao discovery de skills tem quatro problemas separados:

1. **Recuperacao**: achar skills candidatas para uma intencao.
2. **Ranking**: ordenar candidatas pelo melhor tradeoff entre utilidade e confianca.
3. **Admissao**: decidir se uma skill pode ser instalada/executada naquele ambiente.
4. **Distribuicao de confianca**: permitir que pessoas, times e comunidades compartilhem curadoria sem transformar isso em "instale porque e popular".

## 2. Objeto central: o manifesto da skill

Toda skill precisa ter um manifesto estruturado. Sem isso, discovery vira busca textual fragil.

Campos essenciais:

- `id`: identificador estavel da skill
- `name`: nome humano
- `description`: descricao curta
- `version`: versao publicada
- `publisher`: autor ou organizacao
- `runtime`: ambientes suportados, por exemplo Codex, Claude Code, Gemini CLI
- `entrypoints`: comandos, prompts, scripts ou arquivos principais
- `capabilities`: permissoes desejadas
- `inputs`: tipos de entrada esperados
- `outputs`: tipos de saida produzidos
- `domains`: temas e categorias
- `examples`: exemplos reais de uso
- `artifacts`: arquivos, hashes e fonte
- `provenance`: commit, build, assinatura, auditoria, quando existir

O manifesto nao concede permissao. Ele apenas declara o que a skill pede. A plataforma decide se aceita.

## 3. Pipeline basico

O algoritmo pode ser pensado assim:

```text
query/contexto do usuario
  -> entender intencao
  -> descobrir fontes provaveis
  -> consultar fontes externas
  -> resolver candidatos encontrados
  -> filtrar compatibilidade
  -> calcular utilidade
  -> calcular confianca
  -> calcular risco
  -> aplicar politica local
  -> ranquear
  -> explicar recomendacao
  -> instalar/executar com sandbox
  -> coletar feedback local
```

Esse pipeline e mais importante do que qualquer tecnologia de registry.

## 4. Descoberta federada: onde procurar

O usuario nao esta olhando uma lista local de skills. Na pratica, a plataforma precisa descobrir skills em fontes distribuidas, mais parecido com busca na web do que com uma app store fechada.

Fontes possiveis:

- busca geral na web
- sites especificos de listas de skills
- repositorios Git
- releases de projetos
- indices comunitarios
- listas curadas por pessoas ou times
- eventos publicados em redes/protocolos descentralizados
- referencias encontradas em READMEs, documentacao e posts
- cache local de skills ja vistas antes

O algoritmo nao deve assumir uma fonte canonica. Ele deve tratar discovery como um problema de **coleta, normalizacao e verificacao de candidatos**.

Para cada fonte, o sistema precisa de um adaptador:

- `web_search`: encontra paginas, repositorios e listas publicas
- `repo_scan`: procura manifestos em repositorios conhecidos
- `curated_list`: le listas mantidas por usuarios, comunidades ou empresas
- `protocol_events`: le eventos de redes descentralizadas, quando existirem
- `local_cache`: reaproveita skills ja vistas, instaladas ou avaliadas

Depois da coleta, cada candidato precisa ser resolvido para algo verificavel:

1. validar schema do manifesto
2. normalizar categorias, runtimes e capabilities
3. calcular hashes dos artefatos
4. extrair texto indexavel
5. rodar checks estaticos basicos
6. atribuir uma classe inicial de risco
7. registrar origem e versao

Skills sem manifesto bom podem existir, mas devem perder ranking e exigir mais cautela.

## 5. Geracao de candidatos

Discovery bom nao depende de uma lista local. Ele mistura fontes externas, curadorias e contexto local para montar um conjunto pequeno de candidatos plausiveis.

### 5.1 Planejamento da busca

Antes de sair procurando, a plataforma transforma o pedido do usuario em uma estrategia:

- termos provaveis de busca
- categorias provaveis
- runtimes aceitos
- capacidades aceitaveis
- fontes preferidas
- fontes proibidas
- grau maximo de risco

Exemplo:

```text
Pedido: "preciso converter PDF escaneado em Markdown"
Busca externa: "codex skill pdf markdown ocr", "agent skill pdf ocr markdown"
Categorias: documents, pdf, ocr, markdown
Capabilities maximas: read-file, write-workspace, optional-network-read
Fontes preferidas: skills ja usadas, listas confiaveis, repositorios conhecidos
```

### 5.2 Consulta de fontes

Cada fonte devolve evidencias, nao necessariamente uma skill pronta:

- URL de manifesto
- repo com `SKILL.md`
- release com bundle
- pagina de catalogo
- recomendacao humana
- lista curada
- evento assinado
- referencia indireta em documentacao

O sistema deve coletar mais candidatos do que pretende mostrar. Depois ele deduplica, resolve versoes e descarta o que nao passa no minimo de qualidade.

### 5.3 Cache local e matching por contexto

O sistema tambem deve olhar para o ambiente atual:

- arquivos presentes no workspace
- extensoes de arquivos
- framework detectado
- comandos disponiveis
- sistema operacional
- ferramentas autenticadas
- historico local de uso

Exemplo: se o workspace tem `.pptx`, skills de apresentacao sobem. Se tem `pyproject.toml`, skills Python sobem. Se ha um PR aberto, skills GitHub sobem.

O cache local serve para acelerar e personalizar, mas nao e a fonte de verdade. Ele guarda:

- skills ja vistas
- manifestos resolvidos
- hashes conhecidos
- fontes que funcionaram
- uso local
- bloqueios e preferencias do usuario

### 5.4 Curadoria e descoberta social

Listas humanas sao essenciais:

- favoritos do usuario
- aprovados pelo time
- recomendados por especialistas
- skills oficiais de um projeto
- skills bloqueadas por seguranca

Curadoria nao deve substituir ranking. Ela deve entrar como sinal ponderado.

### 5.5 Deduplicacao e resolucao

Fontes diferentes podem apontar para a mesma skill. Antes de ranquear, o sistema precisa agrupar candidatos por identidade:

- mesmo `id`
- mesmo repositorio
- mesmo publisher + nome
- mesmo hash de artefato
- manifestos equivalentes em fontes diferentes

Depois, escolhe a versao mais apropriada pela politica local: estavel, assinada, auditada, recente o suficiente e compativel com o runtime.

## 6. Filtro de compatibilidade

Antes de ranquear, descarte ou rebaixe skills que nao podem funcionar.

Verificacoes tipicas:

- runtime suportado
- sistema operacional
- versao minima da plataforma
- dependencias disponiveis
- ferramentas externas necessarias
- tipo de workspace
- capacidades proibidas pela politica local
- conflitos com outras skills

Uma skill perfeita para a tarefa, mas impossivel de executar, nao deve aparecer como recomendacao principal.

## 7. Score de utilidade

Utilidade responde: "essa skill provavelmente ajuda neste caso?"

Sinais bons:

- a fonte encontrada descreve uma tarefa parecida
- o manifesto declara entradas/saidas compativeis com o pedido
- exemplos parecidos com a tarefa atual
- compatibilidade com arquivos do workspace
- historico de sucesso local
- historico de sucesso em contextos parecidos
- manutencao recente
- documentacao clara
- testes ou fixtures

Um score simples:

```text
utility =
  0.25 * task_fit +
  0.20 * manifest_fit +
  0.20 * context_match +
  0.15 * historical_success +
  0.10 * documentation_quality +
  0.10 * maintenance_health
```

Os pesos devem ser ajustaveis. Para uma primeira versao, pesos manuais sao suficientes.

## 8. Score de confianca

Confianca responde: "quem esta dizendo que isso e bom, e por que eu deveria ligar?"

Sinais positivos:

- publisher conhecido pelo usuario
- publisher aprovado pela organizacao
- skill usada antes com sucesso
- vouch explicito de peers confiaveis
- recomendada por pessoas que o usuario segue
- recomendada por curadores seguidos
- usada por comunidades proximas ao usuario
- auditoria humana registrada
- artefatos assinados
- hashes batem
- origem em repositorio conhecido
- recomendada por curadores confiaveis
- poucas mudancas perigosas entre versoes
- bom historico de updates

Sinais negativos:

- publisher novo ou desconhecido
- ownership mudou recentemente
- artefato sem fonte
- manifesto vago
- capabilities amplas demais
- reports negativos relevantes
- versao nova sem historico
- pacote tenta executar coisas fora do escopo declarado

Confianca deve ser contextual. Uma pessoa pode confiar numa skill para ler Markdown, mas nao para enviar emails ou acessar secrets.

### 8.1 Web of trust e vouches

Web of trust nao e popularidade. O ponto nao e "muita gente gostou"; e "pessoas relevantes para mim estao colocando reputacao em jogo por esta skill".

Sinais de web of trust:

- peer direto fez vouch da skill
- peer direto usa a skill regularmente
- pessoa seguida recomendou a skill
- curador confiavel incluiu a skill em uma lista
- organizacao confiavel aprovou a skill
- auditor conhecido assinou uma revisao
- varios peers independentes convergem na mesma recomendacao
- nao ha reports relevantes vindos de peers confiaveis

Esses sinais devem ser ponderados por proximidade e contexto:

```text
trust =
  direct_peer_vouches +
  followed_people_vouches +
  trusted_curator_vouches +
  organization_approval +
  auditor_attestations +
  local_success_history -
  trusted_negative_reports -
  suspicious_recommendation_patterns
```

Exemplo: uma skill de Nostr recomendada por tres pessoas que o usuario segue no Nostr pode subir bastante no ranking. Mas isso nao deve liberar automaticamente capabilities sensiveis. O vouch aumenta confianca; a politica local ainda decide o que pode executar.

Vouches tambem precisam ter escopo. "Usei e gostei" vale menos que:

```text
Eu usei `github-pr-review-helper@2.1.0` em tres PRs.
Nao pediu secrets.
So leu comentarios e escreveu no workspace.
Funcionou no Codex.
```

## 9. Score de risco

Risco responde: "qual o tamanho do estrago se essa skill se comportar mal?"

Uma taxonomia pratica:

- `R0`: leitura local limitada
- `R1`: escrita no workspace
- `R2`: rede de leitura
- `R3`: rede de escrita ou chamadas autenticadas
- `R4`: shell, instalacao de dependencias ou execucao de binarios
- `R5`: acesso a segredos, mensagens externas, pagamentos, contas de usuario

O risco base vem das capabilities declaradas. Depois ele e ajustado por comportamento observado e auditoria.

Risco deve medir blast radius, nao reputacao. Um publisher desconhecido nao torna automaticamente a skill mais destrutiva; ele reduz a confianca. Misturar os dois deixa o algoritmo confuso.

Exemplo de risco intrinseco:

```text
risk =
  capability_risk +
  dependency_risk +
  artifact_uncertainty +
  behavior_anomaly
```

Depois, a decisao combina risco com confianca:

```text
decision_pressure =
  intrinsic_risk -
  trust_mitigation
```

O ponto importante: risco alto nao significa "nunca instalar". Significa exigir mais evidencia, mais sandbox e mais confirmacao. Web of trust ajuda a reduzir incerteza, mas nao apaga o risco operacional de uma skill com shell, rede de escrita ou acesso a secrets.

## 10. Score final

Ranking nao deve ser "maior utilidade vence". Deve ser utilidade ponderada por confianca e penalizada por risco.

Uma formula inicial:

```text
final_score =
  utility_score
  * trust_multiplier
  * compatibility_multiplier
  - risk_penalty
  - policy_penalty
```

Onde:

- `trust_multiplier` aumenta skills vindas de fontes confiaveis
- `compatibility_multiplier` derruba skills parcialmente compativeis
- `risk_penalty` cresce com permissoes sensiveis
- `policy_penalty` bloqueia ou rebaixa o que viola regras locais

O `trust_multiplier` deve incluir web of trust: peers diretos, pessoas seguidas, curadores, organizacoes e auditores. O peso de um vouch deve cair com distancia social e subir quando vem acompanhado de contexto verificavel, versao exata e ausencia de conflito de interesse.

Para casos sensiveis, use thresholds:

```text
se risk >= R4 e trust < threshold:
  nao recomendar instalacao direta
  mostrar como "requer revisao"

se risk >= R4 e trust >= threshold:
  permitir recomendacao, mas manter sandbox e confirmacao explicita
```

## 11. Politica local

Politica local e a parte que impede o sistema de virar uma democracia de popularidade.

Exemplos:

- nunca instalar skill com `secret-access` sem aprovacao explicita
- permitir somente publishers aprovados em workspaces de cliente
- bloquear skills sem hash de artefato
- exigir auditoria para `network-write`
- permitir auto-install apenas ate `R1`
- quarentenar versoes recem-publicadas por 24 horas

Politica deve ser declarativa e auditavel.

## 12. Explicabilidade

Toda recomendacao deveria conseguir responder:

- por que apareceu?
- por que esta acima das outras?
- quais permissoes pede?
- quem recomenda?
- qual e o risco?
- o que mudou desde a versao anterior?
- o que sera bloqueado pelo sandbox?

Exemplo de explicacao boa:

> Recomendada porque foi encontrada em uma fonte confiavel para tarefas de PDF, o manifesto declara entrada PDF e saida Markdown, suporta este runtime, ja foi usada 12 vezes localmente com sucesso e pede apenas leitura do arquivo e escrita no workspace.

Exemplo ruim:

> Popular no catalogo.

Popularidade sozinha e um sinal fraco.

## 13. Compartilhamento

Compartilhar skill nao deveria significar "manda um zip e confia".

Modelos melhores:

- compartilhar um link para manifesto versionado
- compartilhar uma lista curada
- compartilhar uma recomendacao com comentario
- compartilhar uma policy pack de time
- compartilhar um lockfile com hashes
- compartilhar um bundle assinado

O compartilhamento ideal inclui:

- versao exata
- hash dos artefatos
- origem
- capabilities
- comentario humano opcional
- contexto em que funcionou

Exemplo:

```text
Usei `markdown-converter@1.4.2` para converter PDFs escaneados.
Funcionou bem com contratos longos.
Capabilities: read-file, write-workspace, optional-ocr.
Nao requer rede.
```

## 14. Atualizacoes

Atualizacao e uma das maiores fontes de risco.

O sistema deve comparar versoes:

- capabilities novas
- dependencias novas
- arquivos executaveis novos
- mudanca de publisher
- mudanca de origem
- aumento de risco
- diferenca de tamanho anormal
- mudancas em scripts de install/run

Regras praticas:

- patch sem mudanca de capability pode atualizar com pouco atrito
- nova capability sensivel exige confirmacao
- troca de publisher exige revisao
- queda de assinatura/provenance bloqueia update automatico

## 15. Feedback loop

O sistema melhora quando aprende com uso real, mas privacidade precisa ser default.

Feedback local:

- instalada
- executada
- completou tarefa
- falhou
- desinstalada
- marcada como favorita
- bloqueada pelo usuario

Feedback compartilhavel, se opt-in:

- recomendacao
- review textual
- report de bug
- report de malware
- score agregado anonimo
- exemplo de tarefa resolvida

O historico local deve pesar muito. Se uma skill funciona repetidamente para Breno, isso importa mais do que popularidade global.

## 16. Anti-gaming

Qualquer sistema de ranking sera atacado.

Defesas basicas:

- nao usar download count bruto como sinal forte
- pesar recomendacoes por confianca, nao por quantidade
- detectar reviews coordenadas
- separar publisher reputation de skill reputation
- penalizar mudancas bruscas de capability
- quarentena para publishers novos
- permitir blocklists locais
- exigir hashes e assinaturas para artefatos

O objetivo nao e impedir todo ataque. E evitar que ataques baratos funcionem.

## 17. UX recomendada

Uma boa interface teria tres modos:

### 17.1 Sugestao durante a tarefa

Quando o usuario pede algo, a plataforma sugere:

```text
Skill sugerida: markdown-converter
Motivo: esta tarefa envolve PDF -> Markdown.
Risco: baixo, leitura de arquivo e escrita no workspace.
Acao: usar uma vez / instalar / ver detalhes
```

### 17.2 Busca federada

Busca que consulta fontes externas e permite filtros:

- categoria
- runtime
- risco maximo
- publisher
- curador
- capacidades
- auditada ou nao
- funciona offline

### 17.3 Tela de decisao

Antes de instalar/executar:

- resumo da skill
- exemplos de uso
- permissoes pedidas
- origem e versao
- sinais de confianca
- riscos
- mudancas desde a ultima versao
- botoes: usar uma vez, instalar, negar, revisar codigo

## 18. MVP recomendado

Eu faria o MVP assim:

1. Definir manifesto local de skill.
2. Criar adaptadores de descoberta para web, repositorios, listas curadas e cache local.
3. Implementar resolucao de candidatos para manifestos versionados e hasheados.
4. Implementar capabilities e classes de risco.
5. Implementar score simples: utilidade, confianca, risco.
6. Permitir listas curadas locais: favoritos, aprovadas, bloqueadas.
7. Mostrar explicacao curta para cada recomendacao.
8. Registrar feedback local de uso.
9. Travar instalacao/execucao por politica local.

Nao precisa comecar com marketplace ou reputacao global. Primeiro o sistema precisa descobrir candidatos em fontes reais, resolver manifestos corretamente e recomendar bem para uma pessoa em uma maquina.

## 19. Pseudocodigo

```python
def recommend_skills(query, workspace, user_profile, policy):
    intent = parse_intent(query, workspace)
    search_plan = plan_discovery(intent, workspace, user_profile, policy)

    evidence = collect_from_sources(
        web_search(search_plan),
        repo_scan(search_plan),
        curated_lists(search_plan, user_profile),
        protocol_events(search_plan),
        local_cache(search_plan, user_profile),
    )

    candidates = resolve_candidates(evidence)
    candidates = deduplicate(candidates)

    scored = []

    for skill in candidates:
        compatibility = check_compatibility(skill, workspace)
        if compatibility.blocked:
            continue

        utility = score_utility(skill, intent, workspace)
        trust_signals = collect_trust_signals(skill, evidence, user_profile)
        trust = score_trust(skill, trust_signals, user_profile)
        risk = score_intrinsic_risk(skill)
        policy_result = evaluate_policy(skill, risk, trust, policy)

        if policy_result.blocked:
            continue

        final = (
            utility
            * trust.multiplier
            * compatibility.multiplier
            - risk.penalty
            - policy_result.penalty
        )

        scored.append({
            "skill": skill,
            "score": final,
            "utility": utility,
            "trust": trust,
            "risk": risk,
            "explanation": explain(skill, utility, trust, risk, policy_result),
        })

    return sorted(scored, key=lambda item: item["score"], reverse=True)
```

## 20. Opiniao direta

O melhor sistema de descoberta de skills parece mais com um **package manager com ranking contextual e policy engine** do que com uma app store.

App store otimiza por popularidade, reviews e conversao. Skills precisam otimizar por:

- encaixe na tarefa atual
- baixo atrito
- seguranca operacional
- confianca contextual
- controle local
- explicabilidade

Minha regra de ouro:

> Recomende pela utilidade, permita pela politica, limite pelo sandbox e aprenda com o uso local.
