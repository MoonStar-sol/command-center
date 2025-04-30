import subprocess
import time
import os
from typing import Optional

class CuaDocker:
    def __init__(self, container_name: str = "cua-container"):
        self.container_name = container_name
        self.container_id = None

    def _check_container_exists(self) -> bool:
        """Check if the container exists and is running."""
        try:
            # Check if container exists and is running
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.Status}}"],
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                # Container exists, check if it's running
                status = result.stdout.strip().lower()
                if "up" in status:
                    # Get the container ID
                    id_result = subprocess.run(
                        ["docker", "ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.ID}}"],
                        capture_output=True,
                        text=True
                    )
                    self.container_id = id_result.stdout.strip()
                    return True
                else:
                    # Container exists but is stopped, remove it
                    subprocess.run(["docker", "rm", self.container_name], check=True)
            return False
        except subprocess.CalledProcessError:
            return False

    def build_image(self) -> None:
        """Build the Docker image."""
        print("Building Docker image...")
        subprocess.run(["docker", "build", "-t", "cua-image", "."], check=True)
        print("Docker image built successfully.")

    def start_container(self) -> None:
        """Start the Docker container."""
        # Check if container already exists and is running
        if self._check_container_exists():
            print(f"Using existing container: {self.container_name}")
            return

        print("Starting Docker container...")
        cmd = [
            "docker", "run", "--rm", "-d",
            "--name", self.container_name,
            "-p", "5900:5900",
            "-e", "DISPLAY=:99",
            "cua-image"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.container_id = result.stdout.strip()
        print(f"Container started with ID: {self.container_id}")
        
        # Wait for container to be ready
        time.sleep(5)
        print("Container is ready. You can connect using a VNC client at localhost:5900")
        print("VNC password: secret")

    def stop_container(self) -> None:
        """Stop the Docker container."""
        if self.container_id:
            print("Stopping container...")
            subprocess.run(["docker", "stop", self.container_name], check=True)
            self.container_id = None
            print("Container stopped.")

    def execute_command(self, command: str) -> str:
        """Execute a command in the container."""
        if not self.container_id:
            raise RuntimeError("Container is not running")
        
        safe_cmd = command.replace('"', '\\"')
        docker_cmd = f'docker exec {self.container_name} sh -c "{safe_cmd}"'
        result = subprocess.run(docker_cmd, shell=True, capture_output=True, text=True)
        return result.stdout

    def __enter__(self):
        """Context manager entry."""
        self.build_image()
        self.start_container()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_container()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Manage CUA Docker container")
    parser.add_argument("--command", help="Command to execute in the container")
    args = parser.parse_args()

    with CuaDocker() as cua:
        if args.command:
            print("Executing command:", args.command)
            result = cua.execute_command(args.command)
            print("Result:", result)
        else:
            print("Container is running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping container...")

if __name__ == "__main__":
    main() 