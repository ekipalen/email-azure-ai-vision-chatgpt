from robocorp.tasks import task
from robocorp import workitems, vault
from RPA.Cloud.Azure import Azure 
from RPA.Email.Exchange import Exchange
import openai
import os

vision_library = Azure()
DATA_FOLDER = "output/data"
SYSTEM_PROMPT = "Your are an assistant helping to determine whether a surveillance camera images contains suspicious objects."
USER_PROMPT = """Reply with 'Yes' or 'No'. Yes if it is something that might be suspicious, like person, 
car or other vehicle. Single animal or mammal is not suspicious unless there is also a person in the image. \n
Surveillance camera image contained the following object(s): """
SUBJECT = "Suspicious action happening on your yard!"
BODY = "Please see the suspicious image(s)."

@task
def surveillance_camera_ai():
    do_the_initial_setup()
    images_to_send = read_email_and_return_objects()
    if images_to_send:
        send_email(images_to_send)

def read_email_and_return_objects():
    item = workitems.inputs.current
    try:
        paths = item.get_files("*.jpg", DATA_FOLDER)
    except Exception as e:
        print("Problem reading email:", str(e))
        return

    if not paths:
        print("No files, exiting")
        return
    
    images_to_send = []
    for path in paths: 
        detected_objects = ''
        vision_result = vision_library.vision_detect_objects(path)
        for object in vision_result['objects']:
            detected_objects += (object['object']) + ','
        result = analyze_objects_with_chatgpt(detected_objects)
        result = result.replace(".","")
        if result == 'Yes':
            images_to_send.append(str(path))
    return images_to_send

def analyze_objects_with_chatgpt(detected_objects):
    chatgpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT + detected_objects}
        ]
    )
    chatgpt_response = chatgpt_response['choices'][0]['message']['content']
    return chatgpt_response

def send_email(images_to_send):
    vault_name = "email_oauth_microsoft"
    email_credentials = vault.get_secret(vault_name)
    mail = Exchange(
        vault_name=vault_name,
        vault_token_key='token',
        tenant=email_credentials['tenant']
    )
    mail.authorize(
        username=email_credentials['username'],
        autodiscover=True,
        is_oauth=True,
        client_id=email_credentials["client_id"],
        client_secret=email_credentials["client_secret"],
        token=email_credentials["token"]
    )
    mail.send_message(
        recipients=email_credentials['username'],
        subject= SUBJECT,
        body=BODY,
        attachments=images_to_send
    )

def do_the_initial_setup():
    vision_library.set_robocorp_vault(vault_name="AzureVision")
    vision_library.init_computer_vision_service(region="eastus",use_robocorp_vault=True)
    openai_credentials = vault.get_secret("OpenAI")
    os.environ["OPENAI_API_KEY"] = openai_credentials["key"]
    openai.api_key = openai_credentials["key"]