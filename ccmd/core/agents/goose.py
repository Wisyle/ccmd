from ccmd.core.agents.base import BaseAgent, LaunchContext


class GooseAgent(BaseAgent):
    id = "goose"
    display_name = "Goose"
    brand_color = "#f59e0b"
    ascii_logo = "✱"
    binaries = ["goose"]
    install_url = "https://block.github.io/goose/ — install goose CLI"

    def build_command(self, ctx: LaunchContext) -> list[str]:
        bin_path = self.which()
        if not bin_path:
            raise FileNotFoundError("Goose is not installed")
        # interactive session by default; with prompt use run
        if ctx.initial_prompt:
            return [bin_path, "run", "-t", ctx.initial_prompt, *ctx.extra_args]
        return [bin_path, *ctx.extra_args] if ctx.extra_args else [bin_path, "session"]
