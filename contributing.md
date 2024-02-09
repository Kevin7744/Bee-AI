# Contributing to Bee-AI Chatbot

Thank you for considering contributing to Bee-AI Chatbot! This document provides guidelines for adding a new tool to enhance the functionality of the chatbot.

## Getting Started

Before adding a new tool, make sure you have the following prerequisites installed:

- Python 3.x
- Git

## Steps to Add a New Tool

1. **Clone the Repository**: Fork the Bee-AI Chatbot repository to your GitHub account and clone it to your local machine.

    ```bash
    git clone https://github.com/your_username/bee-ai-chatbot.git
    ```

2. **Create a New Branch**: Create a new branch for your changes.

    ```bash
    git checkout -b feature/new-tool
    ```

3. **Implement the Tool**: Create a new Python file for your tool in the `Functions` directory. Ensure the tool class inherits from `BaseTool` and implements the required methods. Add the tool to the `main.py` file and update the system-message.

4. **Write Tests**: Write unit tests for your tool to ensure its functionality and integration with the chatbot.

5. **Update README**: If your tool introduces significant changes or new features, update the README.md file to reflect these changes.

6. **Commit Changes**: Commit your changes with descriptive commit messages.

    ```bash
    git add .
    git commit -m "Add new tool for XYZ functionality"
    ```

7. **Push Changes**: Push your changes to your forked repository.

    ```bash
    git push origin feature/new-tool
    ```

8. **Create Pull Request**: Submit a pull request to the main Bee-AI Chatbot repository. Provide a clear title and description for your pull request, detailing the changes made and the purpose of the new tool.

9. **Review and Collaborate**: Collaborate with other contributors and address any feedback or suggestions provided during the review process.

10. **Merge Pull Request**: Once your pull request is approved, it will be merged into the main branch, and your new tool will be integrated into the Bee-AI Chatbot.

## Code Style and Guidelines

- Follow Python PEP 8 style guide for code formatting.
- Write clear and concise code with descriptive variable and function names.
- Include docstrings and comments where necessary to improve code readability.

## Testing

- Ensure all unit tests pass before submitting your pull request.
- Write comprehensive unit tests to cover all aspects of your tool's functionality.
- Test edge cases and handle exceptions gracefully.

## License

By contributing to the Bee-AI Chatbot project, you agree that your contributions will be licensed under the [MIT License](LICENSE).

## Need Help?

If you need any assistance or have questions regarding the contribution process, feel free to reach out to the project maintainers or open an issue for discussion.
