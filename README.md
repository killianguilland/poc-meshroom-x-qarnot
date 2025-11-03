# poc-meshroom-x-qarnot

> Small proof-of-concept that runs a meshroom_batch command inside a Qarnot task running the meshroom docker image.

## Installation

Setup with pipenv:

1. Install pipenv if you don't have it:

   ```bash
   pip install --user pipenv
   ```

2. Install dependencies and create the virtualenv:

   ```bash
   pipenv install
   ```

3. Copy `.env.example` to `.env` and set your QARNOT_TOKEN there, or export
   the variable in your shell:

   ```bash
   export QARNOT_TOKEN="your-token-here"
   ```

4. (Optional) Set your SSH public key in the environment for SSH access to the
   running task:

   ```bash
   export SSH_PUBLIC_KEY="your-ssh-public-key-here"
   ```

## Usage

Run the script inside the pipenv environment:

```bash
pipenv run python task.py
```

You can also just run it yourself using ssh if you set the SSH_PUBLIC_KEY environment variable.
Note that this replaces the normal meshroom_batch command with an ssh server inside the container.
You will have to run meshroom_batch manually after connecting.
Add the --ssh flag to the script execution:

```bash
pipenv run python task.py --ssh
```
