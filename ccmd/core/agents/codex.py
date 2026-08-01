from ccmd.core.agents.base import BaseAgent, LaunchContext


class CodexAgent(BaseAgent):
    id = "codex"
    display_name = "Codex"
    brand_color = "#10a37f"
    ascii_logo = "◎"
    binaries = ["codex"]
    install_url = "npm i -g @openai/codex  # or curl install from OpenAI"

    def build_command(self, ctx: LaunchContext) -> list[str]:
        bin_path = self.which()
        if not bin_path:
            raise FileNotFoundError("Codex is not installed")
        cmd = [bin_path, *ctx.extra_args]
        if ctx.initial_prompt:
            cmd.append(ctx.initial_prompt)
        return cmd
