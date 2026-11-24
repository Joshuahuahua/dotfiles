require("minuet").setup({
  provider = "openai_fim_compatible",
  n_completions = 1,
  context_window = 512,

  -- Wait 600ms after typing before requesting a completion.
  debounce = 600,

  -- Don't send requests more frequently than every 1500ms.
  throttle = 1500,

  provider_options = {
    openai_fim_compatible = {
      api_key = "TERM", -- name of an env var that always exists; Ollama ignores the key
      name = "Ollama",
      end_point = "http://localhost:11434/v1/completions",
      model = "qwen2.5-coder:3b-base",
      stream = true,
      optional = {
        max_tokens = 56,
        top_p = 0.9,
      },
    },
  },

  virtualtext = {
    auto_trigger_ft = { "*" },
    keymap = {
      accept = "<A-f>",
      accept_line = "<A-e>",
      accept_n_lines = "<A-z>",
      prev = "<A-[>",
      next = "<A-]>",
      dismiss = "<A-c>",
    },
  },
})
