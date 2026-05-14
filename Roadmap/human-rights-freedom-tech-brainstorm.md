# Human Rights And Freedom-Tech Skill Brainstorm

As of 2026-05-14.

This brainstorm is intentionally broader than the current Bitcoin, private communications, and cryptography roadmap. It focuses on additional skill areas that could matter to human rights defenders, freedom activists, dissidents, journalists, community organizers, and non-technical users operating in hostile environments.

The list below tries to avoid repeating the ideas already captured in the main roadmap documents.

## Most Promising Directions

These are the strongest candidates from this brainstorm because they combine real user value with plausible implementation paths.

### How to read the labels

- `FOSS-heavy`: the skill would likely rely on open-source software, self-hostable tools, or standard open protocols.
- `Non-technical-heavy`: the skill is mainly workflow, judgment, coordination, or human process rather than software operation.
- Many of the best ideas are hybrid. That is a feature, not a flaw.

| Skill | What it does | FOSS-heavy | Non-technical-heavy | Likely implementation surface |
| --- | --- | --- | --- | --- |
| `evidence-intake` | Receives photos, videos, audio, and written testimony, then organizes them with time, place, incident context, source notes, and handling status. | `Medium` | `High` | Filesystem workflows, OCR, hashing, structured templates, case folders |
| `media-redaction` | Removes faces, plates, names, voices, and other identifiers from sensitive media before publication or sharing. | `High` | `Medium` | `ffmpeg`, image tooling, OCR, speech-to-text, blur/redaction pipelines |
| `metadata-scrubber` | Cleans EXIF, author names, revision history, embedded previews, and other metadata that can reveal source, device, or location. | `High` | `Low` | `exiftool`, `mat2`, PDF/image/video metadata tooling |
| `mirror-network-builder` | Creates a replication plan across multiple hosts, formats, and delivery channels so material survives takedowns and blocking. | `High` | `Medium` | static site tooling, object storage, rsync, IPFS-style distribution, archive workflows |
| `onion-publisher` | Publishes `.onion` versions of sites, pages, and documents for censorship resistance and alternate reachability. | `High` | `Low` | Tor hidden services, static sites, local web servers, deployment scripts |
| `persona-separator` | Helps users separate public, organizational, pseudonymous, and operational identities so they do not leak into one another. | `Low` | `High` | decision trees, profile/account mapping, checklists, browser/device profile separation |
| `secure-intake-form-builder` | Designs safer forms with minimal data collection, clearer consent language, and lower risk for whistleblowers, victims, and beneficiaries. | `Medium` | `High` | form stacks, schema guidance, consent templates, data minimization checks |
| `anonymous-tipline-setup` | Helps groups set up an anonymous reporting channel with better triage, less improvisation, and fewer accidental disclosures. | `Medium` | `High` | self-hosted forms, inbox routing, ticketing, secure submission patterns |
| `field-kit-checklist` | Organizes the physical and digital kit for protests, documentation missions, field reporting, or emergency support work. | `Low` | `High` | checklists, packing logic, equipment inventories, print/export kits |
| `detainee-support-coordinator` | Coordinates what happens after a detention: logs, assigned tasks, family contact, legal handoff, and follow-up. | `Low` | `High` | workflow templates, status tracking, contact trees, incident runbooks |
| `claim-verifier` | Verifies dates, locations, claims, quotes, and numbers before they become advocacy material, testimony, or a public statement. | `Medium` | `High` | search, structured fact tables, source comparison, citation workflow |
| `tool-migration-guide` | Helps a group leave an unsafe or brittle platform and move to a better one without breaking operations in the middle of the transition. | `Medium` | `High` | migration checklists, import/export guidance, user comms, permissions review |

## Software-First, Hybrid, And Human-Process-First

This list is not purely non-technical.

### Software-first ideas

These are strongly tied to open-source software, self-hosting, or technical automation:

- `media-redaction`
- `metadata-scrubber`
- `mirror-network-builder`
- `onion-publisher`
- `anonymous-tipline-setup`
- `tool-migration-guide`
- `secure-intake-form-builder`
- `claim-verifier`

