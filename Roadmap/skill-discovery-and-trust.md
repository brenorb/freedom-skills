# Skill discovery, recommendation and trust

Pesquisa inicial sobre descoberta de skills, recomendação e mitigação de risco para skills maliciosos, com preferência por uma arquitetura descentralizada baseada em **Nostr**.

## TL;DR

Não parece existir hoje um padrão Nostr maduro e específico para **registry de skills**. O que existe são **blocos compatíveis** que podem ser combinados:

- **NIP-89** para descoberta de handlers/apps recomendados
- **NIP-51** para listas, sets e curadorias públicas/privadas
- **NIP-32** para labels, classificação, risco e compatibilidade
- **NIP-56** para reports, inclusive `malware`
- **NIP-58** para badges/attestations de confiança
- **NIP-34** para anunciar repositórios e colaboração de código via Nostr
- **NIP-90** para serviços/agentes sob demanda, útil para a camada de uso/execução

Minha leitura: dá para montar uma arquitetura muito boa em Nostr, mas ela precisará ser **composta** a partir desses NIPs, e não simplesmente adotada pronta.

## 1. O que já existe em Nostr que ajuda

### 1.1 Descoberta de apps e handlers, NIP-89
O NIP-89 define:
- `kind:31990` para um app publicar como lida com certos kinds
- `kind:31989` para usuários recomendarem apps/handlers para kinds específicos

Isso é interessante porque se aproxima bastante de um modelo de descoberta de skills:
- o **skill publisher** pode publicar um manifesto tipo handler
- usuários/curadores podem publicar recomendações
- clientes podem buscar recomendações primeiro no grafo social e depois resolver o manifesto do skill

Ponto forte:
- descoberta descentralizada e social-first

Limitação:
- foi desenhado para **application handlers**, não para skill packages com trust/security/provenance completos

### 1.2 Listas, sets e curadoria, NIP-51
O NIP-51 define listas públicas/privadas e vários tipos de sets.

Isso é ótimo para:
- listas de skills favoritos
- listas de skills aprovados por uma comunidade
- sets temáticos, por exemplo:
  - `bitcoin-wallets`
  - `nostr-publishing`
  - `btcpay-merchant-ops`
  - `safe-for-beginners`
  - `audited-skills`

Também é útil para:
- seguir curadores
- montar feeds de recomendação
- publicar listas privadas de skills internos/experimentais

### 1.3 Labels e classificação, NIP-32
O NIP-32 permite anexar labels a eventos, pubkeys, relays, URLs e tópicos.

Isso pode servir para classificar skills por:
- categoria
- linguagem
- compatibilidade com harnesses
- risco
- status de auditoria
- maturidade
- licença

Exemplos de labels úteis:
- `skill.category:bitcoin`
- `skill.category:nostr`
- `skill.category:btcpay`
- `skill.runtime:codex`
- `skill.runtime:claude-code`
- `skill.runtime:gemini`
- `skill.risk:low`
- `skill.risk:network-write`
- `skill.audit:passed`
- `skill.audit:manual-review-required`

### 1.4 Reports, inclusive malware, NIP-56
O NIP-56 define reports (`kind:1984`) e inclui explicitamente o tipo `malware`.

Isso é uma peça importante para um ecossistema de skills porque dá uma base para:
- denunciar skills maliciosos
- denunciar publishers comprometidos
- denunciar blobs/artefatos infectados
- distribuir sinais de risco via grafo social

Limitação importante:
- report sozinho não basta, porque pode ser manipulado, brigado e spammado
- precisa ser combinado com confiança social, curadores e políticas locais

### 1.5 Badges e attestations, NIP-58
O NIP-58 permite badges emitidos por terceiros e escolhidos pelo usuário no perfil.

Isso pode virar uma camada de atestação, por exemplo:
- `audited-by-freedom-skills`
- `trusted-publisher`
- `bitcoin-domain-expert`
- `claude-code-compatible`
- `reproducible-artifact`

Uso interessante:
- badges emitidos por auditores, comunidades ou mantenedores respeitados
- clientes podem elevar o ranking de skills com badges de emissores confiáveis

### 1.6 Repositórios e código no Nostr, NIP-34
O NIP-34 cobre anúncio de repositórios Git, patches, PRs e issues via Nostr.

Isso sugere um caminho forte para skills:
- cada skill pode apontar para um repo anunciado em Nostr
- o source of truth do código fica versionado e auditável
- reputação do skill pode se apoiar também no histórico do repositório e dos maintainers

