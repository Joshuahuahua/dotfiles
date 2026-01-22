-- Highlight relative line numbers when diagnostics exist on a line
vim.opt.number = true
vim.opt.relativenumber = true

-- Highlight groups
local function set_hls()
  vim.api.nvim_set_hl(0, "LineNrError", { fg = "#ff5f5f", bold = true })
  vim.api.nvim_set_hl(0, "LineNrWarn",  { fg = "#ffaa00", bold = true })
  -- vim.api.nvim_set_hl(0, "LineNrInfo",  { fg = "#5fafff" })
  -- vim.api.nvim_set_hl(0, "LineNrHint",  { fg = "#5fffaf" })
end

set_hls()

-- Reapply after colorscheme changes
vim.api.nvim_create_autocmd("ColorScheme", {
  callback = set_hls,
})

-- Diagnostic signs that recolor the line number
local signs = {
  Error = "LineNrError",
  Warn  = "LineNrWarn",
  Info  = "LineNrInfo",
  Hint  = "LineNrHint",
}

for type, hl in pairs(signs) do
  vim.fn.sign_define(
    "DiagnosticSign" .. type,
    { text = "", texthl = "", numhl = hl }
  )
end

-- Make sure diagnostics are enabled
vim.diagnostic.config({
  signs = true,
  severity_sort = true,
})
