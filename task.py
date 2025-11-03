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

def main(open_ssh=False, list_available_constraints=False):
	load_dotenv()
	
	token = os.environ.get("QARNOT_TOKEN")

	if not token:
		print("ERROR: environment variable QARNOT_TOKEN is not set.", file=sys.stderr)
		print("Export QARNOT_TOKEN or create a .env file with QARNOT_TOKEN=value before running.", file=sys.stderr)
		sys.exit(2)

	# CONNECTION SETUP

	conn = qarnot.connection.Connection(client_token=token)
	if list_available_constraints:
		for hwc in conn.all_hardware_constraints():
			print(hwc.to_json())
		return

	# TASK SETUP 
	profile = "docker-network-ssh" if open_ssh else "docker-batch"
	task = conn.create_task("meshroom-test", profile, 1)

	try:
		input_bucket = conn.retrieve_bucket("meshroom-in")
		print("Found input bucket.")
	except qarnot.exceptions.BucketStorageUnavailableException as e:
		input_bucket = conn.create_bucket("meshroom-in")
		print("Created input bucket.")

	task.resources.append(input_bucket)

	task.results = output_bucket

	DOCKER_SSH = os.environ.get("SSH_PUBLIC_KEY")

	task.constants["DOCKER_REPO"] = "alicevision/meshroom"
	task.constants["DOCKER_TAG"] = "2025.1.0-av3.3.0-ubuntu22.04-cuda12.1.1"
	if open_ssh:
		task.constants['DOCKER_CMD'] = "/bin/bash -c 'mkdir -p ~/.ssh /run/sshd ;" \
								"echo \"${DOCKER_SSH}\" >> ~/.ssh/authorized_keys ;" \
								"/usr/sbin/sshd -D'"
		task.constants['DOCKER_SSH'] = DOCKER_SSH
	else:
		task.constants['DOCKER_CMD'] = "/usr/local/bin/meshroom_batch --input /full --output /output"

	# BUCKET CONNECTION
	try:
		output_bucket = conn.retrieve_bucket("meshroom-out")
		print("Found output bucket.")
	except qarnot.exceptions.BucketStorageUnavailableException as e:
		output_bucket = conn.create_bucket("meshroom-out")
		print("Created output bucket.")

	# TASK START
	task.submit()

	# MONITORING LOOP
	last_state = ''
	done = False
	ssh_has_started = False

	while not done:

		# OUTPUT HANDLING
		_latest_out = task.fresh_stdout()
		if _latest_out:
			print(_latest_out)
		
		_latest_err = task.fresh_stderr()
		if _latest_err:
			print(_latest_err, file=sys.stderr)
		
		if task.state != last_state:
			last_state = task.state
			print("** {}".format(last_state))

		if task.state == 'FullyExecuting':
			instance_info = task.status.running_instances_info.per_running_instance_info[0]
			cpu = instance_info.cpu_usage
			memory = instance_info.current_memory_mb
			print("\n*******************************\n")
			print('Current Timestamp : ', datetime.now())
			print("Current CPU usage : {:.2f} %".format(cpu))
			print("Current memory usage : {:.2f} MB".format(memory))

			# SSH STARTUP (OPTIONAL)
			forward_list = task.status.running_instances_info.per_running_instance_info[0].active_forward
			if open_ssh and not ssh_has_started and len(forward_list) != 0:
				ssh_forward_port = forward_list[0].forwarder_port
				ssh_forward_host = forward_list[0].forwarder_host
				print("SSH is available ! Connect using this command :")
				cmd = f"ssh -o StrictHostKeyChecking=no root@{ssh_forward_host} -p {ssh_forward_port}"
				print(cmd)
				ssh_has_started = True

		# Display errors on failure
		if task.state == 'Failure':
			print("** Errors: %s" % task.errors[0])
			done = True

		done = task.wait(10)


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
	args = parser.parse_args()

	main(list_available_constraints=args.list_constraints, open_ssh=args.ssh)