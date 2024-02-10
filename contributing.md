# Contributing to Bee-AI Chatbot

Thank you for considering contributing to Bee-AI Chatbot! This document provides guidelines for adding a new tool to enhance the functionality of the chatbot.

## Getting Started

Before adding a new tool, make sure you have the following prerequisites installed:

- Python 3.x
- Install the necessary dependencies using the [requirements.txt](requirements.txt)
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

3. **Implement the Tool**: 
    - Create new directory in the [Functions](Functions) directory.
    - Add a pydantic class of the tool with its desctiptions.
    - Ensure the tool class inherits from `BaseTool` and implements the required methods. 
    - Add the tool to the [main.py](main.py) file and update the system-message with context of the tool added.

4. **Update README**: If your tool introduces significant changes or new features, update the README.md file to reflect these changes.

5. **Commit Changes**: Commit your changes with descriptive commit messages.

    ```bash
    git add .
    git commit -m "Add new tool for XYZ functionality"
    ```

6. **Push Changes**: Push your changes to your forked repository.

    ```bash
    git push origin feature/new-tool
    ```

7. **Create Pull Request**: Submit a pull request to the main Bee-AI Chatbot repository. Provide a clear title and description for your pull request, detailing the changes made and the purpose of the new tool.

8. **Review and Collaborate**: Collaborate with other contributors and address any feedback or suggestions provided during the review process.

9. **Merge Pull Request**: Once your pull request is approved, it will be merged into the main branch, and your new tool will be integrated into the Bee-AI Chatbot.

## Code Style and Guidelines

- Follow Python PEP 8 style guide for code formatting.
- Write clear and concise code with descriptive variable and function names.
- Include docstrings and comments where necessary to improve code readability.


## License

By contributing to the Bee-AI Chatbot project, you agree that your contributions will be licensed under the [MIT License](LICENSE).

## Need Help?

If you need any assistance or have questions regarding the contribution process, feel free to reach out to the project maintainers or open an issue for discussion.
