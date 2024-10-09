require("paq")({
  "savq/paq-nvim", -- Let Paq manage itself

  -- LSP
  "neovim/nvim-lspconfig",
  "williamboman/mason.nvim",
  "williamboman/mason-lspconfig.nvim",
  "j-hui/fidget.nvim",
  "folke/neodev.nvim",

  -- Completion
  "hrsh7th/nvim-cmp",
  "L3MON4D3/LuaSnip",
  "saadparwaiz1/cmp_luasnip",
  "hrsh7th/cmp-nvim-lsp",
  "hrsh7th/cmp-path",
  "hrsh7th/cmp-buffer",
  "hrsh7th/cmp-nvim-lua",
  "hrsh7th/cmp-cmdline",
  "rafamadriz/friendly-snippets",

  -- "folke/lazydev.nvim",           -- Add the lazydev.nvim plugin

  "supermaven-inc/supermaven-nvim",
  "nvim-tree/nvim-web-devicons",
  "nvim-lualine/lualine.nvim",
  "folke/noice.nvim",
  "MunifTanjim/nui.nvim",

  'MeanderingProgrammer/markdown.nvim', -- Markdown Preview

  'akinsho/toggleterm.nvim', -- Terminal

  -- "onsails/lspkind.nvim",

  -- Everything else
  "folke/tokyonight.nvim",
  "mbbill/undotree",
  "nvim-lua/plenary.nvim",
  "nvim-telescope/telescope.nvim",
  { "nvim-treesitter/nvim-treesitter", build = ":TSUpdate" },
  "numToStr/Comment.nvim",
  "JoosepAlviste/nvim-ts-context-commentstring",
  "f-person/git-blame.nvim",
  "stevearc/conform.nvim",
  { "schrieveslaach/sonarlint.nvim",   url = "https://gitlab.com/schrieveslaach/sonarlint.nvim" },
})

require("settings")
require("keybinds")
