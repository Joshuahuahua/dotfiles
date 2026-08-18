-- Custom 99.nvim provider that uses `pi` (pi.dev) instead of the built-in
-- claude/opencode/cursor-agent/gemini CLIs, so it rides on the same GitHub
-- Copilot license/subscription pi itself uses.
--
-- `pi` behaves like the other coding-agent CLIs 99 supports: given
-- `--print`, it runs non-interactively, has its own read/edit/write/bash
-- tools, and can be pointed at a specific provider/model. 99's prompt
-- template tells the agent to write its result to a TEMP_FILE using its
-- own file tools, which `pi --approve` (skip permission prompts) handles
-- the same way ClaudeCodeProvider's `--dangerously-skip-permissions` does.

local BaseProvider = require("99.providers").BaseProvider

--- @class PiProvider : _99.Providers.BaseProvider
local PiProvider = setmetatable({}, { __index = BaseProvider })

--- @param query string
--- @param context _99.Prompt
--- @return string[]
function PiProvider._build_command(_, query, context)
	return {
		"pi",
		"--print",
		"--approve",
		"--provider",
		"github-copilot",
		"--model",
		context.model,
		query,
	}
end

--- @return string
function PiProvider._get_provider_name()
	return "PiProvider"
end

--- @return string
function PiProvider._get_default_model()
	return "claude-sonnet-5"
end

--- @param callback fun(models: string[]|nil, err: string|nil): nil
function PiProvider.fetch_models(callback)
	vim.system(
		{ "pi", "--list-models", "github-copilot" },
		{ text = true },
		function(obj)
			vim.schedule(function()
				if obj.code ~= 0 then
					callback(nil, "Failed to fetch models from pi")
					return
				end
				local models = {}
				-- skip the header row, take the 2nd column ("model")
				local lines = vim.split(obj.stdout, "\n", { trimempty = true })
				for i, line in ipairs(lines) do
					if i > 1 then
						local id = line:match("^%S+%s+(%S+)")
						if id then
							table.insert(models, id)
						end
					end
				end
				callback(models, nil)
			end)
		end
	)
end

local _99 = require("99")

_99.setup({
	provider = PiProvider,
	tmp_dir = "./tmp",
	md_files = {
		"AGENT.md",
		"AGENTS.md",
	},
})

vim.keymap.set("v", "<leader>9v", function()
	_99.visual()
end, { desc = "99: replace visual selection" })

vim.keymap.set("n", "<leader>9s", function()
	_99.search()
end, { desc = "99: search" })

vim.keymap.set("n", "<leader>9x", function()
	_99.stop_all_requests()
end, { desc = "99: stop all requests" })

-- Model/provider pickers, via telescope (already installed)
vim.keymap.set("n", "<leader>9m", function()
	require("99.extensions.telescope").select_model()
end, { desc = "99: select model" })
