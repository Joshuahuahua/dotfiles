----------------------------
-- Lil Config +Notes
----------------------------
-- This is just a lil sample config, I'd recommend seperating the headings into different files
-- External Deps needed: fd-find, ripgrep, git

----------------------------
-- Var Abstractions (lol) --
----------------------------

local o = vim.opt
local g = vim.g
local set = vim.keymap.set

--------------
-- Settings --
--------------

-- Leader Key
g.mapleader = " "
g.maplocalleader = " "

-- Line Numbers
o.number = true
o.numberwidth = 4
o.relativenumber = true

-- Indentation
o.tabstop = 2
o.softtabstop = 2
o.shiftwidth = 2
o.expandtab = true
o.smartindent = true

-- Window behaviour
o.splitright = true
o.splitbelow = true

-- Others
o.wrap = true
o.mouse = "a"          -- Fixes mouse highlighting etc
o.scrolloff = 8        -- Lines of padding when scrolling
o.termguicolors = true -- True color support

--------------
-- Keybinds --
--------------

-- Misc
set("n", "<ESC>", ":noh<CR>")
set("n", "gl", "<cmd>lua vim.diagnostic.open_float()<CR>")


-- nvim navigate splits
set("n", "<C-h>", "<C-w>h")
set("n", "<C-j>", "<C-w>j")
set("n", "<C-k>", "<C-w>k")
set("n", "<C-l>", "<C-w>l")

-- Jump to start/end of line
set("n", "H", "^")
set("n", "L", "$")

-- System Clipboard
set("n", "<leader>y", '"+y')
set("v", "<leader>y", '"+y')
set("n", "<leader>Y", '"+Y')

-- Comment
set("n", "<C-_>", "gcc") -- Ctrl+/    NOT WORKING

-- File Search
set("n", "<C-p>", function()
  require("telescope.builtin").find_files()
end)

-- Monorepo
set("n", "<leader>m", function()
  require("telescope").extensions.monorepo.monorepo()
end)
set("n", "<leader>n", function()
  require("monorepo").toggle_project()
end)

-- Live Grep
set("n", "<C-f>", function()
  require("telescope.builtin").live_grep()
end)

-- Formatting
set("n", "<leader>f", function()
  vim.lsp.buf.format { async = true }
end)
