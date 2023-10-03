# Suspicious Images example - Robocorp, Azure AI Vision, ChatGPT

This example leverages the new Python open-source structure [robo](https://github.com/robocorp/robo).

The full power of [rpaframework](https://github.com/robocorp/rpaframework) is also available for you on Python as a backup while we implement new Python libraries.

## Description
This example operates as follows:

1. **Email Trigger:** Activated by an email sent to the Robocorp Control Room.

2. **Processing the inputs:** Read the attached surveillance camera images.

3. **Azure AI Vision:** Utilizes Azure AI Vision to detect objects in the images.

4. **ChatGPT Analysis:** Engages ChatGPT to determine suspicious content in the images.

5. **Suspicion Alert:** Sends an email with suspicious images attached for further action.

