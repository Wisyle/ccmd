from ccmd.core.agents.base import BaseAgent, LaunchContext


class AiderAgent(BaseAgent):
    id = "aider"
    display_name = "Aider"
    brand_color = "#38bdf8"
    ascii_logo = "△"
    binaries = ["aider"]
    install_url = "pip install aider-chat"

    def build_command(self, ctx: LaunchContext) -> list[str]:
        bin_path = self.which()
        if not bin_path:
            raise FileNotFoundError("Aider is not installed")
        cmd = [bin_path, *ctx.extra_args]
        if ctx.initial_prompt:
            cmd.extend(["--message", ctx.initial_prompt])
        return cmd
