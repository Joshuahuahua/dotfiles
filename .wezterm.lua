-- Pull in the wezterm API
local wezterm = require 'wezterm'

-- This table will hold the configuration.
local config = {}

-- In newer versions of wezterm, use the config_builder which will
-- help provide clearer error messages
if wezterm.config_builder then
  config = wezterm.config_builder()
end

-- This is where you actually apply your config choices

-- For example, changing the color scheme:
-- config.color_scheme = 'Belge (terminal.sexy)'
config.color_scheme = "Tokyo Night Storm"

-- Spawn a pwsh shell
-- config.default_prog = { 'pwsh' }
config.wsl_domains = { {name="WSL:Ubuntu", distribution="Ubuntu-24.04"} }
config.default_domain = "WSL:Ubuntu"

-- and finally, return the configuration to wezterm
return config
