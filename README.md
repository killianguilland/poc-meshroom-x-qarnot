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

Available actions (mutually exclusive; only one action is performed per run):

- Start the photogrammetry task:
   Process a subfolder inside `/in` and write results to `/out`:

   ```bash
   python poc.py --meshroom-task SUBFOLDER_NAME
   ```

   Example: process images in `/in/my_scan`:

   ```bash
   python poc.py --meshroom-task my_scan
   ```

- Open an SSH connection to the running task:
   If you set SSH_PUBLIC_KEY, this opens an SSH session into the container so you can run meshroom_batch manually:

   ```bash
   python poc.py --ssh
   ```

- Sync a local folder with the corresponding bucket:
   Sync either the `in` or `out` folder with the remote bucket:

   ```bash
   python poc.py --sync-folder in
   python poc.py --sync-folder out
   ```

- List available hardware constraints:

   ```bash
   python poc.py --list-constraints
   ```
   
   Example output for --list-constraints might look like:

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

If you run the script without any of the above flags it will print "No action specified. Use --help for usage information."