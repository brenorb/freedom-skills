---
name: napplet-icon
description: Use when designing, generating, or refining a napplet app icon, favicon, or app identity mark. Turns the app's purpose and visual references into a design direction, generates or edits actual icon artwork, checks legibility at small sizes, and delivers an asset ready for optional NIP-5D integration. Also supports design-only briefs and prompts when requested.
compatibility: Artwork-only work needs no CLI; manifest integration follows `@napplet/cli` 0.13.0.
license: MIT
metadata:
  version: "0.2.0"
  repository: "https://github.com/napplet/web"
  homepage: "https://napplet.run"
  upstream_sha: "6c4dafd20142cade5a51ae049beecfef7c8f7c2e"
  upstream_cli: "0.13.0"
  upstream_sdk: "0.30.0"
  upstream_source: "https://github.com/napplet/web/tree/6c4dafd20142cade5a51ae049beecfef7c8f7c2e/skills/napplet-icon"
---

# Design and generate a napplet icon

Own the icon from concept through finished artwork. Use this independently for an existing app or alongside `napplet-design` for a new one. Use `napplet-ui` for interface layout and controls; an app icon does not require redesigning the app.

## 1. Establish the direction

Read the app's purpose, existing design notes, palette, and icon assets. Inspect supplied visual references before describing or editing them. Reuse known context; ask only when a missing detail would materially change the result. If the user gives no style preference, choose a direction that fits the app and briefly state it before generating. Do not require approval of a design board unless the user asks for that process.

Write a compact brief:

- **Identity:** app name, one job, and the feeling the icon should convey.
- **Concept:** one recognizable subject or metaphor, with a distinctive silhouette or negative-space detail tied to that job.
- **Treatment:** shape language, material or illustration style, palette, and solid or transparent background.
- **Constraints:** reference features to preserve, requested text, target sizes, and anything the user excludes.

Prefer a clear focal shape over a miniature interface or a collection of feature symbols. Avoid small lettering and fine detail that disappear at launcher size; honor an explicit monogram or text request. Match an existing brand when provided. Offer distinct concepts when the user wants exploration; otherwise select one and proceed.

A square 1024 px master is a useful default when the tool supports it. Plan enough clear space for the mark to survive rounded and circular display masks. These are design recommendations, not NIP-5D requirements.

## 2. Generate the artwork

Use the available image-generation tool and its instructions. If an `imagegen` skill is installed, follow its tool-specific workflow. Prefer the host's built-in tool when available; use a separate API or CLI only when requested. For an existing icon, inspect it first and use the image-editing workflow with that reference, stating precisely what should change and what should remain.

Translate the brief into a focused prompt. Include only relevant fields:

```text
Deliverable: one standalone app icon for [name and job]
Concept: [subject, silhouette, distinctive feature]
Style: [shape language, material, rendering treatment]
Composition: [focal shape, scale, negative space, crop clearance]
Palette and background: [colors; solid or true transparency]
Small-size behavior: [features that must remain recognizable]
Preserve / change: [reference constraints, for edits]
Exclude: [specific unwanted details]
```

Ask for the icon itself, without a phone mockup, surrounding interface, or presentation board. Generate separate files for requested alternatives. When transparency is requested, enable the tool's transparent-background option and preserve alpha; a drawn checkerboard is not transparency. Record actual output paths returned by the tool instead of assuming where files were saved.

For a design-only or prompt-only request, stop at that deliverable. If image generation is unavailable, provide the brief and ready-to-use prompt, state that no image was generated, and identify the missing capability. Do not call a placeholder a finished icon.

## 3. Inspect and refine

View the generated result. Check a preview at 16, 32, and 64 px as well as the master size, using available image-viewing tools or a scaled preview. Check transparent artwork against both light and dark backgrounds and under rounded/circular masks when relevant. A large attractive render is not enough evidence of small-size legibility.

Look for a recognizable silhouette, clear separation between foreground and background, preserved negative space, even visual weight, and unclipped edges. Check requested text for accuracy and inspect transparent edges for halos or an opaque backdrop. Verify actual dimensions, format, and alpha with available file inspection tools; do not infer them from the prompt or extension.

If a check fails, make a targeted edit such as widening a gap, simplifying interior detail, increasing contrast, or removing a halo. Preserve the chosen identity while refining. Reinspect the changed result. Report any unavailable visual or file checks rather than claiming they passed.

## 4. Deliver and integrate

Save the selected asset in the project's existing asset convention, outside the build output directory; for a standalone request, save it in the requested output location. Keep a master when exporting a smaller version. Default to PNG for a generated raster icon unless the user or project calls for another supported format. Preserve existing assets unless replacing them is part of the request. Return the actual file, its path, dimensions, format, and a short design rationale.

When adding the icon to a napplet project, inspect the installed build and publishing tooling before changing configuration. The [vite-plugin documentation](https://github.com/napplet/napplet/blob/main/packages/vite-plugin/README.md) describes byte input through `icon.data` with `mimeType`; verify that the installed version supports it. Use that path to embed the selected bytes and derive metadata instead of inventing config options or manifest tags. Finish with the project's build and `napplet-test` checks.

Protocol guidance here is non-normative. Before integration, read the actual `5D.md` at the current head of [NIP-5D PR #2303](https://github.com/nostr-protocol/nips/pull/2303), particularly **Manifest**, **Icon**, and **HTML Metadata for Publishing**. Follow the living text if it changes:

- NIP-5D requires a single self-contained `/index.html`. Keep the icon embedded as a supported data URL in the built HTML when using the HTML publishing mapping; do not introduce an external runtime icon dependency. Check the built artifact even if the config says `artifactMode: 'single-file'`.
- The optional manifest icon currently supports PNG, JPEG, and WebP. An SVG design source needs a supported raster export for that field. Icons and specific pixel dimensions are not mandatory protocol features.
- Let publishing tooling hash the final decoded image bytes and upload those same bytes as the icon blob. The icon hash and the artifact's `x` hash describe different bytes. Finalize embedded icon metadata before the artifact is hashed and signed; do not patch a signed artifact afterward.
- If optional Zapstore metadata is also configured, keep its URL-based image fields separate from the NIP-5D manifest icon. Follow the existing publishing workflow and the user's publishing scope.

For delivery, show the selected icon and identify the checks performed. Distinguish a finished asset from verified app integration and publication; report only what actually ran.
