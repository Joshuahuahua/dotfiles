local servers = {
  bicep = { cmd = { "bicep-lsp" } },
  pyright = {},
  rust_analyzer = {},
  ts_ls = {},
  tailwindcss = {},
  eslint = {
    workingDirectory = { mode = "auto" },
  },
  lua_ls = {
    Lua = {
      workspace = { checkThirdParty = false },
      telemetry = { enable = false },
    },
  },
}

require("mason").setup({
  PATH = "prepend", -- "skip" seems to cause the spawning error
})
require("mason-lspconfig").setup({
  ensure_installed = vim.tbl_keys(servers),
  automatic_enable = false,
})

-- Formatters, linters and debug adapters (LSP servers are handled above)
require("mason-tool-installer").setup({
  ensure_installed = { "stylua", "prettier", "black", "ruff", "yamllint", "debugpy" },
})

require("fidget").setup({}) -- LSP progress notifications

local capabilities = require("cmp_nvim_lsp").default_capabilities(vim.lsp.protocol.make_client_capabilities())

for name, settings in pairs(servers) do
  vim.lsp.config(name, {
    capabilities = capabilities,
    settings = settings,
    filetypes = settings.filetypes,
    cmd = settings.cmd,
  })
  vim.lsp.enable(name)
end

vim.cmd("packadd lazydev.nvim")
require("lazydev").setup({
  library = {
    { path = "${3rd}/luv/library", words = { "vim%.uv" } },
  },
})
