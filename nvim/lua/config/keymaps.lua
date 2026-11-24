local set = vim.keymap.set
local telescope = require("telescope.builtin")

-- Window navigation (tmux-aware)
set({ "n", "t" }, "<C-h>", function() require("tmux").move_left() end)
set({ "n", "t" }, "<C-l>", function() require("tmux").move_right() end)
set({ "n", "t" }, "<C-k>", function() require("tmux").move_top() end)
set({ "n", "t" }, "<C-j>", function() require("tmux").move_bottom() end)

-- Clipboard
set({ "n", "v" }, "<leader>y", '"+y') -- system clipboard
set("n", "<leader>Y", '"+Y')
set({ "n", "v" }, "<leader>d", '"_d') -- void register
set("n", "ycc", "yygccp", { remap = true })

-- Handy
set("n", "<ESC>", "<cmd>noh<CR><ESC>") -- Esc unhighlights
set("v", "J", ":m '>+1<CR>gv=gv")
set("v", "K", ":m '<-2<CR>gv=gv")
set("n", "J", "mzJ`z")
set("n", "H", "^")
set("n", "L", "$")

-- Keep the cursor centred
set("n", "<C-u>", "<C-u>zz")
set("n", "<C-d>", "<C-d>zz")
set("n", "n", "nzzzv")
set("n", "N", "Nzzzv")

-- Telescope / files
set("n", "<C-f>", function() telescope.live_grep({ prompt_prefix = "🔍" }) end)
set("n", "<leader>b", telescope.buffers)
set("n", "<leader>w", telescope.diagnostics)
set("n", "<leader>e", "<cmd>Ex<CR>")
set("n", "<leader>u", "<cmd>UndotreeToggle<CR><cmd>UndotreeFocus<CR>")

-- LSP
set("n", "gd", "<cmd>Telescope lsp_definitions<CR>")
set("n", "gr", "<cmd>Telescope lsp_references<CR>")
set("n", "gi", "<cmd>Telescope lsp_implementations<CR>")
set("n", "<S-k>", vim.lsp.buf.hover)
set("n", "gn", vim.lsp.buf.rename)
set("n", "<leader>ca", vim.lsp.buf.code_action)
set("n", "ge", vim.diagnostic.open_float)
set("n", "gj", function() vim.diagnostic.jump({ count = 1 }) end)
set("n", "gk", function() vim.diagnostic.jump({ count = -1 }) end)

-- Formatting
set("n", "<leader>f", function()
  require("conform").format({ async = true, lsp_fallback = false })
end)
set("n", "<leader>ff", function() vim.lsp.buf.format({ async = true }) end)

-- Quickfix
set("n", "<leader>qa", function()
  vim.fn.setqflist({}, "a", {
    title = "Quickfix",
    items = {
      {
        filename = vim.fn.expand("%:p"),
        lnum = vim.fn.line("."),
        col = vim.fn.col("."),
        text = vim.fn.getline("."),
      },
    },
  })
end, { desc = "Add current file/line to quickfix list" })

-- Next/prev quickfix item. Only takes effect while the quickfix window is
-- open somewhere, otherwise falls through to the fallback (if any).
local function qf_nav(cmd, fallback)
  return function()
    if vim.fn.getqflist({ winid = 0 }).winid ~= 0 then
      vim.cmd(cmd)
      vim.cmd("normal! zz")
    elseif fallback then
      fallback()
    end
  end
end

set("n", "<C-n>", qf_nav("cnext"), { desc = "Next quickfix item" })
set("n", "<C-p>", qf_nav("cprev", function()
  telescope.find_files({ prompt_prefix = "🔍" })
end), { desc = "Previous quickfix item / find files" })

-- Git
set("n", "<leader>gs", "<cmd>Telescope git_status<CR>")
set("n", "<leader>gb", "<cmd>GitBlameToggle<CR>") -- toggle inline blame
set("n", "<leader>gY", "<cmd>GitBlameCopyCommitURL<CR>") -- yank commit URL
set("n", "<leader>go", "<cmd>GitBlameOpenCommitURL<CR>") -- open commit in browser
