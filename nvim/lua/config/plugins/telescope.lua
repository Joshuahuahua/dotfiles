local actions_state = require("telescope.actions.state")

-- Adds the currently highlighted result (not the whole result set) to the
-- quickfix list, keeping the picker open so you can keep adding more.
local function send_current_to_qflist()
  local entry = actions_state.get_selected_entry()
  if not entry then
    return
  end

  vim.fn.setqflist({}, "a", {
    title = "Telescope",
    items = {
      {
        filename = entry.filename or entry.path or entry.value,
        lnum = entry.lnum or 1,
        col = (entry.col or 0) + 1,
        text = entry.text or entry.display or "",
      },
    },
  })
end

require("telescope").setup({
  defaults = {
    initial_mode = "normal",
    selection_strategy = "reset",
    sorting_strategy = "ascending",
    layout_strategy = "horizontal",
    path_display = { "truncate" },
    layout_config = {
      horizontal = { prompt_position = "top", preview_width = 0.5 },
      width = 0.9,
      height = 0.9,
      preview_cutoff = 80,
    },
    mappings = {
      n = { ["q"] = send_current_to_qflist },
    },
  },
  pickers = {
    find_files = {
      find_command = { "fd", "--type", "f", "-H", "-E", ".git" },
    },
  },
})
