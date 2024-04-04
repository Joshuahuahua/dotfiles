local o = vim.opt
local g = vim.g

-- Leader Key
vim.g.mapleader = " "
vim.g.maplocalleader = " "

-- Line Numbers
o.number = true
o.numberwidth = 4
o.relativenumber = true

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

-- Window behaviour
o.splitright = true
o.splitbelow = true

-- Others
o.wrap = false
o.scrolloff = 8
o.termguicolors = true
o.conceallevel = 0
o.concealcursor = ""

-- Theme
vim.cmd.colorscheme("tokyonight-storm")

-- Comments
-- See: `:h comment-nvim`
require("ts_context_commentstring").setup({
  enable_autocmd = false,
})
require("Comment").setup({
  pre_hook = require("ts_context_commentstring.integrations.comment_nvim").create_pre_hook(),
})

-- Telescope
require("telescope").setup({
  defaults = {
    initial_mode = "normal",
    selection_strategy = "reset",
    sorting_strategy = "ascending",
    layout_strategy = "horizontal",
    path_display = { "truncate" },
    layout_config = {
      horizontal = {
        prompt_position = "top",
        preview_width = 0.5,
      },
      width = 0.9,
      height = 0.9,
      preview_cutoff = 80,
    },
  },
  pickers = {
    find_files = {
      find_command = { "fd", "--type", "f", "-H", "-E", ".git" },
    },
  },
})

-- Treesitter
require("nvim-treesitter.configs").setup({
  ensure_installed = { "lua", "typescript", "javascript" },
  highlight = {
    enable = true,
    additional_vim_regex_highlighting = false,
  },
})

require('gitblame').setup {
  enabled = false,
}

-- LSP
local servers = {
  -- pyright = {},
  rust_analyzer = {},
  tsserver = {},
  lua_ls = {
    Lua = {
      workspace = { checkThirdParty = false },
      telemetry = { enable = false },
    },
  },
}

require("mason").setup({
    PATH = "prepend", -- "skip" seems to cause the spawning error
})
require("mason-lspconfig").setup({
  ensure_installed = vim.tbl_keys(servers),
})
require("neodev").setup()
require("fidget").setup({}) -- Notifications

local capabilities = vim.lsp.protocol.make_client_capabilities()
capabilities = require("cmp_nvim_lsp").default_capabilities(capabilities)

require("mason-lspconfig").setup_handlers({
  function(server_name)
    require("lspconfig")[server_name].setup({
      capabilities = capabilities,
      on_attach = nil,
      settings = servers[server_name],
      filetypes = (servers[server_name] or {}).filetypes,
    })
  end,
})

-- Completion
local cmp = require("cmp")
local luasnip = require("luasnip")
require("luasnip.loaders.from_vscode").lazy_load()
luasnip.config.setup()

-- Copilot (Disable suggestions, then add to cmp)
require("copilot").setup({
  suggestion = { enabled = false },
  panel = { enabled = false },
})
require("copilot_cmp").setup()

cmp.setup({
  snippet = {
    expand = function(args)
      luasnip.lsp_expand(args.body)
    end,
  },
  completion = {
    completeopt = "menu,menuone,noinsert",
  },
  mapping = cmp.mapping.preset.insert({
    ["<C-n>"] = cmp.mapping.select_next_item(),
    ["<C-p>"] = cmp.mapping.select_prev_item(),
    ["<C-b>"] = cmp.mapping.scroll_docs(-4),
    ["<C-f>"] = cmp.mapping.scroll_docs(4),
    ["<C-Space>"] = cmp.mapping.complete({}),
    ["<CR>"] = cmp.mapping.confirm({
      behavior = cmp.ConfirmBehavior.Replace,
      select = true,
    }),
    ["<Tab>"] = cmp.mapping(function(fallback)
      if cmp.visible() then
        cmp.select_next_item()
      elseif luasnip.expand_or_locally_jumpable() then
        luasnip.expand_or_jump()
      else
        fallback()
      end
    end, { "i", "s" }),
    ["<S-Tab>"] = cmp.mapping(function(fallback)
      if cmp.visible() then
        cmp.select_prev_item()
      elseif luasnip.locally_jumpable(-1) then
        luasnip.jump(-1)
      else
        fallback()
      end
    end, { "i", "s" }),
  }),
  sources = {
    { name = "copilot", group_index = 2 },
    { name = "nvim_lua" },
    { name = "nvim_lsp" },
    { name = "luasnip" },
    { name = "path" },
    { name = "buffer",  keyword_length = 5 },
  },
  experimental = {
    ghost_text = {},
  },
})

-- cmp on command
cmp.setup.cmdline(":", {
  mapping = cmp.mapping.preset.cmdline(),
  sources = cmp.config.sources({
    { name = "path" },
    { name = "cmdline" },
  }),
})

-- Formatting
require("conform").setup({
  formatters_by_ft = {
    lua = { "stylua" },
    javascript = { { "prettierd", "prettier" } },
    javascriptreact = { { "prettierd", "prettier" } },
    typescript = { { "prettierd", "prettier" } },
    typescriptreact = { { "prettierd", "prettier" } },
    python = { "isort", "black" },
  },
  -- format_on_save = {
  -- 	-- These options will be passed to conform.format()
  -- 	timeout_ms = 500,
  -- 	lsp_fallback = true,
  -- },
})
