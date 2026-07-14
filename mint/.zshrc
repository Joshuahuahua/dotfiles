#!/usr/bin/env zsh

local this_file repo_root
this_file="${${(%):-%N}:A}"
repo_root="${this_file:h:h}"

source "$repo_root/.zshrc"

# Mint-specific zsh config goes here.
