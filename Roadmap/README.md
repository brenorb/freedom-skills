# Roadmap

Primeira varredura de direções para o projeto Freedom Skills.

Objetivo inicial: identificar tecnologias adjacentes ao Bitcoin, carteiras/ecossistemas mais relevantes e ideias de skills úteis para construir em volta disso.

## 1. Tecnologias adjacentes ao Bitcoin

### Base Bitcoin
- Bitcoin Core, descriptors, PSBT, Miniscript, Taproot, MuSig2
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

## 4. Harnesses / coding agents que vale considerar

Além dos skills por tecnologia, o projeto também pode ganhar muito se pensar em **harnesses** como camada de execução.

### Principais para priorizar
1. **Codex**
   - hoje parece ser o principal no teu fluxo.
   - forte para edição de código, diffs, contexto de repo e execução orientada a tarefa.
2. **Claude Code**
   - muito forte para leitura ampla de codebase, refactors e navegação com bom julgamento.
   - vale tratar como primeira classe.
3. **Gemini CLI**
   - bom para geração, exploração e tarefas de apoio; pode ser útil como alternativa competitiva.

### Secundários que podem fazer sentido
- **Cursor Agent / Cursor CLI**: importante porque muita gente já usa Cursor como ambiente principal.
- **Aider / OpenCode / Goose / Pi**: menos centrais para v1, mas úteis como “adaptadores” ou benchmark de compatibilidade.

### O que padronizar entre harnesses
- seleção de harness por tipo de tarefa
- empacotamento de contexto do repo
- anexação de arquivos relevantes
- modo interativo vs modo batch
- patch/diff/apply
- execução com aprovações/permissões
- sessões persistentes vs one-shot
- troca de modelo e fallback
- custo, latência e qualidade por tarefa

### Ideias de skills ligadas a harnesses
21. **harness-chooser**
    - recomenda Codex, Claude Code, Gemini ou outro conforme a tarefa.
22. **prompt-packager**
    - monta contexto, arquivos e instruções do jeito certo para cada harness.
23. **repo-context-bundler**
    - escolhe e agrupa os arquivos mais úteis antes de chamar o agente.
24. **harness-benchmark**
    - compara qualidade, tempo e custo entre harnesses em tarefas parecidas.
25. **session-orchestrator**
    - gerencia sessões persistentes, retomada de contexto e handoff entre agentes.

## 5. Recortes iniciais que parecem mais promissores

Se a ideia é começar pequeno e útil, eu priorizaria dois eixos em paralelo.

### Eixo A, skills de domínio Bitcoin / sovereign tech
1. **wallet-comparator**
2. **btcpay-ops**
3. **nostr-publisher**
4. **nostr-wallet-connect-helper**
5. **cashu-ops**
6. **bitcoin-research-radar**
7. **bitdevs-ops**

### Eixo B, skills de infraestrutura de agentes / harnesses
1. **harness-chooser**
2. **prompt-packager**
3. **repo-context-bundler**
4. **session-orchestrator**

### Minha recomendação
Se for para focar com disciplina, eu começaria por:
- **Codex + Claude Code + Gemini CLI** como trio principal de harnesses
- e por **3 skills iniciais**:
  - **wallet-comparator**
  - **btcpay-ops**
  - **harness-chooser**

## 6. Próximas perguntas para afinar o projeto
- O foco é usuário final, dev, merchant ou comunidade?
- Queremos skills mais operacionais, mais educativas ou mais analíticas?
- O projeto vai mirar automações locais/CLI ou integrações remotas/APIs?
- O recorte principal é Bitcoin puro, Lightning, Nostr, ou “sovereign tech” em volta de Bitcoin?
- Queremos começar por um catálogo amplo ou por 3 skills fortes e bem acabadas?
- Queremos que o projeto seja **multi-harness desde o início** ou comece por Codex e depois expanda?
- A abstração principal deve ser por **skill** ou por **harness adapter**?

## 7. Pesquisa separada
- [[skill-discovery-and-trust.md]] — discovery, recommendation e trust de skills com foco em Nostr e mitigação contra skill malicioso

## 8. Fontes iniciais para expandir depois
- Bitcoin.org wallet chooser
- Bitcoin Optech
- Fedimint docs
- Cashu docs
- sites/docs oficiais de Sparrow, Electrum, Nunchuk, Phoenix, Zeus, BTCPay, Nostr
- docs oficiais de Codex, Claude Code, Gemini CLI e Cursor

## 9. Observações
- Isto é um mapa inicial, não uma taxonomia final.
- Vale validar uso real e prioridade antes de abrir muitas frentes.
- A combinação mais natural hoje parece: **Bitcoin + Lightning + Nostr + BTCPay + Cashu/Fedimint**.
- No eixo de agents, a combinação mais natural hoje parece: **Codex + Claude Code + Gemini CLI**, com Cursor como opcional importante.
