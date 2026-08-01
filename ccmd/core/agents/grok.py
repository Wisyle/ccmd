from ccmd.core.agents.base import BaseAgent, LaunchContext


class GrokAgent(BaseAgent):
    id = "grok"
    display_name = "Grok Build"
    brand_color = "#ffffff"
    ascii_logo = "✦"
    binaries = ["grok"]
    install_url = "curl -fsSL https://x.ai/cli/install.sh | bash"

    def build_command(self, ctx: LaunchContext) -> list[str]:
        bin_path = self.which()
        if not bin_path:
            raise FileNotFoundError("Grok is not installed")
        cmd = [bin_path, *ctx.extra_args]
        if ctx.initial_prompt:
            cmd.append(ctx.initial_prompt)
        return cmd
