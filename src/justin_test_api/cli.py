from pathlib import Path
from typer import Typer, Option


from fastapi_cli.cli import dev, run

app = Typer()


@app.command()
def api(
    mode: str = Option("dev", help="Mode to run the API in."),
):
    if mode not in ["dev", "prod"]:
        raise ValueError("Invalid mode. Choose 'dev' or 'prod'.")

    command = dev if mode == "dev" else run
    command(Path("./src/justin_test_api/api.py"))


def main():
    app()
