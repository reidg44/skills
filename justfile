# Agent skills: one repo, installed as a plugin in Claude Code, Codex, and Copilot CLI.

default:
    @just --list

# Scaffold a new skill: just new my-skill "Does X. Use when Y."
new name description:
    mkdir -p skills/{{name}}
    printf -- '---\nname: {{name}}\ndescription: {{description}}\n---\n\n# {{name}}\n\nTODO: instructions.\n' > skills/{{name}}/SKILL.md
    @echo "Created skills/{{name}}/SKILL.md"

# Validate manifests and skill frontmatter
validate:
    command claude plugin validate .
    jq empty plugin.json .claude-plugin/plugin.json .claude-plugin/marketplace.json .agents/plugins/marketplace.json
    @for f in skills/*/SKILL.md; do \
        grep -q '^name:' "$f" && grep -q '^description:' "$f" || { echo "✗ $f missing name/description"; exit 1; }; \
    done; echo "✔ all SKILL.md files have name + description"

# Bump the patch version in plugin.json (Copilot/Codex). Run before pushing skill changes.
bump:
    jq '.version |= (split(".") | .[2] = ((.[2]|tonumber)+1|tostring) | join("."))' plugin.json > plugin.json.tmp && mv plugin.json.tmp plugin.json
    @jq -r '"version -> " + .version' plugin.json

# Try the plugin in Claude Code straight from this checkout (no install)
try prompt="hello skills":
    command claude --plugin-dir . -p "{{prompt}}"
