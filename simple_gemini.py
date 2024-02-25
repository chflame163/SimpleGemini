import os
import sys
import time
import datetime
import json
import requests
import google.generativeai as genai
import gradio as gr
from typing import List, Tuple, Optional
from PIL import Image

chat_component_height = 360
logs = []
chat_index = 0
previous_image = None
current_path = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.join(os.path.expanduser("~"), ".simplegemini", "log", str(datetime.date.today()))
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, f"{datetime.datetime.now().strftime('%Y%m%d')}-{time.time()}.log")

def log(info:str, image:Image=None, save_log:bool=True, start_with_time:bool=True):
    if start_with_time:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        current_time = ""
    if save_log:
        if image is not None:
            jpg_file = f"{time.time()}.jpg"
            jpg_file = os.path.join(log_dir, jpg_file)
            jpg_file.replace('\\\\', '/')
            side_max_length = 512
            image_width, image_height = image.size
            target_width = image_width
            target_height = image_height
            if image_width > side_max_length or image_height > side_max_length:
                if image_width > image_height:
                    target_width = side_max_length
                    target_height = target_width * image_height / image_width
                else:
                    target_height = side_max_length
                    target_width = target_height * image_width / image_height
                image.thumbnail((target_width, target_height))
                image.save(jpg_file)
            line = f"{current_time}: {info}, image = {jpg_file}"
        else:
            line = f"{current_time}: {info}"
    else:
        line = f"{current_time}: This dialog not recorded because save_log is unchecked."
    logs.append(line)
    with open(log_file, mode='w', encoding='utf-8') as f:
        for i in logs:
            f.write(str(i) + '\n')

def validate_api_key(api_key:str) -> bool:
    url = "https://ai.google.dev"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return True
    else:
        return False

def get_api_key() -> str:
    apikey_json_path = os.path.join(current_path, 'apikey.json')
    try:
        with open(apikey_json_path, 'r') as f:
            config = json.load(f)
        api_key = config["GOOGLE_API_KEY"]
        if len(api_key) < 38:
            line = "API key incorrect, check the file apikey.json."
            log(line)
            print(line)
            sys.exit()
    except Exception as e:
        log(f"{e}, program exit.")
        print(e)
        print("API key load failed, check the file apikey.json.")
        sys.exit()
    if not validate_api_key(api_key):
        line = f"Error: Unable validate GOOGLE_API_KEY, check your network environment."
        log(line)
        print(line)
        sys.exit()
        return api_key
    else:
        log(f"Success load GOOGLE_API_KEY")
        return api_key

def hash_img(img):
    a = []
    hash_img = ''
    width, height = 32, 32
    img = img.resize((width, height))
    for y in range(img.height):
        b = []
        for x in range(img.width):
            pos = x, y
            color_array = img.getpixel(pos)
            color = sum(color_array) / 3
            b.append(int(color))
        a.append(b)
    for y in range(img.height):
        avg = sum(a[y]) / len(a[y])
        for x in range(img.width):
            if a[y][x] >= avg:
                hash_img += '1'
            else:
                hash_img += '0'
    return hash_img

# Calculate the similarity between two images, full same return 1.0, and full difference return 0
def image_similarity(image1, image2):
    hash1 = hash_img(image1)
    hash2 = hash_img(image2)
    difference = 0
    for i in range(len(hash1)):
        difference += abs(int(hash1[i]) - int(hash2[i]))
    similar = 1.0 - (difference / len(hash1))
    return similar

def preprocess_stop_sequences(stop_sequences: str) -> Optional[List[str]]:
    if not stop_sequences:
        return None
    return [sequence.strip() for sequence in stop_sequences.split(",")]

def user(text_prompt: str, chatbot: List[Tuple[str, str]]):
    return "", chatbot + [[text_prompt, None]]


TITLE = """<h1 align="center">Simple Gemini</h1>"""
SUBTITLE = """<h4 align="center">an AI chatbot with google Gemini API</h4>"""
AVATAR_IMAGES = (os.path.join(current_path, "images", "user.jpg"),
                 os.path.join(current_path, "images", "gemini.jpg"))
