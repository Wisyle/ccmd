"""Command parser module for routing and interpreting commands"""

from typing import Tuple, Optional, Dict, Any, List
import sys


class CommandParser:
    """Parse and route commands"""

    def __init__(self, registry):
        """
        Initialize parser with command registry

        Args:
            registry: CommandRegistry instance
        """
        self.registry = registry

    def parse(self, args: List[str]) -> Tuple[Optional[str], Optional[str], Dict[str, Any]]:
        """
        Parse command line arguments

        Args:
            args: Command line arguments (excluding program name)

        Returns:
            Tuple of (command_name, subcommand, parameters)
        """
        if not args:
            return None, None, {}

        command_name = args[0]
        subcommand = None
        parameters = {}

        # Check if command exists
        if not self.registry.command_exists(command_name):
            return None, None, {'error': f"Unknown command: {command_name}"}

        # Get command definition
        command_def = self.registry.get_command(command_name)

        # Check if there's a subcommand
        if len(args) > 1:
            action = command_def.get('action')

            # If action is a dict, second arg might be a subcommand
            if isinstance(action, dict):
                potential_subcommand = args[1]
                if potential_subcommand in action:
                    subcommand = potential_subcommand
                    # Remaining args are parameters
                    parameters = self._parse_parameters(args[2:], command_def)
                else:
                    # Not a valid subcommand
                    parameters = {'error': f"Unknown subcommand: {potential_subcommand}"}
            else:
                # Single action command, remaining args are parameters
                parameters = self._parse_parameters(args[1:], command_def)
        else:
            # No additional arguments
            # Check if command requires parameters
            if self._requires_parameters(command_def):
                parameters = {'error': f"Command '{command_name}' requires additional arguments"}

        return command_name, subcommand, parameters

    def _requires_parameters(self, command_def: Dict[str, Any]) -> bool:
        """
        Check if a command requires parameters

        Args:
            command_def: Command definition

        Returns:
            True if command requires parameters
        """
        action = command_def.get('action', '')

        # Check if action contains parameter placeholders
        if isinstance(action, str):
            return '{' in action and '}' in action
        elif isinstance(action, dict):
            # Check if any action value contains placeholders
            for value in action.values():
                if isinstance(value, str) and '{' in value and '}' in value:
                    return True

        return False

    def _parse_parameters(self, args: List[str], command_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse parameters from remaining arguments

        Args:
            args: Remaining command line arguments
            command_def: Command definition

        Returns:
            Dictionary of parameters
        """
        parameters = {}

        # Check if command has a prompt (indicating it needs specific input)
        if 'prompt' in command_def:
            # Join all remaining args as a single value
            if args:
                param_name = self._extract_param_name(command_def.get('action', ''))
                parameters[param_name] = ' '.join(args)
            else:
                parameters['needs_prompt'] = True
                parameters['prompt'] = command_def['prompt']
        else:
            # Generic parameter handling
            if args:
                # If single arg, try to match to placeholder
                action = command_def.get('action', '')
                if isinstance(action, str):
                    param_name = self._extract_param_name(action)
                    if param_name:
                        parameters[param_name] = args[0]
                elif isinstance(action, dict):
                    # For dict actions, parameters might apply to subcommands
                    parameters['args'] = args

        return parameters

    def _extract_param_name(self, action_string: str) -> Optional[str]:
        """
        Extract parameter name from action string

        Args:
            action_string: Action string with {param} placeholder

        Returns:
            Parameter name or None
        """
        if not isinstance(action_string, str):
            return None

        # Find content between { and }
        start = action_string.find('{')
        end = action_string.find('}')

        if start != -1 and end != -1 and start < end:
            return action_string[start + 1:end]

        return None

    def get_action(self, command_name: str, subcommand: Optional[str] = None,
                   os_type: Optional[str] = None) -> Optional[str]:
        """
        Get the action string for a command

        Args:
            command_name: Name of the command
            subcommand: Optional subcommand
            os_type: Operating system type for OS-specific commands

        Returns:
            Action string or None if not found
        """
        command_def = self.registry.get_command(command_name)
        if not command_def:
            return None

        action = command_def.get('action')

        if isinstance(action, str):
            return action
        elif isinstance(action, dict):
            # If subcommand is provided, use it
            if subcommand and subcommand in action:
                return action[subcommand]

            # If os_type is provided, use OS-specific action
            if os_type and os_type in action:
                os_action = action[os_type]
                # If OS action is also a dict, might need subcommand
                if isinstance(os_action, dict) and subcommand:
                    return os_action.get(subcommand)
                return os_action

            # Fallback to first available action
            if action:
                first_key = next(iter(action))
                return action[first_key]

        return None

    def format_action(self, action: str, parameters: Dict[str, Any]) -> str:
        """
        Format action string with parameters

        Args:
            action: Action string with placeholders
            parameters: Parameter values

        Returns:
            Formatted action string
        """
        if not action:
            return ""

        formatted = action
        for key, value in parameters.items():
            placeholder = f"{{{key}}}"
            if placeholder in formatted:
                formatted = formatted.replace(placeholder, str(value))

        return formatted


def create_parser(registry) -> CommandParser:
    """
    Factory function to create a command parser

    Args:
        registry: CommandRegistry instance

    Returns:
        CommandParser instance
    """
    return CommandParser(registry)
