import asyncio
from pathlib import Path

from fastapi_cli.cli import dev as dev_command
from fastapi_cli.cli import run as run_command
from typer import Argument, Exit, Typer, echo, prompt

from .auth.dependencies import get_user_repository, get_user_service
from .auth.schemas import UserCreate
from .dependencies import get_async_session

app = Typer()


@app.command()
def run(
    mode: str = Argument("dev", help="Mode to run the API in."),
):
    if mode not in ["dev", "prod"]:
        raise ValueError("Invalid mode. Choose 'dev' or 'prod'.")

    command = dev_command if mode == "dev" else run_command
    command(Path("./src/ticket_api/api.py"))


@app.command()
def create_superuser():
    email = prompt("Email")
    password = prompt("Password", hide_input=True)
    password2 = prompt("Confirm password", hide_input=True)

    if password != password2:
        raise ValueError("Passwords do not match.")

    async def _create():
        async for session in get_async_session():
            async for user_repository in get_user_repository(session):
                async for user_service in get_user_service(user_repository):
                    try:
                        user_create = UserCreate(
                            email=email,
                            password=password,
                            is_active=True,
                            is_superuser=True,
                        )
                        user = await user_service.create(user_create)
                        echo(
                            f"Superuser created with ID: {user.id} and email: {user.email}"
                        )
                    except Exception as e:
                        echo(f"Error creating superuser: {e}")
                        raise Exit(1)

    asyncio.run(_create())


def main():
    app()
