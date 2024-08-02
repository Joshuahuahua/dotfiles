local M = {}

---@param config table|nil Configuration table.
---     - border:     (default="none")
---         - The border style of the floating window.
---         - Example: "single", "double", "shadow", "rounded", "solid"
M.show_diagnostics = function(config)
	config = config or {}

	local bufnr = vim.api.nvim_get_current_buf()
	local filetype = vim.api.nvim_buf_get_option(bufnr, "filetype")

	if filetype ~= "typescript" and filetype ~= "typescriptreact" and filetype ~= "typescript.tsx" then
		return
	end

	local line_num = vim.api.nvim_win_get_cursor(0)[1] - 1
	local diagnostics = vim.diagnostic.get(bufnr, { lnum = line_num })

	if #diagnostics == 0 then
		return
	end

	local message = M.create_diagnostics_list(diagnostics)

	local floating_bufnr, floating_winnr =
		vim.lsp.util.open_floating_preview(message, "markdown", { stylize_markdown = true })
end

M.create_diagnostic_message = function(diagnostic)
	local message = diagnostic.message
	local severity_name = vim.diagnostic.severity[diagnostic.severity]:lower():gsub("^%l", string.upper)

	message = message:gsub("Type", "Type:\n")
	-- message = message:gsub("'{", "```typescript\ntype error = {\n")
	-- message = message:gsub(";", ";\n")
	-- message = message:gsub("}'", "}\n```\n")
	message = message:gsub("'", "`")

	return message
end

M.create_diagnostics_list = function(diagnostics)
	local lines = {}

	table.insert(lines, "# Diagnostics")

	for i, diagnostic in ipairs(diagnostics) do
		if diagnostic.source == "typescript" then
			local message = diagnostic.message
			local severity_name = vim.diagnostic.severity[diagnostic.severity]:lower():gsub("^%l", string.upper)

			-- Diagnostic Header
			table.insert(lines, "## " .. severity_name .. " - " .. diagnostic.code)

			-- message = "> [!CAUTION]\n> " .. message
			-- message = "> " .. message

			-- Diagnostic Message
			message = message:gsub("Type", "Type:\n\n")
			message = message:gsub("Did you mean", "\n> [!TIP]\n> Did you mean")
			-- message = message:gsub("'{", "```typescript\ntype error = {\n")
			-- message = message:gsub(";", ";\n")
			-- message = message:gsub("}'", "}\n```\n")
			message = message:gsub("'", "`")

			for line in message:gmatch("[^\n]+") do
				line = line:gsub("^%s*(.-)%s*$", "%1") -- Strip whitespace
				line = line:gsub("manifest", "    manifest")
				if line ~= "" then
					table.insert(lines, line)
				end
			end

			if i ~= #diagnostics then
				table.insert(lines, "")
			end
		end
	end
	return lines
end

return M
