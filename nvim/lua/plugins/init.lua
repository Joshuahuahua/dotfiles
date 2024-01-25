---------
-- LSP --
---------

local lspInit = function()
  local lsp_zero = require("lsp-zero")

  lsp_zero.on_attach(function(client, bufnr)
    -- see :help lsp-zero-keybindings
    -- to learn the available actions
    lsp_zero.default_keymaps({ buffer = bufnr })
  end)

  require("mason").setup({})
  require("mason-lspconfig").setup({
    ensure_installed = {},
    handlers = {
      lsp_zero.default_setup,
    },
  })

  -- require('plugins.cmp')
end

-------------
-- Plugins --
-------------

-- Install lazy.nvim if it doesn't exist (requires git)
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", -- latest stable release
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

-- Call lazy to load plugins
require("lazy").setup({
  -- Example plugin, can be a string or object but object if you want more control. See docs.
  {
    "folke/tokyonight.nvim", -- Plugin name/url, automatically prefixed with `github.com/`
    config = function()      -- This is called after the plugin is loaded
      vim.cmd([[colorscheme tokyonight]])
    end,
  },

  -- Telescope for searching n stuff
  {
    "nvim-telescope/telescope.nvim",
    branch = "0.1.x",
    dependencies = { "nvim-lua/plenary.nvim" },
    config = function()
      require('telescope').setup {
        defaults = {
          initial_mode = "normal"
        }
      }
    end,
  },

  -- File Explorer
  --   {
  --     'nvim-tree/nvim-tree.lua',
  --     requires = {
  --       { 'kyazdani42/nvim-web-devicons' },
  --     },
  --     config = function() require("plugins.config.nvimtree") end,
  --   },


  -- Cool Syntax Highlighting
  {
    "nvim-treesitter/nvim-treesitter",
    -- build = function()
    --	require("nvim-treesitter.install").update({ with_sync = true })
    -- end,
    config = function()
      require("nvim-treesitter.configs").setup({
        ensure_installed = {},
        sync_install = false,
        auto_install = true,
        highlight = {
          enable = true,
          additional_vim_regex_highlighting = false,
        },
        context_commentstring = {
          enable = true,
        },
      })
    end,
  },

  -- LSP Stuffs
  "neovim/nvim-lspconfig",
  "williamboman/mason.nvim",
  "williamboman/mason-lspconfig.nvim",
  {
    "VonHeikemen/lsp-zero.nvim",
    branch = "v3.x",
    config = lspInit
  },

  -- Completions
  "hrsh7th/nvim-cmp",
  "hrsh7th/cmp-nvim-lsp",
  "hrsh7th/cmp-nvim-lua",
  "hrsh7th/cmp-buffer",
  "hrsh7th/cmp-path",
  "hrsh7th/cmp-cmdline",
  "L3MON4D3/LuaSnip",


  -- Comments
  {
    'numToStr/Comment.nvim',
    opts = {},
    lazy = false,
    config = function()
      require("plugins.comment")
    end
  }
})
