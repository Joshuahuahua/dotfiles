# Project memory
- Investigated recurring pnpm-lock.yaml churn where `bufferutil`, `canvas`, `utf-8-validate` lines keep getting added/removed across unrelated PRs (package.json never changes). Root cause: these are NOT real deps - they're unmet optional peer deps (canvas is optional peer of jsdom; bufferutil/utf-8-validate are optional peers of ws, pulled in via jsdom used by jest-environment-jsdom). pnpm 10.x has known non-determinism bugs (pnpm/pnpm#13846, #12358, #12286) where the `transitivePeerDependencies` exclusion list for optional peers flips depending on dependency-resolution order, triggered by *any* unrelated dependency change elsewhere in the graph. Confirmed via `git log -- pnpm-lock.yaml`: commits like 3c3534c9 (swiper override bump) and 34c43e6b flip these lines in/out with no actual canvas/bufferutil/utf-8-validate package ever resolved in the lockfile. Safe/cosmetic - nothing is actually installed/removed from node_modules.

Fix: pnpm 11.3+ fixed this non-determinism class ("lockfile no longer flips between two equally-valid forms across consecutive runs").

Checked ADO: no ticket exists yet for "upgrade pnpm to v11+". Related: #12230 (User Story "pnpm", open umbrella), #12231 (Task "Upgrade pnpm to v9", closed), #21289 (Task "Review and remove temporary pnpm security overrides", open, New - likely should be done together since both touch the `pnpm.overrides` block in package.json).

Upgrade implications researched:
- Node: pnpm v11 requires Node 22+ (drops 18/19/20/21). Repo already pinned to Node 22.23.1 in package.json engines - no change needed.
- TypeScript: repo uses 5.3.3 across all Apps/* package.json - unaffected by pnpm v11.
- SPFx: repo uses @microsoft/sp-core-library / sp-build-web 1.21.1 (Apps/Sharepoint). Official SPFx 1.21.1 compatibility (learn.microsoft.com/en-us/sharepoint/dev/spfx/compatibility) targets Node v22, TypeScript v5.3, React 17.0.1 - already aligned. SPFx has no official package-manager gate (npm/yarn/pnpm all informally supported via @pnp/generator-spfx).
- Real migration cost is config-format, not runtime compat:
  1. `package.json#pnpm` field no longer read in v11 - root package.json's `pnpm.overrides` block (form-data, @azure/core-xml, websocket-driver, swiper, tar, maplibre-gl) must move into pnpm-workspace.yaml.
  2. `.npmrc` restricted to auth/registry only in v11 - current `.npmrc` has `shamefully-hoist` and `engine-strict`, both must move into pnpm-workspace.yaml as camelCase keys.
  3. Build-allow settings consolidate into single `allowBuilds` map (replaces onlyBuiltDependencies/neverBuiltDependencies/etc) - check workspace package.jsons for these before upgrading.
  4. `patchedDependencies` (currently `chokidar: patches/chokidar.patch`) stays but `ignorePatchFailures` is removed - patch failures now always throw.
  5. Security defaults tighten (minimumReleaseAge default 1 day, blockExoticSubdeps default true) - repo already explicitly sets `minimumReleaseAge: 10080` (7 days) in pnpm-workspace.yaml so unaffected.
  6. pnpm ships a `pnpm-v10-to-v11` codemod to automate most of this.

Action: added a high-priority todo (#8) to upgrade pnpm to v11+ in hub/workspace2, since no ADO ticket exists yet for this. _(saved 2026-10-01)_