### Hybrid ideas

These are part software and part operational practice:

- `evidence-intake`
- `persona-separator`
- `field-kit-checklist`
- `detainee-support-coordinator`

### Human-process-first ideas

These are mainly coordination, judgment, triage, consent, workflow, and training:

- many of the organization, intake, advocacy, and care skills later in this document

## 1. Documentation, Evidence, And Testimony

- `evidence-intake` — receives photos, videos, audio, and testimony and organizes them with time, place, context, and handling notes.
- `chain-of-custody-lite` — creates a lightweight evidence-preservation workflow so material is easier to defend later.
- `media-redaction` — removes faces, plates, names, voices, and other identifying details from sensitive material.
- `metadata-scrubber` — strips EXIF, author names, revision history, filenames, and other revealing metadata.
- `witness-interview-guide` — helps conduct witness interviews with clearer structure and fewer leading questions.
- `testimony-structurer` — turns a raw account into a chronological and internally consistent testimony draft.
- `abuse-pattern-mapper` — groups incidents by location, unit, method, date range, or recurring actor.
- `evidence-crosslinker` — links media, witness accounts, and documents that refer to the same incident.
- `source-consent-check` — checks what can be published, under what name, and with what risks.
- `evidence-export-packager` — packages evidence for lawyers, journalists, archives, or partner organizations.
- `forensic-timeline-builder` — assembles incident timelines from multiple fragmented sources.
- `document-authenticity-check` — helps assess whether a PDF, memo, or screenshot appears manipulated or inconsistent.
- `screenshot-provenance-helper` — records origin, capture context, and supporting notes for screenshots.
- `ocr-translate-redact` — extracts text, translates it, and redacts dangerous details in images or documents.
- `evidence-priority-sorter` — separates strong, weak, duplicate, and risky-to-publish evidence.

## 2. Publishing, Preservation, And Takedown Resistance

- `mirror-network-builder` — creates a multi-channel replication plan for important content.
- `onion-publisher` — publishes `.onion` versions of sites and documents.
- `ipfs-publisher` — packages and publishes content through IPFS-like distribution flows.
- `archive-seed` — submits pages and files to archiving services and preserves hashes and retrieval links.
- `takedown-resilience-planner` — prepares fallback channels before a site, page, or account gets removed.
- `static-site-emergency-kit` — generates a minimal static site for campaigns, emergency statements, or incident updates.
- `low-bandwidth-publisher` — creates lightweight versions of important content for slow or unreliable networks.
- `offline-drop-packager` — assembles HTML, PDF, ZIP, or media bundles for USB, SD card, LAN, or offline relay distribution.
- `censorship-fallback-router` — picks alternate publication and access channels when the main one is blocked.
- `petition-resilience-kit` — replicates petitions or forms across more resilient hosting surfaces.
- `press-room-builder` — creates a lightweight press room with media assets, timeline, contacts, and key facts.
- `campaign-microsite-builder` — builds a simple campaign or incident microsite without depending on a fragile central platform.

## 3. Access, Circumvention, And Hostile-Network Navigation

- `anti-blocking-setup` — configures layered access options for bypassing basic to moderate censorship.
- `browser-hardening` — hardens a browser against leakage, fingerprinting, and contaminated sessions.
- `safe-search-mode` — guides sensitive research with less exposure of account history and browsing traces.
- `link-safety-gate` — evaluates suspicious links before a user opens them.
- `download-safety-check` — checks signatures, hashes, provenance, and risk before opening downloads.
- `wifi-risk-check` — reviews the risk of public Wi-Fi, captive portals, and local interception.
- `cross-border-mode` — prepares a lower-exposure digital posture before crossing borders or checkpoints.
- `device-checkpoint-prep` — helps reduce what is exposed before device inspection or seizure risk.
- `travel-comms-plan` — prepares contact, fallback, and check-in routines for sensitive travel.
- `shutdown-survival-kit` — assembles a playbook for unstable connectivity or internet shutdown conditions.

