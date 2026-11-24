require("paq")({
  "savq/paq-nvim", -- Let Paq manage itself

  -- LSP
  "neovim/nvim-lspconfig",
  "williamboman/mason.nvim",
  "williamboman/mason-lspconfig.nvim",
  "WhoIsSethDaniel/mason-tool-installer.nvim",
  "j-hui/fidget.nvim",
  "folke/lazydev.nvim",

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

  -- AI suggestions
  "milanglacier/minuet-ai.nvim",

  -- UI
  "folke/tokyonight.nvim",
  "nvim-tree/nvim-web-devicons",
  "nvim-lualine/lualine.nvim",
  "folke/noice.nvim",
  "MunifTanjim/nui.nvim",
  "norcalli/nvim-colorizer.lua",
  "MeanderingProgrammer/markdown.nvim", -- Markdown preview

  -- Navigation / editing
  "nvim-lua/plenary.nvim",
  { "nvim-telescope/telescope.nvim", branch = "0.1.x" },
  { "nvim-treesitter/nvim-treesitter", build = ":TSUpdate" },
  "aserowy/tmux.nvim",
  "mbbill/undotree",
  "stevearc/conform.nvim",

  -- Misc
  "akinsho/toggleterm.nvim",
  "f-person/git-blame.nvim",
  "vyfor/cord.nvim",
})