Isso é melhor do que guardar só um blob solto, porque:
- facilita revisão de diff
- facilita provenance
- facilita auditoria humana

### 1.7 Serviços/agentes sob demanda, NIP-90
O NIP-90 é mais sobre Data Vending Machines, isto é, pedidos de computação/resultado.

Não resolve registry de skill, mas ajuda a pensar a camada de **uso**:
- skill como serviço remoto
- agente como skill executável sob demanda
- comparação entre múltiplos provedores para o mesmo tipo de tarefa

Pode ser útil se o projeto quiser suportar dois modelos:
- **skill package local**
- **skill/service remoto**

## 2. O que já existe fora de Nostr e vale reaproveitar

Para segurança, o Nostr sozinho não basta. O ideal é combinar Nostr com práticas modernas de supply chain.

### 2.1 TUF
O TUF, The Update Framework, é focado em segurança de sistemas de update, incluindo cenários em que o repositório ou chaves são comprometidos.

Ideias reaproveitáveis:
- múltiplos papéis de assinatura
- rotação e revogação de chaves
- thresholds, por exemplo exigir 2 de 3 assinaturas para um skill “trusted”
- metadata separada dos artefatos

### 2.2 in-toto
O in-toto registra quais passos foram executados, por quem e em que ordem dentro da supply chain.

Ideias reaproveitáveis:
- provar de qual commit saiu o skill
- provar quem empacotou
- provar que os testes passaram
- provar que o artefato publicado corresponde ao source revisado

### 2.3 SLSA
O SLSA é um framework de níveis de integridade para artefatos de software.

Ideias reaproveitáveis:
- provenance verificável
- builds auditáveis
- hardening gradual por níveis
- linguagem comum para dizer se um skill tem baixa ou alta garantia

### 2.4 Assinatura e provenance de artefatos
Mesmo quando o registry é descentralizado, ainda vale usar ideias do mundo de pacotes/containers:
- assinatura criptográfica dos manifests
- hash de conteúdo de cada arquivo
- provenance do build/pacote
- política local de verificação antes de instalar/executar

## 3. Proposta de arquitetura Nostr-first para discovery de skills

### 3.1 Entidades principais
1. **Skill manifest**
   - evento descrevendo o skill, versão, publisher, runtime compatível, capabilities e artefatos
2. **Skill recommendation**
   - evento de recomendação/curadoria por usuários ou comunidades
3. **Skill labels**
   - classificação, compatibilidade, risco, auditoria
4. **Skill reports**
   - malware, spam, impersonation, unsafe behavior
5. **Skill badges / attestations**
   - emitidos por auditores/curadores confiáveis

### 3.2 Modelo mínimo
Uma primeira versão poderia ser:
- usar um evento tipo manifesto do skill, possivelmente inspirado em **NIP-89**
- usar **NIP-51** para listas e catálogos curados
- usar **NIP-32** para labels e compatibilidade
- usar **NIP-56** para reports
- usar **NIP-58** para badges de confiança
- usar **NIP-34** quando o skill tiver repo Git associado

### 3.3 Ranking / recomendação
A recomendação pode combinar:
- quem você segue
- curadores seguidos
- badges emitidos por emissores que você confia
- sinais de uso/instalação
- quantidade e peso social de reports negativos
- compatibilidade com o harness em uso
- proximidade temática com o contexto atual

### 3.4 Sinal de uso
Dá para pensar em eventos opcionais de uso, por exemplo:
- install
- execute
- success
- failure
- uninstall
- bookmark

Mas isso precisa ser tratado com cuidado por privacidade. O default ideal provavelmente é:
- uso local e privado
- opt-in explícito para publicação
- ou publicação agregada/anônima quando fizer sentido

## 4. Como reduzir o risco de skill malicioso

## Resposta curta
**Não dá para garantir 100%.**

O que dá para fazer é construir um sistema de **redução de risco em camadas**.

### 4.1 Manifesto com capabilities explícitas
Cada skill deve declarar claramente:
- quais ferramentas pode pedir
- se precisa de shell
- se precisa de rede
- se precisa escrever em disco
- se precisa acessar segredos
- se precisa enviar mensagens para fora
- quais harnesses/runtime suporta

Exemplo de classes de risco:
- `read-only`
- `workspace-write`
- `network-read`
- `network-write`
- `exec-shell`
- `secret-access`
- `external-messaging`

### 4.2 Permissões vêm da plataforma, não do skill
Regra importante:
- o skill pode **declarar** o que gostaria de usar
- mas quem concede permissão é a **plataforma/política do usuário**, nunca o skill sozinho

Ou seja, o manifesto não pode auto-conceder poderes.

