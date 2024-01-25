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

  -- LSP Configuration & Plugins
  {
    'neovim/nvim-lspconfig',
    dependencies = {
      { 'williamboman/mason.nvim', config = true }, -- Automatically install LSPs to stdpath for neovim
      'williamboman/mason-lspconfig.nvim',
      { 'j-hui/fidget.nvim',       opts = {} },   -- Useful status updates for LSP. NOTE: `opts = {}` is the same as calling `require('fidget').setup({})`
      'folke/neodev.nvim',                        -- Additional lua configuration, makes nvim stuff amazing!
    }
  },

  -- Completions
  "hrsh7th/nvim-cmp",
  {
    require("nvim-cmp").setup({
snippet = {
    expand = function(args)
      luasnip.lsp_expand(args.body)
    end,
  },
  completion = {
    completeopt = 'menu,menuone,noinsert',
  }
})
},
  "hrsh7th/cmp-nvim-lsp",
  "hrsh7th/cmp-nvim-lua",
  "hrsh7th/cmp-buffer",
  "hrsh7th/cmp-path",
  "hrsh7th/cmp-cmdline",
  "L3MON4D3/LuaSnip",


-- require("lua.plugins.cmp")
})
