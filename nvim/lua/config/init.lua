-- Plugin list first so everything below can require() plugins.
require("config.paq")

require("config.options")
require("config.diagnostics")
require("config.keymaps")

-- Per-plugin setup
require("config.plugins.ui")
require("config.plugins.telescope")
require("config.plugins.treesitter")
require("config.plugins.lsp")
require("config.plugins.completion")
require("config.plugins.ai")
require("config.plugins.formatting")
require("config.plugins.tools")
