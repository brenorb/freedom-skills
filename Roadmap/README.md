# Roadmap

Primeira varredura de direções para o projeto Freedom Skills.

Objetivo inicial: identificar tecnologias adjacentes ao Bitcoin, carteiras/ecossistemas mais relevantes e ideias de skills úteis para construir em volta disso.

## Notas adicionais

- [skills-benchmarks-landscape.md](./skills-benchmarks-landscape.md)
  - levantamento do que existe hoje em benchmarks de skills e benchmarks adjacentes
- [skills-benchmark-strategy.md](./skills-benchmark-strategy.md)
  - proposta de como o Freedom Skills pode reaproveitar benchmarks existentes e onde precisa construir os seus

## 1. Tecnologias adjacentes ao Bitcoin

### Base Bitcoin
- Bitcoin Core, descriptors, PSBT, Miniscript, Simplicity, Taproot, MuSig2
- Lightning Network, LNURL, BOLT12, Nostr Wallet Connect (NWC)
- Hardware wallets, multisig, watch-only, xpubs, descriptors
- Self-custody UX, backup/recovery, signing flows

### Camadas e protocolos próximos
- **Nostr**: identidade, mensagens, social, zaps, NWC, automações ligadas a chaves/eventos.
- **BTCPay Server**: pagamentos, lojas, invoices, webhooks, automação para creators/comércios.
- **Fedimint**: e-cash federado, custódia comunitária, onboarding simples e privacidade.
- **Cashu**: e-cash Chaumiano, mints, wallets, vouchers, paywalls e micropagamentos.
- **Liquid**: asset issuance, L-BTC, swaps, treasury e casos institucionais.
- **RGB**: assets/smart contracts client-side sobre Bitcoin.
- **Taproot Assets**: emissão e movimentação de assets usando a stack de Lightning/Taproot.
- **Ark**: pagamentos Bitcoin com foco em UX e escalabilidade, ainda cedo mas conceitualmente promissor.
- **Silent Payments / PayJoin / CoinJoin / privacy tooling**: privacidade e composição de pagamentos.
- **DLCs**: contratos discretos para apostas, hedge e mercados condicionais.

### Tecnologias de comunicação/comunidade que fazem sentido ao lado de Bitcoin
- **SimpleX**: mensageria privada, sem identificador global persistente.
- **Matrix**: comunidades, bridging, bots e coordenação open source.
- **White Noise / Noise-style secure messaging**: linha de ferramentas de comunicação privada e resistente à vigilância.
- **Signal**: menos aberto para integrações, mas UX e referência de privacidade importam.

## 2. Carteiras e stacks mais relevantes para observar

### Mobile / uso cotidiano
- **Phoenix**: Lightning com boa UX, forte referência para self-custody simples.
- **Blixt**: Lightning power-user/mobile node.
- **Muun**: UX muito forte, modelo híbrido, boa referência de onboarding.
- **Wallet of Satoshi**: enorme adoção histórica por simplicidade, apesar de custodial.
- **Blink**: custodial muito usada em onboarding Lightning.
- **Aqua**: Bitcoin + Liquid, ponte interessante para assets e stablecoins.
- **BlueWallet**: referência histórica em mobile/watch-only/Lightning.
- **Zeus**: controle de node Lightning e operações mais avançadas.

### Hardware / cold storage
- **Bitkey**
- **Coldcard**
- **Ledger**
- **Trezor**
- **Jade**
- **Passport**

### Desktop / multisig / advanced
- **Sparrow**
- **Electrum**
- **Nunchuk**
- **Specter Desktop**

### Ecash / Fedimint / Cashu
- **Fedi**
- **Cashu wallets** (ecosistema de mints, vouchers, apps web/mobile/CLI)

### O que aprender com as carteiras mais usadas
- onboarding e backup
- receive/send extremamente simples
- fee selection sem confundir
- watch-only e separação entre observação e assinatura
- hardware wallet pairing
- integração com LNURL, NWC, BTCPay e Nostr
- recovery, migration, export/import, compatibilidade entre wallets

## 3. Ideias de skills interessantes para criar

### Bitcoin infra / custody
1. **bitcoin-wallet-audit**
   - inspeciona setup de wallet, backups, multisig, xpub/descriptors, riscos comuns.
2. **psbt-assistant**
   - ajuda a montar, revisar e explicar PSBTs antes de assinar.
3. **sparrow-helper**
   - tarefas comuns no Sparrow: labels, import/export, UTXO hygiene, coin control.
4. **multisig-checklist**
   - cria/valida checklist de setup multisig, recovery e rotação de dispositivos.

### Lightning / payments
5. **lightning-ops**
   - invoices, LNURL, liquidity, node checks, canais, swaps, backups.
6. **btcpay-ops**
   - instalar/configurar BTCPay, criar lojas, webhooks, integração com produtos/assinaturas.
7. **ln-onboarding**
   - guia pessoas para escolher carteira Lightning conforme perfil: custodial, self-custody, node, merchant.

### Nostr / identity / creator economy
8. **nostr-publisher**
   - publicar notas, threads, artigos, eventos e sincronizar conteúdos.
