# ai-request-coach

Spec inicial de uma skill para ajudar **usuários não técnicos** a pedir melhor para a IA sem precisar aprender prompting “na marra”.

## Problema

Muita gente sabe o que quer fazer, mas não sabe como pedir.

Pedidos típicos de usuário não técnico costumam vir assim:
- "faz isso"
- "me ajuda com esse negócio"
- "quero criar um projeto"
- "arruma isso aqui"
- "faz um site / campanha / documento"

O problema não é falta de intenção. É falta de estrutura.
A IA normalmente precisa inferir:
- objetivo real
- contexto
- urgência
- restrições
- público-alvo
- formato de saída
- nível de risco aceitável

Essa skill existe para reduzir esse atrito.

## Objetivo

Transformar pedidos vagos ou incompletos em pedidos melhores, com menos carga cognitiva para o usuário.

Ela não deve ensinar prompt engineering como aula. Ela deve **ajudar o usuário a chegar mais rápido num pedido útil**.

## Usuário-alvo

- pessoas não técnicas
- ativistas / organizadores / comunicadores
- gente com pressa
- usuários que sabem o objetivo, mas não sabem estruturar o pedido
- usuários que ficam intimidados com IA ou não sabem “o jeito certo de pedir”

## Resultado esperado

A skill deve ajudar a IA a fazer 5 coisas:

1. **Inferir a intenção principal** do usuário
2. **Detectar lacunas** relevantes de contexto
3. **Fazer poucas perguntas boas**, em vez de jogar um questionário enorme
4. **Sugerir uma formulação melhor** do pedido
5. **Oferecer modos guiados**, como “rápido”, “mais seguro”, “mais detalhado” ou “feito para mim”

## O que a skill faria na prática

### 1. Reescrever o pedido do usuário
Exemplo:

Entrada do usuário:
> quero ajuda para organizar um evento

Saída intermediária:
> Entendi. Você quer organizar um evento e precisa de ajuda prática. Posso te ajudar a montar plano, cronograma, divulgação, orçamento ou checklist. Se quiser, já começo com um plano simples.

### 2. Perguntar só o mínimo necessário
Em vez de dez perguntas, faria algo como:
- qual é o objetivo do evento?
- quando ele acontece?
- você quer um plano rápido ou detalhado?

### 3. Oferecer estrutura pronta
Exemplo:
- objetivo
- público
- prazo
- formato de entrega
- riscos / cuidados

### 4. Melhorar a formulação sem culpar o usuário
Em vez de:
- “seu prompt está ruim”

Usar algo como:
- “posso deixar seu pedido mais claro para a IA e seguir com isso”

### 5. Ajustar o modo de ajuda ao contexto
Exemplos de modo:
- **modo rápido**: assume o razoável e começa
- **modo guiado**: faz 2 ou 3 perguntas antes
- **modo seguro**: destaca riscos, privacidade, exposição e validações
- **modo especialista invisível**: a IA reorganiza o pedido internamente sem exigir nada do usuário

## Entradas

A skill pode receber:
- mensagem vaga do usuário
- link, imagem, arquivo ou contexto curto
- histórico recente da conversa
- preferência de modo, se houver

## Saídas

A skill pode produzir uma ou mais destas saídas:
- pedido reestruturado
- perguntas de esclarecimento mínimas
- plano inicial de ação
- checklist do que falta
- alerta de risco / privacidade / segurança
- template que o usuário pode reutilizar

## Exemplo de transformação

### Caso 1, pedido muito vago
Usuário:
> quero montar uma campanha

Skill ajudaria a IA a converter isso em algo como:
> Posso te ajudar a montar a campanha. Para não complicar, me diz só 3 coisas: qual é a causa, para quem é a campanha, e qual o prazo. Se preferir, eu posso assumir um formato simples e já te entregar um rascunho.

### Caso 2, pedido operacional
Usuário:
> preciso fazer um site pra um evento

Transformação útil:
> Posso montar a estrutura do site. Me ajuda só com: nome do evento, data, objetivo e onde as pessoas se inscrevem. Se quiser, já começo com uma landing page padrão e depois ajustamos.

### Caso 3, contexto sensível
Usuário:
> quero divulgar isso sem me expor

Transformação útil:
> Entendi. Como isso envolve exposição, vou priorizar segurança e privacidade. Posso te ajudar a escolher canal, formato de publicação e o que evitar divulgar. Se quiser, começo com um plano mais seguro e conservador.

## Heurísticas importantes

### Menos é mais
A skill não deve burocratizar a conversa.
Ela deve reduzir fricção, não aumentar.

### Perguntas com alto valor informacional
Só perguntar o que muda materialmente a resposta.

### Ajudar sem infantilizar
Usuário não técnico não é usuário incapaz.
O tom precisa ser respeitoso.

### Explicação opcional
A pessoa pode querer só ajuda prática.
Explicações longas sobre prompting devem ser opt-in.

### Segurança contextual
Se o pedido tocar em:
- exposição pública
- identidade
- localização
- contas
- arquivos sensíveis
- comunicação com terceiros

A skill deve sugerir cuidado extra ou acionar skills irmãs, como:
- `threat-model-lite`
- `private-comms-setup`
- `privacy-alerts`
- `publish-safely`

## Modos possíveis

### Modo 1, invisível
A IA melhora o pedido internamente sem falar muito disso.
Melhor para fluidez.

### Modo 2, assistido
A IA mostra uma versão melhorada do pedido e pede confirmação.
Melhor para ensinar sem dar aula.

### Modo 3, template
A IA entrega um mini formulário reutilizável.
Melhor para trabalhos recorrentes.

## Critérios de sucesso

A skill está funcionando bem se:
- o usuário chega mais rápido numa resposta útil
- há menos troca inútil de mensagens
- a IA faz menos perguntas redundantes
- pedidos vagos ainda produzem progresso
- usuários não técnicos se sentem mais à vontade para pedir ajuda
- contextos sensíveis disparam alertas melhores

## Riscos

- perguntar demais e matar a fluidez
- presumir contexto errado com excesso de confiança
- transformar toda conversa em formulário
- explicar demais “como pedir” em vez de simplesmente ajudar
- esconder riscos reais para parecer conveniente

## Benchmarks / avaliação futura

Essa skill poderia ser avaliada por:
- taxa de sucesso de pedidos vagos vs sem a skill
- número de mensagens até chegar numa tarefa executável
- satisfação subjetiva do usuário
- redução de ambiguidades críticas
- desempenho com usuários não técnicos reais
- taxa de detecção de contextos sensíveis

## Relação com outras skills do roadmap

Esta skill conversa diretamente com:
- `secure-project-bootstrap`
- `threat-model-lite`
- `private-comms-setup`
- `privacy-alerts`
- `publish-safely`
- `guided-agent-mode`

## Minha leitura

Essa pode ser uma das skills mais importantes do projeto.

Porque antes de resolver execução, benchmark ou marketplace, ela resolve uma coisa básica:
**ajudar a pessoa a conseguir pedir ajuda de um jeito que a IA realmente consiga transformar em ação útil.**
