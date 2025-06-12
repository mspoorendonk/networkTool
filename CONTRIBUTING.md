# Contributing to Network Tool

Thank you for your interest in contributing to Network Tool! We welcome contributions from the community to help improve and expand the functionality of the application. Below are some guidelines to help you get started.

## How to Contribute

1. **Fork the Repository**:
   - Click the 'Fork' button at the top right of the repository page to create your own copy of the repository.

2. **Create a New Branch**:
   - Create a new branch for your feature or bug fix. Use a descriptive name for your branch.
     ```sh
     git checkout -b feature/your-feature-name
     ```

3. **Make Your Changes**:
   - Make the necessary changes to the codebase. Ensure that your code follows the project's coding standards and guidelines.

4. **Commit Your Changes**:
   - Commit your changes with a clear and concise commit message.
     ```sh
     git commit -m 'Add your commit message here'
     ```

5. **Push Your Changes**:
   - Push your changes to your forked repository.
     ```sh
     git push origin feature/your-feature-name
     ```

6. **Create a Pull Request**:
   - Go to the original repository and click on the 'Compare & pull request' button to create a new pull request. Provide a detailed description of your changes and why you made them.

## Coding Standards

- Follow PEP 8 guidelines for Python code.
- Use meaningful variable and function names.
- Write clear and concise docstrings for all functions and classes.
- Ensure that your code is well-documented and easy to understand.
- Although this is currently only tested on windows, try to make it as cross-platform as possible, such that in the future it can also be used on linux.

## Testing

- Write unit tests for your changes to ensure that they work as expected.
- Run the existing test suite to make sure that your changes do not break any existing functionality.
   ```sh
   poetry run pytest
   ```

## Releasing
- Thoroughly test and ensure all tests complete succesfully
- Update the version number in inno setup script.iss to a new version: #define MyAppVersion "1.1.0" 
- Build an installer by running the package.bat
- Test the installer by running it
- Push all changes to main
- Tag the codebase in github with that same version number.
- Create a new release on github with the tag and a description of the changes and upload the installe

## License

By contributing to Network Tool, you agree that your contributions will be licensed under the GNU General Public License version 3. See the `LICENSE` file for more details.

## Contact

If you have any questions or need further assistance, please use github issues
