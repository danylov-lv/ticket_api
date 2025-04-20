# Ticket API
---

## Table of Contents
- [Introduction](#introduction)
- [Installation & Usage](#installation--usage)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Architecture](#architecture)
- [Design Patterns](#design-patterns)
- [Challenges Faced](#challenges-faced)
- [Improvements](#improvements)


## Introduction
This project is a simple ticketing system that allows users to create support tickets, add messages to them, and receive AI-generated responses. It uses FastAPI for the backend, SQLAlchemy for ORM, and PostgreSQL as the database. The project also includes JWT authentication for user management. The AI integration is done using Groq's API to generate responses based on the ticket description and message history. AI integration is not limited to Groq, it uses the OpenAI API as an universal interface for many AI provider.

## Installation & Usage
To set up the project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone [repository_url]
   ```

2. Navigate to the project directory:
   ```bash
   cd [project_directory]
   ```

3. Install the required packages using Poetry:
   ```bash
   poetry install
   ```

4. Setup the environment variables. (see the [Configuration](#configuration) section or `.env.example` file for more details).

5. Run the database migrations:
   ```bash
   poetry run alembic upgrade head
   ```

6. Create a superuser (admin) account:
   ```bash
   poetry run ticket-api create-superuser
   ```

7.  Start the FastAPI server:
   ```bash
    poetry run ticket-api run [--mode dev|prod] 
    ```

To run in the Docker container, use the following command:
```bash
docker-compose up --build
```

To stop the Docker container, use:
```bash
docker-compose down
```

This will start the FastAPI server and PostgreSQL database in a Docker container. You can access the API at `http://localhost:8000`.

## Configuration

The project uses environment variables for configuration. Create a `.env` file in the root directory and add the following variables:

```env
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=ticket_db
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=your_openai_api_base
```

You can also use the `.env.example` file as a template.

To obtain secret key, you can use the following command:
```bash
openssl rand -hex 32
```

## API Endpoints

The API provides the following endpoints:

- **User Authentication**:
  - `POST /auth/register`: Create a new user account.
  - `POST /auth/login`: Log in and obtain a JWT token.
  - `POST /auth/logout`: Log out and invalidate the JWT token.
  - `GET /users/me`: Get the current user's information.
  - `PATCH /users/me`: Update the current user's information.
  - `GET /users/{user_id}`: Get a specific user's information (admin only).
  - `PATCH /users/{user_id}`: Update a specific user's information (admin only).
  - `DELETE /users/{user_id}`: Delete a specific user (admin only).

- **Ticket Management**:
  - `GET /tickets/statuses`: Get all possible ticket statuses.
  - `POST /tickets/statuses`: Create a new ticket status (admin only).
  - `DELETE /tickets/statuses/{status_id}`: Delete a specific ticket status (admin only).
  - `GET /tickets`: List all tickets for the current user.
  - `POST /tickets`: Create a new support ticket.
  - `GET /tickets/{ticket_id}`: Get a specific ticket's details and messages (owner or admin only).
  - `PATCH /tickets/{ticket_id}`: Update a specific ticket's details (owner or admin only).
  - `DELETE /tickets/{ticket_id}`: Delete a specific ticket (owner or admin only).
  - `POST /tickets/{ticket_id}/messages`: Add a new message to a specific ticket (owner or admin only).
  - `GET /tickets/{ticket_id}/ai-response`: Get AI-generated response for a specific ticket (owner or admin only). It streams the response using Server-Sent Events (SSE).


## Architecture

The project follows a modular feature-based architecture. Each feature is organized into its own directory, containing the necessary files for models, schemas, routes, and services.
Feature-based architecture provides good separation of concerns and makes it easier to manage and scale the project. Each feature can be developed, tested, and maintained independently. To add a new feature or whole new module, you can simply create a new directory and add the necessary files. This allows for better organization and makes it easier to navigate the codebase.

The main components of the architecture are:
- **Models**: SQLAlchemy models representing the database tables.
- **Schemas**: Pydantic models for data validation and serialization.
- **Routes**: FastAPI routes for handling API requests and responses.
- **Services**: Business logic and database operations.
- **Dependencies**: Common dependencies used across multiple routes.
- **Repositories**: Database access layer for interacting with the models.

Most of the code is organized in a way that allows for easy testing and maintainability. 
Schemas use inheritance to create a base schema for common fields, and models use mixins to share common functionality. 
Repositories and services are separated to keep the code clean and organized. They also use encapsulation and abstraction to hide implementation details and provide a clear interface for interacting with the database. It lets you easily swap out the database implementation if needed.

## Design Patterns

The project uses several design patterns to improve code organization and maintainability:

- **Repository Pattern**: Separates the data access logic from the business logic. Each model has a corresponding repository that handles database operations.
- **Service Pattern**: Encapsulates the business logic and interacts with the repositories. This allows for better separation of concerns and makes it easier to test the code.
- **Dependency Injection**: FastAPI's dependency injection system is used to manage dependencies and provide them to the routes. This allows for better testability and modularity.
- **Singleton Pattern**: The database session is created as a singleton to ensure that only one instance is used throughout the application. This helps to manage database connections efficiently.
- **Strategy Pattern**: The AI integration uses a strategy pattern to allow for different AI providers. This makes it easy to switch between different providers without changing the core logic of the application.

## Challenges Faced

- **AI Integration**: Integrating with the AI provider was challenging due to the need for proper request formatting and handling streaming responses. Also it required implementing service-like interface to support multiple providers and separate concerns. But once the integration was set up, it worked smoothly.

## Improvements

- **Testing**: The project could benefit from more comprehensive unit and integration tests. While some things work because of implementation, it would be better to have tests to ensure that everything works as expected.
- **Documentation**: The API documentation could be improved with more detailed descriptions of the endpoints and their parameters. This would help users understand how to use the API more effectively.
- **Automate Ticket Statuses**: The ticket statuses are currently hardcoded. It would be better to automate the creation of ticket statuses based on the workflow. And also update them automatically based on the ticket's progress.
- **Rate Limiting**: Implementing rate limiting for the API endpoints would help prevent abuse and ensure fair usage of the resources.
- **Caching**: Implementing caching for frequently accessed data (e.g., ticket statuses) would improve performance and reduce database load.
- **Error Handling**: Improving error handling and providing more informative error messages would enhance the user experience. Currently, some errors are not handled properly, and users may not understand what went wrong.
