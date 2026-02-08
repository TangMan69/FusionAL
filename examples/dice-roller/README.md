# 🎲 Dice Roller MCP Server

A Model Context Protocol server that provides D&D and tabletop gaming dice rolling functionality.

## Features

- **Roll Dice** - Standard notation (2d6+3, 1d20, etc.)
- **D&D Stats** - 4d6 drop lowest ability score generation
- **Coin Flips** - Single or multiple coin flips
- **Skill Checks** - Roll against DC with modifiers

## Quick Start

```bash
# Build the image
docker build -t dice-mcp-server .

# Register with Claude Desktop
# Add to ~/.config/Claude/claude_desktop_config.json
```

## Usage

In Claude Desktop:
- "Roll 2d6+5 for damage"
- "Generate D&D ability scores"
- "Flip 3 coins"
- "Make a stealth check against DC 15 with +2 modifier"
