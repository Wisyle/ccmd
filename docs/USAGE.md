# Usage Guide

## Quick Start

Once installed, CCMD commands work directly in your terminal without any prefix.

## Default Commands

### Navigation Commands

Navigate to common directories quickly:

```bash
go downloads    # cd ~/Downloads
go documents    # cd ~/Documents
go desktop      # cd ~/Desktop
go home         # cd ~
```

### Directory Shortcuts (v1.2.0)

Register your own directories so `go <name>` jumps there instantly:

```bash
ccmd setup          # interactive wizard — walk you through it
```

Or edit `~/.ccmd/shortcuts.yaml` directly:

```yaml
# ~/.ccmd/shortcuts.yaml
projects: /home/user/code/projects
work:     /home/user/work
docs:     /home/user/Documents/writing
```

```bash
go projects         # cd /home/user/code/projects
go work             # cd /home/user/work
```

Your shortcuts merge with the built-in ones. On a collision, yours win.
Re-run `ccmd setup` anytime to add or change shortcuts.

### Git Commands

Streamline your git workflow:

```bash
push "initial commit"    # git add . && git commit -m "..." && git push
push "fixed bug"         # Same as above with different message
```

### System Monitoring Commands

Check system resources:

```bash
cpu             # Show CPU usage
mem             # Show memory usage
proc            # Show running processes
kap 1234        # Kill process by PID
```

### Management Commands

```bash
update          # Reload commands from commands.yaml
restore         # Restore shell configuration from backup
setup           # (v1.2.0) Register directory shortcuts and set master password
```

## Managing Commands

### List All Commands

```bash
python3 run.py --list
```

This displays all available commands with their descriptions.

### Interactive Editor

```bash
python3 run.py --edit
```

The interactive editor allows you to:
- Add new commands
- Edit existing commands
- Delete commands
- Manage SSH aliases
- View command details

### Check System Configuration

```bash
python3 run.py --check
```

This shows:
- Detected operating system
- Detected shell type
- Number of loaded commands
- System status

### Reload Commands

After editing `commands.yaml` manually:

```bash
python3 run.py --reload
```

Or use the `update` command:

```bash
update
```

### Restore Configuration

If something goes wrong:

```bash
python3 run.py --restore
```

Or use the `restore` command:

```bash
restore
```

This restores your shell configuration from the last backup.

## Command Types

CCMD supports different types of commands:

### Simple Commands

Execute a single command:

```bash
# Example: hello command
hello           # Prints "Hello, World!"
```

### Commands with Parameters

Commands that accept user input:

```bash
# Example: greet command
greet           # Prompts for name, then greets you
```

### Multi-option Commands

Commands with multiple sub-options:

```bash
# Example: go command
go downloads    # Option: downloads
go documents    # Option: documents
go desktop      # Option: desktop
```

### OS-specific Commands

Commands that behave differently based on your OS:

```bash
# Example: cpu command
cpu             # Uses 'top' on Linux/macOS, 'Get-Counter' on Windows
```

## Working with SSH

### Using SSH Aliases

If you've configured SSH aliases in commands.yaml:

```bash
myserver        # SSH to your configured server
production      # SSH to production server
staging         # SSH to staging server
```

### Managing SSH Aliases

Use the interactive editor:

```bash
python3 run.py --edit
# Select SSH management option
```

## Best Practices

### 1. Test Commands Before Using

After adding a new command, test it with the full path first:

```bash
python3 run.py yourcommand
```

Then reload to make it available as an alias:

```bash
update
```

### 2. Back Up Important Configurations

CCMD automatically backs up your shell configuration, but you can manually backup commands.yaml:

```bash
cp commands.yaml commands.yaml.backup
```

### 3. Use Descriptive Names

Choose clear, memorable names for your commands:

```bash
# Good
deploy-prod
start-dev
backup-db

# Less clear
dp
sd
bdb
```

### 4. Document Custom Commands

Add clear descriptions to your commands in commands.yaml:

```yaml
commands:
  mycommand:
    description: Clear description of what this does
    action: ...
```

## Tips and Tricks

### Combining Commands

You can chain multiple commands:

```bash
update && go downloads
```

### Using with Git

Quick workflow with the push command:

```bash
# Edit files
push "Added new feature"
# Everything committed and pushed!
```

### Custom Aliases

Create project-specific navigation:

```yaml
commands:
  myproject:
    description: Go to my project
    action: cd ~/Projects/myproject
    type: navigation
```

Then simply:

```bash
myproject       # Instantly in your project directory
```

## Getting Help

### View This Guide

```bash
cat ~/ccmd/USAGE.md
# or open in your preferred editor
```

### Check Command List

```bash
python3 run.py --list
```

### System Check

```bash
python3 run.py --check
```

## Next Steps

- See [RELEASE_NOTES_v1.2.0.md](RELEASE_NOTES_v1.2.0.md) for what's new
- See [SECURITY_CHANGELOG.md](SECURITY_CHANGELOG.md) for security history
- See [README.md](../README.md) for project overview
