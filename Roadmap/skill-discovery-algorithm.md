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
  -> gerar candidatos
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

## 4. Ingestao: como skills entram no indice

Uma skill pode entrar por varios caminhos:

- publicada por um autor
- importada de um repositorio
- adicionada manualmente por um usuario
- recomendada por um time
- aprovada por uma organizacao
- descoberta em um catalogo publico

Na ingestao, o sistema deve:

1. validar schema do manifesto
2. normalizar categorias, runtimes e capabilities
3. calcular hashes dos artefatos
4. extrair texto indexavel
5. rodar checks estaticos basicos
6. atribuir uma classe inicial de risco
7. registrar origem e versao

Skills sem manifesto bom podem existir, mas devem perder ranking e exigir mais cautela.

## 5. Geracao de candidatos

Discovery bom nao depende de um unico tipo de busca. Ele mistura varias fontes de candidatos.

### 5.1 Busca lexical

Boa para termos exatos:

- `kaggle`
- `btcpay`
- `docx`
- `github pr comments`
- `pomodoro`

Usa BM25 ou equivalente em nome, descricao, tags, exemplos e README.

### 5.2 Busca semantica

Boa quando o usuario descreve uma necessidade:

- "quero transformar um PDF em markdown"
- "preciso responder comentarios de review"
- "me ajuda a organizar uma planilha"

Usa embeddings sobre descricao, exemplos, docs e historico de tarefas resolvidas.

### 5.3 Matching por contexto

O sistema tambem deve olhar para o ambiente atual:

- arquivos presentes no workspace
- extensoes de arquivos
- framework detectado
- comandos disponiveis
- sistema operacional
- ferramentas autenticadas
- historico local de uso

Exemplo: se o workspace tem `.pptx`, skills de apresentacao sobem. Se tem `pyproject.toml`, skills Python sobem. Se ha um PR aberto, skills GitHub sobem.

### 5.4 Curadoria

Listas humanas sao essenciais:

- favoritos do usuario
- aprovados pelo time
- recomendados por especialistas
- skills oficiais de um projeto
- skills bloqueadas por seguranca

Curadoria nao deve substituir ranking. Ela deve entrar como sinal ponderado.

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

- match textual com a consulta
- match semantico com a intencao
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
  0.25 * semantic_match +
  0.20 * lexical_match +
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

Exemplo:

```text
risk =
  capability_risk +
  dependency_risk +
  publisher_uncertainty +
  artifact_uncertainty +
  behavior_anomaly
```

O ponto importante: risco alto nao significa "nunca instalar". Significa exigir mais evidencia, mais sandbox e mais confirmacao.

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

Para casos sensiveis, use thresholds:

```text
se risk >= R4 e trust < threshold:
  nao recomendar instalacao direta
  mostrar como "requer revisao"
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

> Recomendada porque combina semanticamente com "converter PDF para Markdown", suporta este runtime, ja foi usada 12 vezes localmente com sucesso e pede apenas leitura do arquivo e escrita no workspace.

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

### 17.2 Catalogo pesquisavel

Busca com filtros:

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
2. Criar indice local com busca lexical e semantica.
3. Implementar capabilities e classes de risco.
4. Implementar score simples: utilidade, confianca, risco.
5. Permitir listas curadas locais: favoritos, aprovadas, bloqueadas.
6. Mostrar explicacao curta para cada recomendacao.
7. Registrar feedback local de uso.
8. Travar instalacao/execucao por politica local.

Nao precisa comecar com rede descentralizada, marketplace ou reputacao global. Primeiro o sistema precisa recomendar bem para uma pessoa em uma maquina.

## 19. Pseudocodigo

```python
def recommend_skills(query, workspace, user_profile, policy):
    intent = parse_intent(query, workspace)

    candidates = union(
        lexical_search(intent.terms),
        semantic_search(intent.embedding),
        context_matches(workspace),
        curated_candidates(user_profile),
    )

    scored = []

    for skill in candidates:
        compatibility = check_compatibility(skill, workspace)
        if compatibility.blocked:
            continue

        utility = score_utility(skill, intent, workspace)
        trust = score_trust(skill, user_profile)
        risk = score_risk(skill)
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