log(f"Starting Simple Gemini with google-generativeai {genai.__version__}")
GOOGLE_API_KEY = get_api_key()
def bot(image_prompt: Optional[Image.Image],
        chatbot: List[Tuple[str, str]],
        save_log:bool,
        temperature: float,
        max_output_tokens: int,
        stop_sequences: str,
        top_k: int,
        top_p: float,
        ):
    global previous_image
    global chat_index

    text_prompt = chatbot[-1][0]
    chat_index += 1
    log(f"================ Chat {chat_index} ================", start_with_time=False)
    genai.configure(api_key=GOOGLE_API_KEY, transport='rest')
    generation_config = genai.types.GenerationConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        stop_sequences=preprocess_stop_sequences(stop_sequences=stop_sequences),
        top_k=top_k,
        top_p=top_p)
    if image_prompt is None:
        log(f"prompt = {text_prompt}", save_log=save_log)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(text_prompt, generation_config=generation_config)
        log(f"response.text={response.text}", save_log=save_log)
        response.resolve()
    else:
        if previous_image:
            if image_similarity(image_prompt, previous_image) < 1:
                previous_image = image_prompt
                log(f"prompt = {text_prompt}", previous_image, save_log=save_log)
            else:
                log(f"prompt = {text_prompt}, image = previous image", save_log=save_log)
        else:
            previous_image = image_prompt
            log(f"prompt = {text_prompt}", previous_image, save_log=save_log)
        model = genai.GenerativeModel('gemini-pro-vision')
        response = model.generate_content([text_prompt, image_prompt], generation_config=generation_config)
        log(f"response.text={response.text}", save_log=save_log)
        response.resolve()

    # streaming effect
    chatbot[-1][1] = ""
    for chunk in response:
        for i in range(0, len(chunk.text), 10):
            section = chunk.text[i:i + 10]
            chatbot[-1][1] += section
            time.sleep(0.01)
            yield chatbot

image_prompt_component = gr.Image(
    type="pil",
    label="Image Prompt",
    scale=1,
    height=chat_component_height,
    image_mode='RGB',
    sources= "upload",
    interactive=True,
)
chatbot_component = gr.Chatbot(
    label='Chat with Gemini',
    bubble_full_width=False,
    avatar_images=AVATAR_IMAGES,
    scale=1,
    height=chat_component_height,
    show_copy_button=True,
)
text_prompt_component = gr.Textbox(
    placeholder="Input your question here ...",
    label="Text Prompt:",
    autofocus=True,
    show_copy_button=True,
)
run_button_component = gr.Button("Run", scale=9)
save_log_component = gr.Checkbox(value=True, label="Save to LOG", scale=1)
temperature_component = gr.Slider(
    minimum=0,
    maximum=1.0,
    value=0.4,
    step=0.05,
    label="Temperature",
    info=(
        "Temperature controls the degree of randomness in token selection. Lower "
        "temperatures are good for prompts that expect a true or correct response, "
        "while higher temperatures can lead to more diverse or unexpected results. "
    ))
max_output_tokens_component = gr.Slider(
    minimum=1,
    maximum=2048,
    value=1024,
    step=1,
    label="Token limit",
    info=(
        "Token limit determines the maximum amount of text output from one prompt. A "
        "token is approximately four characters. The default value is 2048."
    ))
stop_sequences_component = gr.Textbox(
    label="Add stop sequence",
    value="",
    type="text",
    placeholder="STOP, END",
    info=(
        "A stop sequence is a series of characters (including spaces) that stops "
        "response generation if the model encounters it. The sequence is not included "
        "as part of the response. You can add up to five stop sequences."
    ))
top_k_component = gr.Slider(
    minimum=1,
    maximum=40,
    value=32,
    step=1,
    label="Top-K",
    info=(
        "Top-k changes how the model selects tokens for output. A top-k of 1 means the "
        "selected token is the most probable among all tokens in the model’s "
        "vocabulary (also called greedy decoding), while a top-k of 3 means that the "
        "next token is selected from among the 3 most probable tokens (using "
        "temperature)."
    ))
top_p_component = gr.Slider(
    minimum=0,
    maximum=1,
    value=1,
    step=0.01,
    label="Top-P",
    info=(
        "Top-p changes how the model selects tokens for output. Tokens are selected "
        "from most probable to least until the sum of their probabilities equals the "
        "top-p value. For example, if tokens A, B, and C have a probability of .3, .2, "
        "and .1 and the top-p value is .5, then the model will select either A or B as "
        "the next token (using temperature). "
    ))

user_inputs = [
    text_prompt_component,
    chatbot_component
]

bot_inputs = [
    image_prompt_component,
    chatbot_component,
    save_log_component,
    temperature_component,
    max_output_tokens_component,
    stop_sequences_component,
    top_k_component,
    top_p_component,
]

with gr.Blocks() as demo:
    gr.HTML(TITLE)
    gr.HTML(SUBTITLE)
    with gr.Column():
        with gr.Row():
            image_prompt_component.render()
            chatbot_component.render()
        text_prompt_component.render()
        with gr.Row():
            run_button_component.render()
            save_log_component.render()
        with gr.Accordion("Parameters", open=False):
            temperature_component.render()
            max_output_tokens_component.render()
            stop_sequences_component.render()
            with gr.Accordion("Advanced", open=False):
                top_k_component.render()
                top_p_component.render()

    run_button_component.click(
        fn=user,
        inputs=user_inputs,
        outputs=[text_prompt_component, chatbot_component],
        queue=False
    ).then(
        fn=bot, inputs=bot_inputs, outputs=[chatbot_component],
    )

    text_prompt_component.submit(
        fn=user,
        inputs=user_inputs,
        outputs=[text_prompt_component, chatbot_component],
        queue=False
    ).then(
        fn=bot, inputs=bot_inputs, outputs=[chatbot_component],
    )

demo.queue(max_size=99).launch(debug=False, inbrowser=True)