### 4.3 Artefatos com hash e assinatura
Para cada versão do skill:
- hash do manifesto
- hash dos arquivos do skill
- assinatura do publisher
- idealmente também assinatura de auditores/curadores

### 4.4 Provenance e reprodutibilidade
Quanto mais sensível o skill, mais vale exigir:
- vínculo com commit Git
- origem do build/pacote
- provenance verificável
- artefato reproduzível ou pelo menos comparável

### 4.5 Sandbox por padrão
Mesmo skill confiável deve rodar com contenção:
- filesystem limitado
- rede limitada
- sem acesso automático a segredos
- sem execução irrestrita de shell
- aprovações para ações sensíveis

### 4.6 Revisão humana e auditoria comunitária
Para skills de maior risco, vale exigir:
- revisão manual
- diff legível
- changelog
- approval gates
- auditoria por mais de uma pessoa ou organização

### 4.7 Trust graph e curadores
Em vez de confiar em “qualquer skill publicado”, o cliente pode priorizar:
- publishers que você segue
- curadores seguidos
- organizações confiáveis
- publishers com badges fortes
- skills sem reports relevantes

### 4.8 Revogação e quarentena
Se um skill ou publisher for comprometido, o sistema precisa suportar:
- revogação de versão
- blacklist local
- labels de alto risco
- quarentena temporária
- remoção de recomendação

### 4.9 Política local por organização
Empresas/comunidades podem manter listas próprias:
- approved skills
- denied skills
- allowlist de publishers
- threshold mínimo de badges/auditoria
- skills permitidos por ambiente

## 5. Modelo prático que parece mais promissor

Se fosse desenhar agora, eu faria assim:

### Camada 1, identidade e publicação
- publisher publica skill manifest assinado
- skill aponta para repo, release ou artefato hasheado
- idealmente também aponta para commit Git

### Camada 2, discovery
- catálogo via listas/sets no Nostr
- descoberta social via follows e curadores
- busca por labels e temas

### Camada 3, reputação
- recommendations
- badges
- labels
- reports
- uso local/telemetria opt-in

### Camada 4, segurança
- verificação de assinatura
- verificação de hash
- política de capabilities
- sandbox
- approval para ações sensíveis
- revogação

## 6. O que eu acho que já existe vs o que ainda falta

### Já existe em forma de building blocks
- descoberta de handlers, NIP-89
- curadoria/listas, NIP-51
- labels, NIP-32
- reports de malware, NIP-56
- badges, NIP-58
- repositórios Git via Nostr, NIP-34
- jobs/serviços sob demanda, NIP-90

### Ainda falta, ou pelo menos não aparece como padrão consolidado
- um **skill manifest** padronizado
- um **modelo de capabilities/permissões** para skills
- um **modelo de provenance** específico para skills
- um **esquema de recommendation** mais padronizado
- uma forma padrão de **revogação** de versões maliciosas
- uma UX boa para explicar risco ao usuário

## 7. Recomendação para o Freedom Skills

Eu seguiria por este caminho:

### Fase 1
- definir um **manifesto de skill** simples
- incluir capabilities, runtime compatível, artefatos e hashes
- manter source em Git e registrar commit/release

### Fase 2
- mapear esse manifesto para publicação via Nostr
- usar NIP-51 para catálogos e curadorias
- usar NIP-32 para classificação e risco

### Fase 3
- adicionar reputação:
  - recommendations
  - badges
  - reports
  - web-of-trust

### Fase 4
- endurecer a segurança:
  - provenance
  - thresholds de assinatura
  - sandbox e policies locais
  - revogação e quarantine

## 8. Minha opinião direta

A parte de **discovery e recommendation** dá para fazer de forma bem elegante em Nostr.

A parte de **segurança** não deve depender só de Nostr.

Nostr é muito bom para:
- identidade
- publicação
- descoberta social
- reputação descentralizada
- revogação social e sinais de risco

Mas a segurança pesada precisa vir da combinação com:
- assinatura de artefatos
- hashes
- provenance
- sandbox
- política local
- revisão humana

Se eu tivesse que resumir em uma linha:

> Nostr resolve bem a camada social do registry, mas não deve ser a única linha de defesa contra skill malicioso.

## 9. Fontes pesquisadas
- NIP-89, Recommended Application Handlers
- NIP-51, Lists
- NIP-32, Labeling
- NIP-56, Reporting
- NIP-58, Badges
- NIP-34, git stuff
- NIP-90, Data Vending Machine
- TUF, The Update Framework
- in-toto
- SLSA
