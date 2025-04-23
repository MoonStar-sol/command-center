# Vision

To build a system that automates professional workflows, explores potential automated income streams, and documents the entire process via live streaming. The core idea is to leverage AI pair programming (with me, the AI assistant in this repository) to iteratively develop and manage this system, guided by a simple "please continue" command from the user.

# Current State

*   **Email Client (`email_client.py`):** A script to fetch, display, summarize (using OpenAI), and respond to emails. It accepts various command-line arguments:
    *   `--check`: Display unread emails.
    *   `--recent`: Read the most recent email and its thread.
    *   `--summarize`: Summarize unread emails via OpenAI.
    *   `--respond --body <response_body>`: Respond to the oldest unread email with the provided body.
    *   `--send --recipient <email> --subject <subject> --body <body>`: Send a new email.
*   **AI Voice Assistant (`ai_voice.py`):** A script that monitors the clipboard and uses OpenAI's TTS API to convert copied text to speech, making the live stream more engaging by vocalizing AI responses.
*   **Video Processing (`crop_video.py`):** A script that processes videos for social media by:
    *   Cropping to keep only the right third of the video
    *   Formatting to 9:16 aspect ratio (1080x1920)
    *   Automatically handling both cropping and padding as needed
    *   Supporting various input video formats
*   **Consulting Website (`hansmith.com`):** A website with an AI booking agent chat widget is live, aimed at generating consulting and education leads for "Exponential Integration". Emails from the booking agent are the current input for the `email_client.py`.
*   **Automated Trading Agent:** An external system exists related to AI and crypto trading (part of another business). Not directly integrated here yet.
*   **Live Streaming:** The development process is being streamed to YouTube, but currently has low viewership. We're implementing improvements like the AI Voice Assistant to make it more engaging.

# Available Tools

*   `email_client.py`:
    *   `--check`: Display unread emails.
    *   `--recent`: Read the most recent email and its thread.
    *   `--summarize`: Summarize unread emails via OpenAI.
    *   `--respond --body <response_body>`: Respond to the oldest unread email with the provided body.
    *   `--send --recipient <email> --subject <subject> --body <body>`: Send a new email.
*   `ai_voice.py`:
    *   Monitors clipboard for changes.
    *   Uses OpenAI's TTS API to convert text to speech.
    *   Automatically plays audio when text is copied to clipboard.
    *   Configurable voice options.
*   `crop_video.py`:
    *   Processes videos for social media platforms
    *   Automatically crops to right third and formats to 9:16 aspect ratio
    *   Resizes to 1080x1920 dimensions
    *   Handles both cropping and padding as needed
    *   Supports various input video formats

# Current Focus / Next Steps

1. **Test the AI Voice Assistant:** Test the newly created `ai_voice.py` script during live streams to ensure it properly converts AI responses to speech.

2. **Continue Brainstorming New Directions:** Given the current situation (low streaming viewership and feeling stuck), we need to reconsider our approach and priorities:
   - Define clearer objectives for the Command Center system
   - Identify additional ways to make the live streaming aspect more engaging
   - Explore new potential income streams or automation opportunities
   - Consider how to better integrate existing components (email client, consulting website, trading agent)

3. **Develop a Concrete Workflow:** Once we have a clearer direction, establish a concrete workflow that defines:
   - How leads from the website are processed
   - What automated responses look like
   - How to categorize and prioritize different types of incoming messages
   - What metrics to track to measure success

4. **Plan Integration Points:** Determine how the email client, trading system, and other future components will communicate and work together.

# Meta-Prompt (Instructions for AI)

When the user prompts with "please continue" or a similar instruction to proceed:

1.  **Read:** Carefully read this entire `process.md` file.
2.  **Identify:** Determine the next logical action based on the `Current Focus / Next Steps` section.
3.  **Plan:** Outline the steps needed to accomplish the identified action. This might involve running existing tools, modifying code, creating new files, or researching solutions.
4.  **Execute:** Propose the necessary tool calls (`run_terminal_cmd`, `edit_file`, `web_search`, etc.) to carry out the plan. Wait for user confirmation or feedback if necessary, especially for complex changes.
5.  **Verify:** Check if the execution was successful (e.g., command output, successful code edits, tests pass if available).
6.  **Update:** Modify the `Current State` and `Current Focus / Next Steps` sections of *this file* (`process.md`) to reflect the completed work and determine the *new* next step. Commit this update.
7.  **Report:** Briefly inform the user of the actions taken and the updated status. 