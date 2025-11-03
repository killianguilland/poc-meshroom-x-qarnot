# meshroom-poc

Small proof-of-concept showing how to create a qarnot docker-batch task.

Setup with pipenv:

1. Install pipenv if you don't have it:

   pip install --user pipenv

2. Install dependencies and create the virtualenv:

   pipenv install

3. Copy `.env.example` to `.env` and set your QARNOT_TOKEN there, or export
   the variable in your shell:

   export QARNOT_TOKEN="your-token-here"

4. Run the script inside the pipenv environment:

   pipenv run python task.py

Security note: never commit real tokens to source control. Keep secrets in
environment variables or a local `.env` that's listed in `.gitignore`.
