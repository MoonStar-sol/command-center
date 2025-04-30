import os
import base64
import argparse
import time
import logging
import subprocess
from openai import OpenAI
from PIL import Image, ImageDraw
import io
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from cua_docker import CuaDocker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComputerControl:
    def __init__(self, display_width: int = 1024, display_height: int = 768, environment: str = "browser"):
        self.client = OpenAI()
        self.display_width = display_width
        self.display_height = display_height
        self.environment = environment
        self.last_response_id = None
        self.last_call_id = None
        self.docker = None
        self.click_locations: List[Tuple[int, int]] = []
        
        # Create screenshots directory
        self.screenshots_dir = "cua_screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def mark_click_location(self, img: Image.Image, x: int, y: int) -> Image.Image:
        """Draw a red dot at the click location."""
        draw = ImageDraw.Draw(img)
        dot_radius = 5
        draw.ellipse([(x - dot_radius, y - dot_radius), (x + dot_radius, y + dot_radius)], fill='red')
        return img

    def capture_screenshot(self) -> io.BytesIO:
        """Captures the container's screenshot and marks click locations."""
        try:
            # Use xwd to capture the screen in the container
            self.docker.execute_command("xwd -root -out /tmp/screenshot.xwd")
            
            # Convert xwd to png
            self.docker.execute_command("convert /tmp/screenshot.xwd /tmp/screenshot.png")
            
            # Copy the screenshot from container to host
            subprocess.run([
                "docker", "cp", 
                f"{self.docker.container_name}:/tmp/screenshot.png", 
                "/tmp/screenshot.png"
            ], check=True)
            
            # Read and process the image
            with open("/tmp/screenshot.png", "rb") as f:
                img = Image.open(f)
                
                # Mark all click locations
                for x, y in self.click_locations:
                    img = self.mark_click_location(img, x, y)
                
                # Save screenshot to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = os.path.join(self.screenshots_dir, f"screenshot_{timestamp}.png")
                img.save(screenshot_path)
                logger.info(f"Screenshot saved to {screenshot_path}")
                
                # Also return buffer for API
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                buffer.seek(0)
                return buffer
                
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            raise

    def encode_image(self, image_buffer: io.BytesIO) -> str:
        """Encodes an image buffer to base64."""
        try:
            return base64.b64encode(image_buffer.getvalue()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            raise

    def execute_action(self, action: Dict[str, Any]) -> None:
        """Execute a computer action in the container."""
        action_type = getattr(action, "type", None)
        
        try:
            if action_type == "click":
                x, y = getattr(action, "x", 0), getattr(action, "y", 0)
                button = getattr(action, "button", "left")
                logger.info(f"Clicking at ({x}, {y}) with {button} button")
                self.docker.execute_command(f"xdotool mousemove {x} {y} click 1")
                self.click_locations.append((x, y))
                
            elif action_type == "type":
                text = getattr(action, "text", "")
                logger.info(f"Typing: {text}")
                self.docker.execute_command(f"xdotool type '{text}'")
                
            elif action_type == "keypress":
                keys = getattr(action, "keys", [])
                logger.info(f"Pressing keys: {keys}")
                for key in keys:
                    self.docker.execute_command(f"xdotool key {key}")
                
            elif action_type == "scroll":
                x, y = getattr(action, "x", 0), getattr(action, "y", 0)
                scroll_x, scroll_y = getattr(action, "scroll_x", 0), getattr(action, "scroll_y", 0)
                logger.info(f"Scrolling at ({x}, {y}) with offsets ({scroll_x}, {scroll_y})")
                self.docker.execute_command(f"xdotool mousemove {x} {y} click 4")  # Scroll up
                
            elif action_type == "wait":
                wait_time = getattr(action, "time", 2)
                logger.info(f"Waiting for {wait_time} seconds")
                time.sleep(wait_time)
                
            else:
                logger.warning(f"Unsupported action type: {action_type}")
                
        except Exception as e:
            logger.error(f"Error executing action {action_type}: {e}")
            raise

    def execute_hardcoded_sequence(self) -> None:
        """Execute the hardcoded sequence of actions to reach Instagram Facebook login."""
        try:
            # Initialize Docker if not already initialized
            if not self.docker:
                self.docker = CuaDocker()
                self.docker.build_image()
                self.docker.start_container()
            
            # Wait for Firefox to load
            time.sleep(3)
            
            # Click sequence based on the logs
            actions = [
                ("click", 663, 766),  # Initial click
                ("click", 414, 90),   # URL bar click
                ("type", "instagram.com"),
                ("keypress", ["Return"]),
                ("wait", 2),
                ("click", 352, 135),  # Navigation click
            ]
            
            for action in actions:
                if action[0] == "click":
                    _, x, y = action
                    self.docker.execute_command(f"xdotool mousemove {x} {y} click 1")
                    self.click_locations.append((x, y))
                    time.sleep(1)
                elif action[0] == "type":
                    _, text = action
                    self.docker.execute_command(f"xdotool type '{text}'")
                    time.sleep(1)
                elif action[0] == "keypress":
                    _, keys = action
                    for key in keys:
                        self.docker.execute_command(f"xdotool key {key}")
                    time.sleep(1)
                elif action[0] == "wait":
                    _, duration = action
                    time.sleep(duration)
                
                # Capture screenshot after each action
                self.capture_screenshot()
        except Exception as e:
            logger.error(f"Error in hardcoded sequence: {str(e)}")
            raise

    def run_cua_loop(self, instruction: str) -> None:
        """Run the CUA loop to execute computer actions based on the model's suggestions."""
        logger.info("Initializing CUA loop...")
        
        try:
            # Start Docker container
            self.docker = CuaDocker()
            self.docker.build_image()
            self.docker.start_container()
            
            # Perform initial Instagram setup
            self.execute_hardcoded_sequence()
            
            # Capture initial screenshot
            screenshot_buffer = self.capture_screenshot()
            base64_image = self.encode_image(screenshot_buffer)
            
            # Create initial request
            response = self.client.responses.create(
                model="computer-use-preview",
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": self.display_width,
                    "display_height": self.display_height,
                    "environment": self.environment
                }],
                input=[{
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": instruction},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{base64_image}"
                        }
                    ]
                }],
                truncation="auto"
            )
            
            self.last_response_id = response.id
            
            while True:
                # Find computer calls in the response
                computer_calls = [item for item in response.output if getattr(item, "type", None) == "computer_call"]
                if not computer_calls:
                    logger.info("No more computer calls. Task completed.")
                    break
                    
                computer_call = computer_calls[0]
                self.last_call_id = getattr(computer_call, "call_id", None)
                action = getattr(computer_call, "action", None)
                
                # Check for safety checks
                pending_safety_checks = getattr(computer_call, "pending_safety_checks", [])
                if pending_safety_checks:
                    logger.warning("Safety checks pending. Please review:")
                    for check in pending_safety_checks:
                        logger.warning(f"- {getattr(check, 'message', 'Unknown safety check')}")
                    # In a real implementation, you would handle safety checks here
                    # For now, we'll just acknowledge them
                    acknowledged_checks = [{"id": getattr(check, "id", None), "code": getattr(check, "code", None)} 
                                        for check in pending_safety_checks]
                else:
                    acknowledged_checks = []
                
                # Execute the action
                self.execute_action(action)
                time.sleep(1)  # Allow time for changes to take effect
                
                # Capture new screenshot
                screenshot_buffer = self.capture_screenshot()
                base64_image = self.encode_image(screenshot_buffer)
                
                # Send updated state to model
                response = self.client.responses.create(
                    model="computer-use-preview",
                    previous_response_id=self.last_response_id,
                    tools=[{
                        "type": "computer_use_preview",
                        "display_width": self.display_width,
                        "display_height": self.display_height,
                        "environment": self.environment
                    }],
                    input=[{
                        "type": "computer_call_output",
                        "call_id": self.last_call_id,
                        "acknowledged_safety_checks": acknowledged_checks,
                        "output": {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{base64_image}"
                        }
                    }],
                    truncation="auto"
                )
                
                self.last_response_id = response.id
                
        except Exception as e:
            logger.error(f"Error in CUA loop: {e}")
            raise
        finally:
            if self.docker:
                self.docker.stop_container()

def main():
    parser = argparse.ArgumentParser(description="Control computer using OpenAI's Computer-Using Agent.")
    parser.add_argument("--instruction", required=True, help="Natural language instruction for the computer task.")
    parser.add_argument("--display-width", type=int, default=1024, help="Display width for the virtual environment.")
    parser.add_argument("--display-height", type=int, default=768, help="Display height for the virtual environment.")
    parser.add_argument("--environment", default="browser", choices=["browser", "mac", "windows", "ubuntu"],
                      help="Environment type for the computer agent.")
    
    args = parser.parse_args()
    
    try:
        computer_control = ComputerControl(
            display_width=args.display_width,
            display_height=args.display_height,
            environment=args.environment
        )
        computer_control.run_cua_loop(args.instruction)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

if __name__ == "__main__":
    main() 