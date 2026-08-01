from ccmd.core.agents.base import BaseAgent, LaunchContext


class CursorAgent(BaseAgent):
    id = "cursor"
    display_name = "Cursor Agent"
    brand_color = "#7c3aed"
    ascii_logo = "◇"
    binaries = ["cursor-agent", "cursor"]
    install_url = "Install Cursor and ensure cursor-agent is on PATH"

    def build_command(self, ctx: LaunchContext) -> list[str]:
        bin_path = self.which()
        if not bin_path:
            raise FileNotFoundError("Cursor Agent is not installed")
        cmd = [bin_path, *ctx.extra_args]
        if ctx.initial_prompt:
            cmd.append(ctx.initial_prompt)
        return cmd
