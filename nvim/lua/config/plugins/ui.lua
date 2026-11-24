vim.cmd.colorscheme("tokyonight-storm")

require("lualine").setup({})

require("noice").setup({
  lsp = {
    -- fidget.nvim already renders LSP progress; noice doing it too causes
    -- redraw contention (freezes) while a server is loading/indexing.
    progress = { enabled = false },
  },
})

require("colorizer").setup({ "*" }, {
  RGB = true, -- #RGB
  RRGGBB = true, -- #RRGGBB
  rgb_fn = true, -- rgb(), rgba()
  hsl_fn = true, -- hsl(), hsla()
  names = false, -- Blue, red, etc.
  css = true,
  css_fn = true,
  tailwind = true,
  mode = "background", -- or "foreground"
})

-- Render git blame after search count virtual text (e.g. noice's [x/y] on n/N)
vim.g.gitblame_set_extmark_options = { priority = 9000 }

require("cord").setup({
  text = {
    workspace = "",
    viewing = "Viewing a file",
    editing = "Editing a file",
    file_browser = "Browsing files",
    plugin_manager = "Managing plugins",
    lsp = "Configuring LSP",
    docs = "Reading docs",
    vcs = "Working with Git",
    notes = "Taking notes",
    debug = "Debugging",
    test = "Running tests",
    diagnostics = "Fixing problems",
    games = "Playing a game",
    terminal = "Using the terminal",
  },
})
