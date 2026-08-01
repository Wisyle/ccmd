from ccmd.core.agents.base import BaseAgent, LaunchContext


class ClaudeAgent(BaseAgent):
    id = "claude"
    display_name = "Claude Code"
    brand_color = "#d97757"
    ascii_logo = "◈"
    binaries = ["claude"]
    install_url = "npm install -g @anthropic-ai/claude-code"

    def _prompt_args(self, prompt: str) -> list[str]:
        return ["-p", prompt]

    def build_command(self, ctx: LaunchContext) -> list[str]:
        bin_path = self.which()
        if not bin_path:
            raise FileNotFoundError("Claude Code is not installed")
        cmd = [bin_path, *ctx.extra_args]
        if ctx.initial_prompt:
            cmd.extend(["-p", ctx.initial_prompt])
        return cmd