9. **nostr-profile-ops**
   - perfil, relays, nip-05, listas, follows, verificação de presença.
10. **nostr-wallet-connect-helper**
    - conectar apps via NWC, diagnosticar permissões e limites.
11. **nostr-event-promoter**
    - divulgar meetups/Bitdevs em múltiplos relays e formatos.

### Ecash / Fedimint / privacy payments
12. **cashu-ops**
    - escolher mint, emitir/resgatar ecash, vouchers, análise de risco e UX.
13. **fedimint-guide**
    - comparar federações, onboarding, casos de uso comunitários.
14. **privacy-payment-advisor**
    - ajuda a escolher entre on-chain, Lightning, Cashu, Fedimint, Liquid conforme contexto.

### Comunidade / educação / pesquisa
15. **bitcoin-research-radar**
    - acompanha Bitcoin Optech, BIPs, newsletters, mudanças de wallets e infra.
16. **bitdevs-ops**
    - pauta, divulgação, follow-up, relatório, pagamentos e checklist do evento.
17. **wallet-comparator**
    - compara carteiras por self-custody, privacidade, Lightning, hardware, open source e perfil de uso.

### Comunicação privada / comunidade técnica
18. **simplex-helper**
    - onboarding e operação de grupos/canais no ecossistema SimpleX.
19. **matrix-community-ops**
    - rooms, bridges, bots, moderação e integrações.
20. **secure-comms-chooser**
    - recomenda stack de comunicação conforme ameaça, comunidade e UX.

## 4. Público prioritário que parece mais importante

Um recorte forte para o Freedom Skills pode ser:
- **ativistas de liberdade e direitos humanos**
- pessoas em ambientes de censura, vigilância ou repressão
- usuários **não técnicos** que precisam montar projetos, se comunicar melhor e reduzir risco sem virar especialistas

Isso muda a priorização.

Não basta ter skills “poderosas”. Elas precisam ser:
- guiadas
- opinativas
- com linguagem simples
- seguras por padrão
- com alertas claros de privacidade e segurança
- úteis para alguém que quer **fazer uma coisa concreta** sem entender toda a stack por trás

## 5. Harnesses / agents que vale priorizar

Além dos skills por tecnologia, o projeto também ganha muito se pensar nos **harnesses/agentes** como camada de execução e UX.

### Mais importantes agora
1. **OpenClaw**
   - importante como camada prática de orquestração, automação, memória, sessões e ferramentas.
   - especialmente valioso para fluxos guiados e assistentes úteis para não técnicos.
2. **Hermes**
   - faz sentido tratar como peça importante de testes e experiência de agente, especialmente se for parte do ecossistema que vocês querem comparar/validar.
3. **Codex**
   - segue como principal para código, diffs, contexto de repo e tarefas de implementação.

### Também vale tratar como primeira classe
- **Claude Code**: muito forte para leitura ampla de codebase, refactors e navegação com bom julgamento.
- **Goose**: vale tratar como importante no ecossistema de testes e compatibilidade entre agentes.

### Secundários por enquanto
- **Gemini CLI**: útil para exploração, geração e tarefas de apoio, mas não parece central agora.
- **Cursor Agent / Cursor CLI**: ainda importante, mas menos central do que OpenClaw/Hermes para o rumo que você descreveu.
- **Aider / OpenCode / Pi**: bons como adaptadores, benchmark e compatibilidade futura.

### O que padronizar entre harnesses
- seleção do melhor harness por tipo de tarefa
- empacotamento de contexto do repo e da conversa
- anexação de arquivos relevantes
- modo interativo vs modo batch
- patch/diff/apply
- execução com aprovações/permissões
- sessões persistentes vs one-shot
- fallback de modelo/runtime
- custo, latência e qualidade por tarefa
- suporte a fluxos guiados para usuários não técnicos

### Ideias de skills ligadas a harnesses
21. **harness-chooser**
    - recomenda OpenClaw, Hermes, Codex, Claude Code, Goose, Gemini ou outro conforme a tarefa e o perfil do usuário.
22. **prompt-packager**
    - monta contexto, arquivos e instruções do jeito certo para cada harness.
23. **repo-context-bundler**
    - escolhe e agrupa os arquivos mais úteis antes de chamar o agente.
24. **harness-benchmark**
    - compara qualidade, tempo e custo entre harnesses em tarefas parecidas.
25. **session-orchestrator**
    - gerencia sessões persistentes, retomada de contexto e handoff entre agentes.
26. **guided-agent-mode**
    - adapta a experiência do agente para usuários não técnicos, com linguagem simples e checkpoints explícitos.

## 6. Skills básicas que podem ajudar ativistas e pessoas não técnicas

Além dos skills de tecnologia específica, parece muito promissor ter uma camada de skills mais básicas e guiadas.

27. **secure-project-bootstrap**
    - ajuda a tirar um projeto do zero com estrutura mínima, checklist, nomes, pastas, prioridades e riscos.
28. **threat-model-lite**
    - ajuda a pessoa a pensar: do que preciso me proteger, de quem, e o que é risco alto vs baixo.