## 4. Identity, Accounts, And Compartmentalization

- `persona-separator` — separates public, internal, pseudonymous, and operational identities.
- `account-compartment-builder` — maps which accounts, browsers, profiles, and devices belong to which role.
- `alias-hygiene` — reduces overlap across usernames, email addresses, phone numbers, and bios.
- `burner-phone-setup` — prepares a narrowly scoped phone for temporary or high-risk use.
- `burner-browser-profile` — creates isolated browser profiles for research, publishing, and administration.
- `contact-book-sanitizer` — cleans and segments contacts to reduce lateral exposure.
- `2fa-migration-helper` — safely migrates authentication factors across devices and methods.
- `recovery-contact-planner` — organizes account recovery without creating bigger exposure.
- `shared-account-exit-plan` — removes former volunteers or admins cleanly from shared systems.
- `least-privilege-audit` — reviews who really needs access to what.
- `identity-leak-scanner` — looks for obvious public links across profiles, domains, bios, and infra.
- `doxxing-surface-review` — spots public exposure of address, routine, employer, family, or historical data.

## 5. Team Coordination, Roles, And Organizational Security

- `volunteer-intake-secure` — screens and onboards volunteers without collecting unnecessary personal data.
- `role-splitting-designer` — separates responsibilities so one compromise does not expose everything.
- `cell-structure-planner` — helps groups design lower-fragility operational structures.
- `handoff-protocol` — standardizes safe handoff of context between people or teams.
- `need-to-know-router` — routes sensitive information only to those who need it.
- `sensitive-meeting-prep` — prepares high-risk meetings with rules, agenda, and post-meeting handling.
- `minutes-redactor` — converts raw meeting notes into a safer circulation version.
- `decision-log-sanitizer` — preserves institutional memory without oversharing sensitive context.
- `access-offboarding` — runs a clean offboarding checklist for staff, volunteers, or collaborators.
- `conflict-deescalation-playbook` — helps teams respond when tension, infiltration fear, or trust breakdown appears.
- `rumor-control-desk` — slows down internal rumor spirals by forcing verification before escalation.
- `trust-onboarding` — structures access and trust as a gradual process instead of an all-at-once jump.

## 6. Research, Verification, And Information Defense

- `claim-verifier` — checks claims, dates, locations, and quotations before publication.
- `rapid-osint-brief` — builds a quick brief on an actor, institution, event, company, or policy.
- `narrative-watch` — tracks how an issue is being framed across channels and audiences.
- `disinfo-triage` — classifies content that may be false, manipulated, or coordinated.
- `bot-amplification-check` — looks for basic signs of synthetic or coordinated amplification.
- `press-quote-checker` — validates that numbers and quotes are being repeated accurately.
- `translation-sanity-check` — catches high-impact translation mistakes in legal, political, or security-sensitive contexts.
- `fact-pack-builder` — creates compact fact packets for spokespeople, partners, or allies.
- `source-credibility-grid` — compares sources without relying only on authority or popularity.
- `legislation-monitor` — tracks laws, rules, and policy proposals that threaten civil liberties.
- `institution-map` — maps agencies, companies, funders, contractors, and power relationships.
- `incident-pattern-radar` — detects repeated abuse patterns by place, date, actor, or tactic.

## 7. Data Collection, Intake, And Safer Records

- `secure-intake-form-builder` — designs safer collection forms with minimal data and better consent.
- `anonymous-tipline-setup` — sets up a safer anonymous reporting flow.
- `case-intake-router` — sorts incoming cases by urgency, risk, legal relevance, or communications priority.
- `data-minimization-review` — reviews an existing dataset to see what should stop being collected or kept.
- `retention-policy-lite` — defines how long different categories of data should exist.
- `consent-language-helper` — writes simpler, clearer consent language.
- `safe-spreadsheet-review` — reviews spreadsheets for sensitive columns, dangerous sharing, or silent leakage.
- `beneficiary-privacy-check` — protects lists of beneficiaries, victims, witnesses, or participants.
- `survey-risk-check` — assesses whether a survey is politically or operationally risky before launch.
- `duplicate-case-merger` — merges repeated case entries without losing context.

