require("conform").setup({
  log_level = vim.log.levels.DEBUG,

  formatters_by_ft = {
    lua = { "stylua" },
    javascript = { "prettier" },
    javascriptreact = { "prettier" },
    typescript = { "prettier" },
    typescriptreact = { "prettier" },
    html = { "prettier" },
    json = { "prettier" },
    scss = { "prettier" },
    css = { "prettier" },
    yaml = { "prettier" },
    python = { "isort", "black" },
    bicep = { "bicep" },
  },
})
