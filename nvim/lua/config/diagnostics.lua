vim.diagnostic.config({
  underline = true,
  virtual_text = false,
  signs = true,
  update_in_insert = false,
  severity_sort = true,
  float = {
    style = "minimal",
    source = "always",
  },
})

-- Colour the line number instead of showing a sign-column icon.
local function set_hls()
  vim.api.nvim_set_hl(0, "LineNrError", { fg = "#ff5f5f", bold = true })
  vim.api.nvim_set_hl(0, "LineNrWarn", { fg = "#ffaa00", bold = true })
end

set_hls()

-- Reapply after colorscheme changes
vim.api.nvim_create_autocmd("ColorScheme", { callback = set_hls })

local signs = {
  Error = "LineNrError",
  Warn = "LineNrWarn",
  Info = "LineNrInfo",
  Hint = "LineNrHint",
}

for type, hl in pairs(signs) do
  vim.fn.sign_define("DiagnosticSign" .. type, { text = "", texthl = "", numhl = hl })
end
