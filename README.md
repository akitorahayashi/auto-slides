## Overview

This repository is a template for building Streamlit applications.

## Setup and Execution

1.  **Initial Setup**

    Run the setup command to install dependencies and create the `.env` file from the example.

    ```bash
    make setup
    ```

2.  **Environment Configuration**

    Modify the `.env` file with your local configuration, such as the host ip and ports.

3.  **Launch Application**

    Start the Streamlit application using the development server.

    ```bash
    make run
    ```

## Development Workflow

-   **Code Formatting**

    To automatically format the code, run:

    ```bash
    make format
    ```

-   **Linter Execution**

    To check the code for linting issues, run:

    ```bash
    make lint
    ```

-   **Testing**

    To run the entire test suite (unit, integration, build, and E2E), use:

    ```bash
    make test
    ```

    You can also run specific test suites:

    ```bash
    make unit-test
    make intg-test
    make build-test
    make e2e-test
    ```
