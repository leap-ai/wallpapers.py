import requests
import json
import time
import os
from dotenv import load_dotenv

# Generate AI Wallpapers with Leap API
load_dotenv()
API_KEY = os.environ.get('LEAP_API_KEY')

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {API_KEY}"
}

batch = [
    "futuristic tree house, hyper realistic, epic composition, cinematic, landscape vista photography by Carr Clifton & Galen Rowell, Landscape veduta photo by Dustin Lefevre & tdraw, detailed landscape painting by Ivan Shishkin, rendered in Enscape, Miyazaki, Nausicaa Ghibli, 4k detailed post processing, unreal engine",
    "old European town, cobblestone streets, colorful buildings, cafe, charming atmosphere",
    "beautiful landscape sunset over the ocean, full of colors, 8k",
    "tropical rainforest, lush greenery, exotic wildlife, hidden waterfall, untouched wilderness"
]

def generate_image(model_id, prompt):
    url = f"https://api.tryleap.ai/api/v1/images/models/{model_id}/inferences"

    payload = {
        "prompt": prompt,  
        "steps": 50,
        "width": 800,
        "height": 360,
        "numberOfImages": 1,
        "promptStrength": 7,
        "upscaleBy": "x1",
        "negativePrompt": "",
        "sampler": "ddim",
        "restoreFaces": False,
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    data = json.loads(response.text)

    if "error" in data:
        print("Error: ", data)
        return None, None
    inference_id = data["id"]
    status = data["status"]

    print(f"Generating Inference: {inference_id}. Status: {status}")

    return inference_id, status


def get_inference_job(model_id, inference_id):
    url = f"https://api.tryleap.ai/api/v1/images/models/{model_id}/inferences/{inference_id}"

    response = requests.get(url, headers=HEADERS)
    data = json.loads(response.text)

    if "id" not in data:
        print("Error: ", data)
        return None, None, None

    inference_id = data["id"]
    state = data["state"]
    images = None

    if len(data["images"]):
        images = data["images"]

    print(f"Getting Inference: {inference_id}. State: {state}")

    return inference_id, state, images

# Realistic Vision (using as default): eab32df0-de26-4b83-a908-a83f3015e971
# Other models:
# Stable Diffusion 1.5: 8b1b897c-d66d-45a6-b8d7-8e32421d02cf
# Stable Diffusion 2.1: ee88d150-4259-4b77-9d0f-090abe29f650	
model_id = "eab32df0-de26-4b83-a908-a83f3015e971"
inference_ids = []

for i in range(len(batch)):
    prompt = batch[i]
    inference_id, status = generate_image(
        model_id, 
        prompt=prompt,
    )
    inference_ids.append(inference_id)

image_urls = []
while True:
    all_finished = True
    for i in range(len(inference_ids)):
        inference_id = inference_ids[i]
        if inference_id is None:
            continue
        status = ""
        inference_id, status, images = get_inference_job(model_id, inference_id)
        if status != "finished":
            all_finished = False
        else:
            for image in images:
                image_urls.append(image["uri"])
            inference_ids[i] = None
    if all_finished:
        break
    time.sleep(10)
    
for image_url in image_urls:
    print("Image ready:", image_url)



