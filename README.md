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

Enter the pipenv virtual environment:

```bash
pipenv shell
```

Run the script to start a meshroom_batch task:
This will use the images in the `in` folder, run a standard photogrammetry pipeline, and output the result to the `out` folder.

```bash
python task.py
```

You can also just run it yourself using ssh if you set the SSH_PUBLIC_KEY environment variable.
Note that this replaces the normal meshroom_batch command with an ssh server inside the container.
You will have to run meshroom_batch manually after connecting.
Add the --ssh flag to the script execution:

```bash
python task.py --ssh
```

You can list available hardware constraints with the --list-constraints flag:

```bash
python task.py --list-constraints
```

This will output something like:

```js
{'discriminator': 'MinimumRamHardwareConstraint', 'minimumMemoryMB': 32000.0}
{'discriminator': 'MinimumRamHardwareConstraint', 'minimumMemoryMB': 128000.0}
{'discriminator': 'SpecificHardwareConstraint', 'specificationKey': '8c-32g-amd-rz3700x'}
{'discriminator': 'SpecificHardwareConstraint', 'specificationKey': '16c-128g-amd-tr2950x-ssd'}
{'discriminator': 'SpecificHardwareConstraint', 'specificationKey': '28c-128g-intel-dual-xeon2680v4-ssd'}
{'discriminator': 'MinimumCoreHardwareConstraint', 'coreCount': 8}
{'discriminator': 'MinimumCoreHardwareConstraint', 'coreCount': 16}
{'discriminator': 'SSDHardwareConstraint'}
{'discriminator': 'MinimumCoreHardwareConstraint', 'coreCount': 28}
```
