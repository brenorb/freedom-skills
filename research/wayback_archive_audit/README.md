# Wayback Archive Audit

This folder contains the source data and generator for the canonical workbook:

- [wayback-archive-feature-audit.xlsx](/Users/breno/Documents/code/PROJECTS/HRF_GRANT/freedom-skills/research/wayback-archive-feature-audit.xlsx)

Regenerate it with the bundled runtime:

```bash
OAI_NODE_MODULES=/Users/breno/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules \
/Users/breno/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node \
research/wayback_archive_audit/build_wayback_archive_audit.mjs
```

Update [audit_data.json](/Users/breno/Documents/code/PROJECTS/HRF_GRANT/freedom-skills/research/wayback_archive_audit/audit_data.json) first when story status or evidence changes.
