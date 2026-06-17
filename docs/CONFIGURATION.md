# Configuration Guide

## Overview

CCMD commands are defined in `commands.yaml` in the CCMD directory. This file uses YAML format for easy editing.

## Basic Structure

```yaml
commands:
  command_name:
    description: Description of what the command does
    action: shell command to execute
    type: category (git/system/navigation/custom)
    prompt: Optional prompt for parameters (if needed)
```

## Simple Commands

### Basic Example

```yaml
commands:
  hello:
    description: Print hello world
    action: echo "Hello, World!"
    type: custom
```

Usage:
```bash
hello           # Prints: Hello, World!
```

### Multiple Simple Commands

```yaml
commands:
  hello:
    description: Print hello world
    action: echo "Hello, World!"
    type: custom

  date:
    description: Show current date
    action: date
    type: system

  myip:
    description: Show my IP address
    action: curl -s ifconfig.me
    type: network
```

## Commands with Parameters

### Single Parameter

```yaml
commands:
  greet:
    description: Greet a user
    action: echo "Hello, {name}!"
    type: custom
    prompt: Enter your name
```

Usage:
```bash
greet
# Prompts: Enter your name
# You type: John
# Output: Hello, John!
```

### Multiple Parameters

```yaml
commands:
  connect:
    description: Connect to database
    action: psql -h {host} -U {user} -d {database}
    type: database
    prompt: Enter host, user, database (space-separated)
```

## Multi-option Commands

### Navigation Example

```yaml
commands:
  go:
    description: Navigate to directories
    action:
      downloads: cd ~/Downloads
      documents: cd ~/Documents
      desktop: cd ~/Desktop
      home: cd ~
      work: cd ~/Projects/work
      personal: cd ~/Projects/personal
    type: navigation
```

Usage:
```bash
go downloads    # cd ~/Downloads
go work         # cd ~/Projects/work
```

### Project Shortcuts

```yaml
commands:
  project:
    description: Navigate to projects
    action:
      web: cd ~/Projects/website
      api: cd ~/Projects/api
      mobile: cd ~/Projects/mobile-app
      scripts: cd ~/Scripts
    type: navigation
```

## OS-specific Commands

### Cross-platform System Commands

```yaml
commands:
  cpu:
    description: Show CPU usage
    action:
      linux: top -bn1 | grep "Cpu(s)"
      macos: top -l 1 | grep "CPU usage"
      windows: powershell "Get-Counter '\Processor(_Total)\% Processor Time'"
    type: system

  mem:
    description: Show memory usage
    action:
      linux: free -h
      macos: vm_stat
      windows: systeminfo | findstr "Memory"
    type: system
```

### Platform-specific Tools

```yaml
commands:
  update-system:
    description: Update system packages
    action:
      linux: sudo apt update && sudo apt upgrade -y
      macos: brew update && brew upgrade
      windows: winget upgrade --all
    type: system
```

## Advanced Examples

### Docker Shortcuts

```yaml
commands:
  dps:
    description: List Docker containers
    action: docker ps -a
    type: docker

  dstop:
    description: Stop all Docker containers
    action: docker stop $(docker ps -q)
    type: docker

  dclean:
    description: Clean Docker system
    action: docker system prune -a -f
    type: docker

  dlogs:
    description: View Docker container logs
    action: docker logs -f {container}
    type: docker
    prompt: Enter container name or ID
```

### Development Shortcuts

```yaml
commands:
  dev:
    description: Start development server
    action: npm run dev
    type: development

  build:
    description: Build and test project
    action: npm run build && npm run test
    type: development

  deploy:
    description: Deploy to production
    action: npm run build && npm run deploy
    type: deployment

  lint:
    description: Run linter
    action: npm run lint -- --fix
    type: development
```

### Git Workflows

```yaml
commands:
  push:
    description: Git add, commit, and push
    action: git add . && git commit -m "{message}" && git push
    type: git
    prompt: Enter commit message

  pull:
    description: Git pull with rebase
    action: git pull --rebase
    type: git

  status:
    description: Git status short
    action: git status -s
    type: git

  branch:
    description: Create and checkout new branch
    action: git checkout -b {branch}
    type: git
    prompt: Enter branch name
```

### SSH Configuration

```yaml
commands:
  myserver:
    description: SSH to my server
    action: ssh user@example.com -p 22
    type: ssh
    ssh_config:
      host: example.com
      user: myuser
      port: 22
      key_file: ~/.ssh/id_rsa

  production:
    description: SSH to production server
    action: ssh -i ~/.ssh/prod_key admin@prod.example.com
    type: ssh
    ssh_config:
      host: prod.example.com
      user: admin
      port: 22
      key_file: ~/.ssh/prod_key
```

### Database Operations

```yaml
commands:
  db-backup:
    description: Backup database
    action: pg_dump mydb > ~/backups/mydb_$(date +%Y%m%d).sql
    type: database

  db-restore:
    description: Restore database
    action: psql mydb < {file}
    type: database
    prompt: Enter backup file path

  db-connect:
    description: Connect to database
    action: psql -h localhost -U postgres -d mydb
    type: database
```

### File Operations

```yaml
commands:
  backup:
    description: Backup important files
    action: tar -czf ~/backups/backup_$(date +%Y%m%d).tar.gz {path}
    type: file
    prompt: Enter path to backup

  extract:
    description: Extract archive
    action: tar -xzf {file}
    type: file
    prompt: Enter archive file path

  search:
    description: Search for files
    action: find . -name "{pattern}"
    type: file
    prompt: Enter search pattern
```

## Command Types

Use these standard types for organization:

- `navigation` - Directory navigation
- `git` - Git operations
- `system` - System commands
- `docker` - Docker operations
- `development` - Development tasks
- `deployment` - Deployment operations
- `database` - Database operations
- `ssh` - SSH connections
- `file` - File operations
- `network` - Network operations
- `custom` - Custom commands

## Best Practices

### 1. Use Clear Descriptions

```yaml
# Good
description: Deploy application to production server

# Less clear
description: Deploy
```

### 2. Sanitize User Input

Avoid commands that could be dangerous with user input:

```yaml
# Dangerous - could allow command injection
action: rm -rf {path}

# Better - use specific, limited options
action:
  cache: rm -rf ~/.cache/myapp
  logs: rm -rf ~/.myapp/logs
```

### 3. Group Related Commands

```yaml
commands:
  # Docker commands
  dps:
    description: List containers
    ...
  dstop:
    description: Stop containers
    ...

  # Git commands
  push:
    description: Push changes
    ...
  pull:
    description: Pull changes
    ...
```

### 4. Test Before Deploying

Always test new commands:

```bash
python3 run.py yourcommand
```

### 5. Keep Backups

Before major changes:

```bash
cp commands.yaml commands.yaml.backup
```

## Reloading Configuration

After editing `commands.yaml`:

```bash
# Option 1: Use reload command
python3 run.py --reload

# Option 2: Use update command (if installed)
update

# Option 3: Reinstall
python3 run.py --install
```

## Security Considerations

### Input Validation

CCMD automatically validates and sanitizes:
- User input parameters
- Command execution
- File paths

### Dangerous Patterns

These patterns are blocked by default:
- `rm -rf /`
- `:(){ :|:& };:`
- Unescaped special characters in user input

### Safe Command Design

```yaml
# Safe - predefined options
go:
  action:
    downloads: cd ~/Downloads
    documents: cd ~/Documents

# Less safe - user input in critical commands
delete:
  action: rm -rf {path}    # Avoid this pattern
```

## Next Steps

- See [USAGE.md](USAGE.md) for how to use commands
- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
- See [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
