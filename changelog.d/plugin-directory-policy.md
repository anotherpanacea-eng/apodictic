### Plugin directory policy holds

Commands no longer pre-approve tools through `allowed-tools`; Claude now asks before running
shell commands, writing files, or fetching from the web while a command is active. The plugin
also ships `.claude-plugin/icon.svg` for its directory listing.
