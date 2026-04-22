# skill-auditor

Spec inicial para uma skill focada em **auditar skills antes da instalacao**.

## Problema

Se o Freedom Skills tiver marketplace, discovery ou instalacao de skills de terceiros, uma pergunta basica aparece cedo:

> como evitar instalar uma skill maliciosa, insegura, enganosa ou simplesmente desnecessariamente perigosa?

Nao existe garantia perfeita.
Mas da para reduzir muito o risco com uma auditoria curta, repetivel e orientada por politica.

## Objetivo

Antes de instalar uma skill, a skill `skill-auditor` deve ajudar a responder:

- o que essa skill realmente faz?
- o que ela pede para usar?
- quais capacidades ela tenta obter?
- ha sinais de exfiltracao, execucao indevida, privilege escalation ou comportamento hostil?
- a skill parece compativel com a politica local?
- vale aprovar, revisar manualmente, sandboxar ou bloquear?

## Resultado esperado

A skill deve produzir uma avaliacao curta e acionavel, nao um tratado abstrato.

Saida ideal:
- **resumo da skill**
- **capacidades solicitadas**
- **riscos identificados**
- **sinais suspeitos**
- **recomendacao final**
- **acao sugerida**: aprovar, aprovar com restricoes, revisar manualmente, bloquear

## Entradas

A skill pode receber:
- pasta do skill
- manifesto do skill
- arquivos principais, como `SKILL.md`, scripts, referencias e wrappers
- metadata publicada em registry ou Nostr
- politica local da instalacao
- opcionalmente resultados de leitura por mais de um modelo

## O que ela deve inspecionar

### 1. Superficie declarada
- nome e descricao da skill
- objetivo declarado
- ferramentas pedidas
- arquivos acessados
- necessidade de rede
- necessidade de escrita em disco
- necessidade de execucao de shell
- necessidade de envio para terceiros

### 2. Superficie real
- scripts chamados de forma indireta
- downloads externos
- comandos dinamicos
- uso de shell com interpolacao arriscada
- chamadas de rede nao justificadas
- prompts que tentam burlar politica da plataforma
- instrucoes para ignorar revisao, aprovacao ou seguranca

### 3. Sinais de malicia ou comportamento hostil
- exfiltracao de arquivos ou segredos
- coleta excessiva de contexto
- envio de dados para endpoints opacos
- instalacao de binarios ou dependencias sem necessidade clara
- execucao de comandos destrutivos
- alteracoes fora do escopo do workspace
- tentativas de auto-ampliar permissoes
- engenharia social nas instrucoes

### 4. Compatibilidade com politica local
- a skill pede mais do que a politica permite?
- a skill pede capacidades que nao combinam com seu objetivo?
- a skill pode rodar em sandbox?
- a skill exige aprovacao humana forte?

## Leitura cruzada por multiplos modelos

Uma parte importante da ideia e passar a skill por mais de um modelo/agente para reduzir ponto cego.

Exemplo de fluxo:
- modelo A faz leitura estrutural e enumera capacidades
- modelo B faz leitura adversarial, procurando risco e abuso
- modelo C faz revisao final e resolve divergencias

O objetivo nao e “democratizar a verdade”, e sim aumentar cobertura de risco.

## Estrutura de saida sugerida

### Resumo
- o que a skill faz em 2 ou 3 linhas

### Capacidades solicitadas
- read only
- workspace write
- exec shell
- network read
- network write
- secrets
- messaging

### Achados
- achados de baixo risco
- achados de medio risco
- achados de alto risco

### Sinais suspeitos
- lista curta e objetiva

### Recomendacao
- **approve**
- **approve-with-restrictions**
- **manual-review-required**
- **block**

### Justificativa
- razoes objetivas para a recomendacao

## Heuristicas importantes

### Capacidade sem justificativa e sinal ruim
Se a skill pede rede, shell ou escrita ampla sem precisar disso para o objetivo, isso deve pesar contra.

### Texto bonito nao conta como prova
A auditoria deve olhar para o que a skill **faz ou tenta fazer**, nao apenas para o que ela diz.

### Menos falso positivo inutil
Nem toda skill poderosa e maliciosa.
A ideia e separar:
- poder legitimo
- poder excessivo
- poder opaco

### Politica local manda
Uma skill pode ser aceitavel num laboratorio tecnico e inaceitavel num ambiente sensivel.

## Possiveis niveis de risco

- **baixo**: leitura e transformacao local, sem shell, sem rede, sem segredos
- **medio**: escrita local limitada, shell controlado, sem exfiltracao externa
- **alto**: rede, shell amplo, instalacao de dependencias, integracoes externas
- **critico**: segredos, terceiros, comandos destrutivos, opacidade forte, auto-elevacao

## Integracoes naturais

Essa skill conversa diretamente com:
- `skill-discovery-and-trust.md`
- `privacy-alerts`
- `threat-model-lite`
- `guided-agent-mode`

## Benchmarks / avaliacao futura

Se quiser benchmarkar essa skill, daria para medir:
- taxa de deteccao de skills maliciosas
- taxa de falso positivo
- qualidade da classificacao de risco
- concordancia entre modelos/auditores
- tempo de auditoria
- utilidade pratica da recomendacao final

## Minha leitura

Essa skill e uma das mais importantes do projeto.

Porque sem discovery confiavel e pre-install audit, um ecossistema de skills corre o risco de virar um marketplace de prompt opaco com superficie de ataque crescente.

Em uma frase:

> `skill-auditor` existe para impedir que a conveniencia de instalar skills seja maior do que a seguranca de quem vai usá-las.
