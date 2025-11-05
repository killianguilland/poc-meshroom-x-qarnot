import os
import sys
import qarnot
from datetime import datetime
import argparse
from dotenv import load_dotenv

"""Create and run a qarnot docker-batch task using a token from the
environment. This avoids committing secrets to source control.

Set QARNOT_TOKEN in your environment (or use a local `.env` file when
developing).
"""

# TOKEN GLOBAL SETUP
load_dotenv()
	
token = os.environ.get("QARNOT_TOKEN")

if not token:
	print("ERROR: environment variable QARNOT_TOKEN is not set.", file=sys.stderr)
	print("Export QARNOT_TOKEN or create a .env file with QARNOT_TOKEN=value before running.", file=sys.stderr)
	sys.exit(2)


def list_constraints():
	conn = qarnot.connection.Connection(client_token=token)
	for hwc in conn.all_hardware_constraints():
		print(hwc.to_json())
	return


def setup_buckets(conn):
	try:
		input_bucket = conn.retrieve_bucket("meshroom-in")
		print("Found input bucket.")
	except qarnot.exceptions.BucketStorageUnavailableException as e:
		input_bucket = conn.create_bucket("meshroom-in")
		print("Created input bucket.")
	
	try:
		output_bucket = conn.retrieve_bucket("meshroom-out")
		print("Found output bucket.")
	except qarnot.exceptions.BucketStorageUnavailableException as e:
		output_bucket = conn.create_bucket("meshroom-out")
		print("Created output bucket.")
	
	return input_bucket, output_bucket


def sync_folder(folder_path):
	conn = qarnot.connection.Connection(client_token=token)
	input_bucket, output_bucket = setup_buckets(conn)

	if(folder_path == "in"):
		print("Syncing local 'in' folder to input bucket 'meshroom-in'...")
		input_bucket.sync_directory(folder_path)
		print("Sync complete.")
	elif(folder_path == "out"):
		print("Syncing output bucket 'meshroom-out' to local 'out' folder...")
		output_bucket.sync_remote_to_local("out")
		print("Sync complete.")


def run_ssh_task():
	# TASK SETUP
	conn = qarnot.connection.Connection(client_token=token)

	profile = "docker-network-ssh"
	task = conn.create_task("meshroom-test", profile, 1)

	DOCKER_SSH = os.environ.get("SSH_PUBLIC_KEY")

	task.constants["DOCKER_REPO"] = os.environ.get("MESHROOM_DOCKER_REPO")
	task.constants["DOCKER_TAG"] = os.environ.get("MESHROOM_DOCKER_TAG")
	task.constants['DOCKER_CMD'] = "/bin/bash -c 'mkdir -p ~/.ssh /run/sshd ;" \
							"echo \"${DOCKER_SSH}\" >> ~/.ssh/authorized_keys ;" \
							"/usr/sbin/sshd -D'"
	task.constants['DOCKER_SSH'] = DOCKER_SSH

	# BUCKET CONNECTION
	input_bucket, output_bucket = setup_buckets(conn)
	task.resources.append(input_bucket)
	task.results = output_bucket

	# TASK START
	task.submit()

	# MONITORING LOOP
	done = False

	while not done:

		if task.state == 'FullyExecuting':
			# SSH STARTUP (OPTIONAL)
			forward_list = task.status.running_instances_info.per_running_instance_info[0].active_forward
			if len(forward_list) != 0:
				ssh_forward_port = forward_list[0].forwarder_port
				ssh_forward_host = forward_list[0].forwarder_host
				print("SSH is available ! Connect using this command :")
				print(f"ssh -o StrictHostKeyChecking=no root@{ssh_forward_host} -p {ssh_forward_port}")
				done = True

		# Display errors on failure
		if task.state == 'Failure':
			print("** Errors: %s" % task.errors[0])
			done = True

		done = task.wait(10)


def run_meshroom_task(subfolder_name):

	if not subfolder_name:
		print("Please provide a subfolder name containing input data for the photogrammetry task. It should be located directly within the 'in' folder.", file=sys.stderr)
		return
	
	print(f"Starting photogrammetry task for subfolder: {subfolder_name}")

	# TASK SETUP
	conn = qarnot.connection.Connection(client_token=token)

	profile = "docker-nvidia-batch"
	task = conn.create_task("meshroom-test", profile, 1)
	task.constants["DOCKER_REPO"] = "alicevision/meshroom" #os.environ.get("MESHROOM_DOCKER_REPO")
	task.constants["DOCKER_TAG"] = "2025.1.0-av3.3.0-ubuntu22.04-cuda12.1.1" #os.environ.get("MESHROOM_DOCKER_TAG")
	task.constants['DOCKER_CMD'] = f"/opt/Meshroom_bundle/meshroom_batch --input /job/{subfolder_name} --output /job/output"

	# BUCKET CONNECTION

	input_bucket, output_bucket = setup_buckets(conn)
	task.resources.append(input_bucket)
	task.results = output_bucket

	# TASK START
	task.submit()

	# MONITORING LOOP
	last_state = ''
	done = False

	while not done:

		# OUTPUT HANDLING
		_latest_out = task.fresh_stdout()
		if _latest_out:
			for line in _latest_out.replace("\\n", "\n").splitlines():
				print(line)

		_latest_err = task.fresh_stderr()
		if _latest_err:
			for line in _latest_err.replace("\\n", "\n").splitlines():
				print(line, file=sys.stderr)

		if task.state != last_state:
			last_state = task.state
			print("=" * 10)
			print("-- {}".format(last_state))

		if task.state == 'FullyExecuting':
			instance_info = task.status.running_instances_info.per_running_instance_info[0]
			cpu = instance_info.cpu_usage
			memory = instance_info.current_memory_mb
			print("-- ", datetime.now(), "| {:.2f} % CPU | {:.2f} MB MEMORY".format(cpu, memory))

		# Display errors on failure
		if task.state == 'Failure':
			print("-- Errors: %s" % task.errors[0])
			done = True

		done = task.wait(10)

		if task.state == 'Success':
			print("-- Task completed successfully.")
			sync_folder("out")
			print("Output synchronized to local 'out' folder.")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Run qarnot meshroom task")

	parser.add_argument(
		"--ssh",
		action="store_true",
		help="If included, open an SSH connection to the running task when available",
	)

	parser.add_argument(
		"--list-constraints",
		action="store_true",
		help="If included, list all available hardware constraints",
	)

	parser.add_argument(
		"--sync-folder",
		metavar="PATH",
		type=str,
		help="If included, sync the specified folder ('in' or 'out') with the corresponding bucket",
	)
	parser.add_argument(
		"--meshroom-task",
		metavar="PATH",
		type=str,
		help="Starts the photogrammetry task (turns the pictures from the /in folder into a 3D model in the /out folder). Provide the subfolder name within the /in folder containing the input data.",
	)
	args = parser.parse_args()

	if(args.list_constraints):
		list_constraints()
	elif(args.ssh):
		run_ssh_task()
	elif(args.sync_folder):
		sync_folder(args.sync_folder)
	elif(args.meshroom_task):
		run_meshroom_task(args.meshroom_task)
	else:
		print("No action specified. Use --help for usage information.")