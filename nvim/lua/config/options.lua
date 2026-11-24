local o = vim.opt
local g = vim.g

-- Leader key
g.mapleader = " "
g.maplocalleader = " "

-- Line numbers
o.number = true
o.numberwidth = 4
o.relativenumber = true

-- Appearance
o.termguicolors = true
o.laststatus = 3
o.conceallevel = 0
o.concealcursor = ""

-- Netrw
g.netrw_keepdir = 1
g.netrw_banner = 0
g.netrw_localcopydircmd = "cp -r"

-- Indentation
o.tabstop = 2
o.softtabstop = 2
o.shiftwidth = 2
o.expandtab = true
o.smartindent = true

-- Keep Python buffers at two spaces even if a filetype plugin changes the
-- global indentation defaults.
vim.api.nvim_create_autocmd("FileType", {
  pattern = "python",
  callback = function()
    vim.opt_local.tabstop = 2
    vim.opt_local.softtabstop = 2
    vim.opt_local.shiftwidth = 2
    vim.opt_local.expandtab = true
  end,
})

-- Windows and scrolling
o.splitright = true
o.splitbelow = true
o.wrap = false
o.scrolloff = 8