29. **private-comms-setup**
    - compara e ajuda a configurar ferramentas como Signal, SimpleX, Matrix, Nostr e afins, com tradeoffs claros.
30. **opsec-checkup**
    - checklist simples de segurança operacional: dispositivo, contas, backups, 2FA, links, arquivos, exposição.
31. **publish-safely**
    - ajuda a publicar texto, site, manifesto, formulário ou campanha com menos risco de vazamento de metadados e erros bobos.
32. **privacy-alerts**
    - revisa um plano/projeto e aponta alertas de privacidade, rastreabilidade e exposição.
33. **secure-file-sharing-guide**
    - recomenda formas de compartilhar arquivos, links e mídias com menos risco.
34. **gpg-ops-guide**
    - gera/gerencia chaves GPG, assina/verifica arquivos e mensagens, e orienta boas práticas de distribuição/revogação de chave.
35. **backup-and-recovery-drill**
    - ensina a fazer backup e recuperar acesso sem depender de memória ou improviso.
36. **campaign-ops-lite**
    - ajuda a organizar ação, evento, campanha ou grupo pequeno com comunicação, papéis, agenda e follow-up.
37. **incident-checklist**
    - checklist para quando algo der errado: conta comprometida, aparelho perdido, link suspeito, vazamento etc.
38. **tool-risk-explainer**
    - explica em linguagem simples por que uma ferramenta pode ser arriscada ou inadequada para um certo contexto.
39. **ai-request-coach**
    - ajuda usuários não técnicos a transformar pedidos vagos em pedidos melhores para a IA, sugerindo objetivo, contexto, restrições, formato de saída e perguntas de esclarecimento.

## 7. Recortes iniciais que parecem mais promissores

Se a ideia é começar pequeno e útil, eu priorizaria três eixos em paralelo.

### Eixo A, domínio Bitcoin / sovereign tech
1. **wallet-comparator**
2. **btcpay-ops**
3. **nostr-publisher**
4. **nostr-wallet-connect-helper**
5. **cashu-ops**
6. **bitcoin-research-radar**
7. **bitdevs-ops**

### Eixo B, infraestrutura de agentes / harnesses
1. **harness-chooser**
2. **prompt-packager**
3. **repo-context-bundler**
4. **session-orchestrator**
5. **guided-agent-mode**

### Eixo C, onboarding e segurança para não técnicos
1. **ai-request-coach**
2. **secure-project-bootstrap**
3. **threat-model-lite**
4. **private-comms-setup**
5. **opsec-checkup**
6. **privacy-alerts**
7. **publish-safely**
8. **incident-checklist**

### Minha recomendação
Se for para focar com disciplina, eu começaria por:
- **OpenClaw + Hermes + Codex** como trio mais importante para testar experiência e execução
- e por **6 skills iniciais**:
  - **ai-request-coach**
  - **secure-project-bootstrap**
  - **threat-model-lite**
  - **private-comms-setup**
  - **wallet-comparator**
  - **harness-chooser**

Isso me parece um começo melhor para o público que você descreveu do que começar só por skills mais técnicas.

## 8. Próximas perguntas para afinar o projeto
- O foco principal é ativista não técnico, operador técnico, merchant, ou comunidade Bitcoin?
- Queremos skills mais operacionais, mais educativas ou mais analíticas?
- O projeto vai mirar automações locais/CLI ou integrações remotas/APIs?
- O recorte principal é Bitcoin puro, Lightning, Nostr, ou “sovereign tech” em volta de Bitcoin?
- Queremos começar por um catálogo amplo ou por poucas skills muito boas?
- Queremos que o projeto seja multi-harness desde o início?
- A abstração principal deve ser por **skill**, por **harness adapter** ou por **guided workflow**?
- Quais níveis de risco aceitaremos para usuários não técnicos?
- Quanto dessa ajuda de prompting deve acontecer automaticamente versus em modo assistido, com perguntas antes de agir?

## 9. Pesquisa separada
- [[skill-discovery-and-trust.md]] — discovery, recommendation e trust de skills com foco em Nostr e mitigação contra skill malicioso
- [[ai-request-coach.md]] — spec inicial para uma skill focada em ajudar usuários não técnicos a pedir melhor para a IA

## 10. Fontes iniciais para expandir depois
- Bitcoin.org wallet chooser
- Bitcoin Optech
- Fedimint docs
- Cashu docs
- sites/docs oficiais de Sparrow, Electrum, Nunchuk, Phoenix, Zeus, BTCPay, Nostr
- docs oficiais de OpenClaw, Hermes, Codex, Claude Code, Goose, Gemini CLI e Cursor

## 11. Observações
- Isto é um mapa inicial, não uma taxonomia final.
- Vale validar uso real e prioridade antes de abrir muitas frentes.
- A combinação mais natural hoje parece: **Bitcoin + Lightning + Nostr + BTCPay + Cashu/Fedimint**.
- No eixo de agents, a combinação mais natural agora parece: **OpenClaw + Hermes + Codex**, com Claude Code e Goose como complementos fortes.
- Para o público descrito, UX guiada e segurança por padrão importam tanto quanto capacidade técnica.
