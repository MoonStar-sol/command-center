import os
import argparse
import logging
from typing import Optional
from cua_docker import CuaDocker
from computer_control import ComputerControl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InstagramCUA:
    def __init__(self):
        self.docker = None
        self.computer_control = None

    def run_with_instruction(self, instruction: str, use_hardcoded: bool = True) -> None:
        """Run the CUA agent with the given instruction."""
        try:
            logger.info("Initializing Docker container...")
            self.docker = CuaDocker()
            self.docker.build_image()
            self.docker.start_container()
            
            logger.info("Initializing ComputerControl...")
            self.computer_control = ComputerControl()
            
            if use_hardcoded:
                logger.info("Executing hardcoded sequence...")
                self.computer_control.execute_hardcoded_sequence()
            
            logger.info("Starting CUA loop with instruction...")
            self.computer_control.run_cua_loop(instruction)
            
        except Exception as e:
            logger.error(f"Error during execution: {str(e)}")
            raise
        finally:
            if self.docker:
                logger.info("Cleaning up Docker container...")
                self.docker.stop_container()

def main():
    parser = argparse.ArgumentParser(description="Run CUA agent")
    parser.add_argument("--instruction", required=True, help="The instruction for the CUA agent to execute")
    parser.add_argument("--no-hardcoded", action="store_true", help="Skip hardcoded sequence and use CUA directly")
    
    args = parser.parse_args()
    
    instagram_cua = InstagramCUA()
    instagram_cua.run_with_instruction(args.instruction, not args.no_hardcoded)

if __name__ == "__main__":
    main() 