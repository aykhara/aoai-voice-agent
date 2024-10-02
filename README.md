# Voice Agent with Azure OpenAI and Azure AI Speech

## Prerequisites

Ensure you have Python installed on your system. This script requires Python 3.10 or higher.

### Setup Azure Resources

To create the necessary Azure resources, you can use the [iac-promptflow-starter](https://github.com/aykhara/iac-promptflow-starter) repository. Follow these steps:

1. Fork the repository:

   - Go to the [iac-promptflow-starter repository](https://github.com/aykhara/iac-promptflow-starter) on GitHub.
   - Click the "Fork" button in the top-right corner of the page.
   - Choose your GitHub account to fork the repository.

1. Clone your forked repository:

   ```sh
   git clone https://github.com/<your-username>/iac-promptflow-starter.git
   cd iac-promptflow-starter

   ```

1. Follow the instructions in the repository's README to set up the required Azure resources.

## Setup

1. **Install Dependencies**

   Use pip to install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

1. **Create .env file**

   Copy `.env.template` to `.env` and fill in the necessary values.

## Usage

Run the `main.py` script to use Azure AI Speech to converse with Azure OpenAI Service.

```sh
python -m main
```
