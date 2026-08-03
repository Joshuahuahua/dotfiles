# Project memory
- For /home/josh/development/personal/devopsPrinter: when changes affect package behavior, commands, configuration, or printer flows, update README.md in the same change. _(saved 2026-07-21)_

## Project memory
- For /home/josh/development/personal/devopsPrinter: a preview-mode smoke test plan lives at TEST_PLAN.md in the project root. When the user asks to test the printer system, follow TEST_PLAN.md — it covers the CLI note receipt, CLI devops ticket (use work item id 20020), the notification listener (NOTIF_PREVIEW=true + notify-send), and the webserver (/health and POST /print-ticket with preview:true), plus clean-slate/teardown steps. All tests are preview-only (never print to the physical printer). _(saved 2026-07-24)_
