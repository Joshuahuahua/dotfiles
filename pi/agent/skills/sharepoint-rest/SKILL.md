---
name: sharepoint-rest
description: Live-tests SharePoint Online REST/CAML endpoints (e.g. Events list queries) against the huddler-integration site using device-code OAuth, bypassing the browser workbench. Use when asked to test a SharePoint REST call, run/compare CAML queries against the real Events list, check live list data, or verify renderlistdataasstream behaviour outside the SPFx webpart.
---

# SharePoint Online REST testing (device-code auth)

Call SharePoint Online's REST API directly (the same `_api/web/lists/...`
and `renderlistdataasstream` endpoints the SPFx webparts use) via `curl`-free
Python, instead of going through the browser workbench. This is the
mechanism used previously to compare CAML query variants for the Events
webpart against real list data.

Use this skill whenever asked to:
- Test/compare a SharePoint REST or CAML query against live data.
- Check what's actually in a SharePoint list (e.g. "what recurring events
  exist in the Events list right now").
- Verify `renderlistdataasstream` behaviour for a webpart's query builder
  outside the browser workbench.
- Debug a SPFx data-fetching bug by reproducing the exact REST call it makes.

## Why device-code auth (not `az` CLI tokens)

Azure CLI's own app registration / default Graph token scopes are **not**
authorized to call SPO REST directly in this tenant (`az account
get-access-token --resource https://huddler365.sharepoint.com` fails with
"App is not allowed to call SPO with user_impersonation scope"; a Graph
token has no `Sites.*` scope).

The working approach is a device-code OAuth flow using the well-known
**"SharePoint Online Management Shell"** first-party app id
(`9bc3ab49-b65d-410a-85ad-de819febfddc`) — it's already consented in this
tenant. The PnP Management Shell app id is *not* registered here and fails
with `AADSTS700016`.

## Configuration (baked into the script, override via env vars if needed)

- Tenant id: `fa17b8ee-13de-4039-84de-200564f4fcfe` (`SPO_TENANT_ID`)
- Tenant host: `huddler365.sharepoint.com` (`SPO_TENANT_HOST`)
- Default site: `huddler-integration` (`SPO_DEFAULT_SITE`) — this is the
  site actually used for live testing, not `huddler-dev` from
  `config/serve.json`.
- Client id: the Management Shell app id above (`SPO_CLIENT_ID`)

Sign in as **joshua.hollander@huddler365.onmicrosoft.com** (the tenant
account) when prompted — the `diversus.com.au` guest account hits
consent/authorization issues.

## Helper script

Script: `scripts/spo.py` (resolve relative to this SKILL.md's directory,
i.e. `/home/josh/.pi/agent/skills/sharepoint-rest/scripts/spo.py`). Run with
`python3`, stdlib only (no extra install needed). `xdg-open` and `xclip` are
used opportunistically for the login step and are not required otherwise.

### First-time / re-login

```bash
python3 spo.py login
```

This starts the device-code flow, opens
`https://login.microsoftonline.com/device` in the browser and copies the
user code to the clipboard automatically so Josh just has to paste it and
approve. Then polls until approved and caches the access + refresh token.

Tokens are cached **per Pi session**, not shared or persisted across
sessions: the cache file lives at `/tmp/spo-token-cache-<PI_SESSION_ID>.json`
(mode 0600), keyed off the `PI_SESSION_ID` env var. A different session has
a different session id, so it has no cache file yet and cannot read this
session's token - it would need to run `login` itself. Within one session,
access tokens last about an hour and the script auto-refreshes using the
cached refresh token on every call, so `login` only needs to be run once per
session (re-run it again if the refresh token itself goes stale).

### GET a REST path

```bash
python3 spo.py get "web/lists/getbytitle('Events')?\$select=Title,ItemCount"
python3 spo.py get "web/lists/getbytitle('Events')?\$select=Title,ItemCount" --site some-other-site
```

### POST a REST path with a JSON body

```bash
python3 spo.py post "web/lists/getbytitle('Events')/items" --body '{"...": "..."}'
python3 spo.py post "some/path" --body-file /tmp/body.json
```

### CAML queries via renderlistdataasstream (what the SPFx webparts call)

This is the main use case — testing a CAML `ViewXml` exactly as the
`eventsApi*.ts` query builders would send it:

```bash
python3 spo.py renderlist Events --viewxml '<View><Query>...</Query></View>'
python3 spo.py renderlist Events --viewxml-file /tmp/view.xml
```

Internally this POSTs to
`web/lists/getbytitle('<list>')/renderlistdataasstream` with
`{"parameters":{"ViewXml": "..."}}`, `Accept`/`Content-Type:
application/json;odata=nometadata` — identical to the production call path,
so results are directly comparable to what the webpart would render.

## Notes

- If a call fails with 401, the cached token has likely gone fully stale —
  run `login` again.
- The token cache file is session-scoped and ephemeral (lives in `/tmp`,
  never touches the repo): never print its contents, never commit it, never
  paste a token into chat.
- When debugging a specific webpart's query builder (e.g.
  `Apps/Sharepoint/src/webparts/Events/shared/eventsApi4.ts`), the fastest
  loop is: generate the `ViewXml` the builder would produce, feed it to
  `renderlist`, and compare against what the browser workbench shows.
