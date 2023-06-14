# Contributing to AgentAI

Hey there! We're thrilled to see your interest in contributing to AgentAI. As an open-source project navigating the fast-paced realm of AI, we're always on the lookout for contributions. Whether it's in the form of new features, infrastructure enhancements, documentation improvements, or bug fixes, your input is highly valued.

## 🗺️ Guidelines

### 👩‍💻 Code Contributions

To contribute code, we'd love for you to follow a ["fork and pull request"](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) process. Please avoid direct pushes to this repository unless you're a maintainer.

When opening pull requests, kindly adhere to the pull request template provided. Remember to note related issues and tag the appropriate maintainers.

Before pull requests can be merged, they must pass our formatting, linting, and testing checks. See the [Common Tasks](#-common-tasks) section for guidance on running these checks locally.

We place a high premium on robust documentation and testing. If you:

- Fix a bug - please consider adding a relevant unit or integration test when possible. These can be found in `tests`.
- Improve existing features - please update any affected example notebooks and documentation in `docs`. Also, update unit and integration tests where relevant.
- Add a new feature - please create a demo notebook in `docs/modules` and add corresponding unit and integration tests.

Our team is small and focused on building. If you'd like to add or modify something, the best way to catch our attention is by opening a pull request.

### 🚩GitHub Issues

We maintain an up-to-date [issues](https://github.com/NirantK/agentai/issues) page, where you can find bugs, improvements, and feature requests.

We utilize a taxonomy of labels for easy sorting and discovery of issues. These labels are great tools to help organize issues.

If you start working on an issue, please assign it to yourself.

When adding an issue, please focus on a single, modular bug/improvement/feature. If issues are related or blocking, link them instead of combining them.

We strive to keep these issues as current as possible, although the rapid pace of development in this field might cause some to fall behind. If you notice this happening, please let us know.

### 🙋Getting Help

We're committed to ensuring a seamless developer setup experience. If you encounter any challenges, please reach out to a maintainer! Not only do we want to assist you, but we also aim to streamline the process for future contributors.

Similarly, we enforce certain linting, formatting, and documentation standards in the codebase. If these are posing a challenge or annoyance, feel free to ask a maintainer for help. We wouldn't want these standards to hinder your contribution of quality code.

## 🚀 Quick Start

This project uses [Poetry](https://python-poetry.org/) as a dependency manager. Check out Poetry's [documentation on how to install it](https://python-poetry.org/docs/#installation) on your system before proceeding.

❗Note: If you use `Conda` or `Pyenv` as your environment/package manager, please do the following to avoid dependency conflicts:

1. _Before installing Poetry_, create and activate a new Conda env (e.g. `conda create -n agentai python=3.9`)
2. Install Poetry (see above)
3. Configure Poetry to use the virtualenv python environment (`poetry config virtualenvs.prefer-active-python true`)
4. Continue with the following steps.