## 8. Hardware, Fieldwork, And Offline Operations

- `field-kit-checklist` — organizes equipment for field reporting, protest support, or evidence gathering.
- `power-resilience-planner` — plans battery, charging, cable, and power fallback needs.
- `mesh-radio-onboarding` — helps people join radio or mesh setups without too much jargon.
- `portable-server-setup` — prepares a lightweight local server for LAN sharing, local archives, or offline coordination.
- `offline-map-packager` — packages maps, key locations, and route notes for offline use.
- `safe-rendezvous-planner` — helps plan meetings with less fragile logistics.
- `checkpoint-logistics` — organizes travel, documents, contacts, and fallback routines in checkpoint-heavy environments.
- `equipment-sharing-ledger` — tracks borrowed devices and media in a less chaotic way.
- `device-sanitation-between-users` — cleans shared devices between shifts or volunteers.
- `rapid-relocation-kit` — prepares a digital and physical minimum for fast evacuation or relocation.

## 9. Media, Advocacy, And External Relations

- `press-outreach-sanitizer` — prepares safer outreach to journalists without oversharing.
- `spokesperson-brief-builder` — creates concise spokesperson briefs from messy internal context.
- `hostile-interview-prep` — prepares people for aggressive or adversarial interviews.
- `public-statement-risk-review` — reviews a public statement for avoidable risk before release.
- `campaign-message-tuner` — adapts a message for different audiences without losing accuracy.
- `solidarity-partner-mapper` — maps likely allies by geography, issue area, language, and capacity.
- `donor-comms-separator` — separates supporter communication from sensitive operational communication.
- `coalition-sync-kit` — helps multiple groups align public messaging without centralizing too much.
- `rapid-response-page` — creates an initial public response page for arrest, attack, leak, or crackdown.
- `international-brief-pack` — builds short briefings for international NGOs, media, or partner networks.

## 10. Care, Support, And Continuity

- `burnout-load-balancer` — redistributes work when a team is overloaded or emotionally exhausted.
- `detainee-support-coordinator` — coordinates support after detention, arrest, or disappearance.
- `family-notification-helper` — structures how families are informed during crisis situations.
- `trauma-aware-intake` — adjusts intake language and tempo to reduce additional harm.
- `bereavement-ops` — supports the operational side of death, disappearance, or grief-heavy incidents.
- `mutual-aid-router` — routes incoming and outgoing mutual-aid requests more cleanly.
- `safety-checkin-scheduler` — defines check-in routines for people in the field or at risk.
- `rest-rotation-planner` — avoids overloading the same few people during crisis response.

## 11. Education, Training, And Autonomy

- `freedom-tech-onboarding-by-role` — teaches different stacks to journalists, organizers, lawyers, volunteers, or family members.
- `security-drill-runner` — runs tabletop or practical drills so teams rehearse before a crisis.
- `nontechnical-admin-coach` — helps non-technical administrators operate systems with fewer mistakes.
- `trainer-kit-builder` — produces workshop structure, exercises, and support materials.
- `risk-explainer-by-scenario` — explains risk through concrete scenarios rather than abstract doctrine.
- `tool-migration-guide` — helps a group migrate from unsafe or brittle tools to safer ones.
- `low-literacy-tech-guide` — adapts training and instructions for users with low digital familiarity.
- `multilingual-rollout-pack` — prepares guides and onboarding materials in multiple languages for faster adoption.

## 12. Final Take

The most interesting pattern here is that many valuable skills for human-rights and freedom-tech users are not purely about protocols or apps.

They often sit at the boundary between:

- open-source software
- operational discipline
- documentation quality
- consent and harm reduction
- training and coordination under pressure

That boundary is probably where Freedom Skills can become unusually useful.
