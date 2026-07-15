# Freedom Skills

![Freedom Skills helps turn complex freedom technologies into practical workflows](assets/07-freedom-skills-helps.png)

Freedom Skills is an open library of reusable skills, hooks, and MCP integrations that help AI agents work with Bitcoin, Nostr, privacy tools, and other freedom technologies.

There are many free and open-source freedom technologies, but using them often means learning a new interface, terminology, setup process, and set of security assumptions for every tool.

Freedom Skills packages that knowledge into reusable, agent-ready workflows. Install a skill in a compatible agent and it can recognize when the skill applies, follow the documented workflow, use the relevant tools, and surface important caveats.

The goal is to make freedom technologies as convenient to use as mainstream apps, without making convenience depend on centralized, data-extracting services.

![From raw tools to tested skills, guided use, safer action, and human-rights work](assets/00-raw-tools-to-human-rights.png)

Freedom technologies can help people communicate, transact, preserve information, and coordinate with greater autonomy. By making these tools easier for agents to understand and operate, Freedom Skills aims to reduce the practical barriers that keep them out of reach for developers, activists, researchers, and human-rights defenders.

## What is an Agent Skill?

An Agent Skill is a portable package of instructions and resources that gives an AI agent specialized knowledge for a specific task.

At minimum, a skill contains a `SKILL.md` file. It can also include scripts, references, templates, and other resources. Compatible agents discover skills from their metadata and load the detailed instructions only when they are relevant.

Freedom Skills follows the open [Agent Skills standard](https://agentskills.io).

## Available skills

### Communication and coordination

| Skill | What it enables |
|---|---|
| [`nostr-cli`](skills/nostr-cli/) | Nostr account setup, relay management, profiles, posts, replies, DMs, follows, and long-form publishing. |
| [`signal-cli`](skills/signal-cli/) | Private Signal messages and attachments, account and contact inspection, group workflows, setup, and troubleshooting. |

### Money and payments

| Skill | What it enables |
|---|---|
| [`mdk-agent-wallet`](skills/mdk-agent-wallet/) | Self-custodial agent wallets for Lightning payments, balances, payment history, and L402 access. |
| [`mdk-l402-api`](skills/mdk-l402-api/) | Paid Next.js or Express APIs using HTTP 402 and Money Dev Kit Lightning payment flows. |
| [`mdk-mcp`](skills/mdk-mcp/) | Connections between coding agents and Money Dev Kit MCP servers. |
| [`mdk-nextjs-checkout`](skills/mdk-nextjs-checkout/) | Money Dev Kit Lightning checkout in Next.js App Router applications. |
| [`mdk-replit-checkout`](skills/mdk-replit-checkout/) | Money Dev Kit Lightning checkout in Replit Vite, React, and Express applications. |

### Privacy, safety, and resilience

| Skill | What it enables |
|---|---|
| [`unbroker`](skills/unbroker/) | Find and remove personal information from data brokers and people-search sites, with consent-gated automation, guided human steps, and recurring rechecks. |
| [`rampart-hook-configurator`](skills/rampart-hook-configurator/) | Install, configure, tune, and verify the paired Rampart hooks for reducing sensitive-data exposure in agent workflows. |
| [`skillspector`](skills/skillspector/) | Security scans for individual skills or skill repositories before installation. |
| [`timelock-sh`](skills/timelock-sh/) | Time-locking, inspecting, and decrypting files with `timelock.sh`. |

### Sharing, publishing, and preservation

| Skill | What it enables |
|---|---|
| [`p2p-transfer-filepizza`](skills/p2p-transfer-filepizza/) | Sharing local files through temporary peer-to-peer links with FilePizza. |
| [`wayback-archive`](skills/wayback-archive/) | Archiving webpages, checking snapshots, creating stable citation links, and batch archiving URLs. |

### Research and media

| Skill | What it enables |
|---|---|
| [`domain-intel`](skills/domain-intel/) | Passive domain reconnaissance, including subdomains, SSL certificates, WHOIS, DNS, and availability checks. |
| [`fast-transcript`](skills/fast-transcript/) | Transcribe and inspect audio and video with the local `fscript` CLI, including local files and supported remote URLs. |

### Product and developer workflows

| Skill | What it enables |
|---|---|
| [`mo-ux-vibedesign-btc`](skills/mo-ux-vibedesign-btc/) | Senior Bitcoin UX reviews covering interviews, copy, flows, wireframes, mockups, and benchmarks. |

## Hooks

The repository also includes a portable [Rampart pre-send and post-send hook pair](hooks/rampart-pre-send/).

The pre-send hook redacts selected personal information before a request reaches a model. The post-send hook restores placeholders in the model's reply. The pair supports raw text and JSON payloads, shared session state, configurable labels, and fail-open or fail-closed behavior.

Read the [hook documentation](hooks/rampart-pre-send/README.md) for details.

## Community and contributing

Freedom Skills is an open-source community project. Anyone can propose a new skill for a freedom technology, improve an existing workflow, add scripts or references, write tests, or report issues.

Contributions are made through pull requests. A useful contribution should explain the workflow, its intended users, prerequisites, safety assumptions, and any relevant tests or examples.
