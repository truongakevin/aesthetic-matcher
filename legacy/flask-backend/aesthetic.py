# hello everyone!  I'm working on a university project that uses AI to classify aesthetic styles. It's going to be an app or website that allows you to take or upload a picture that will then use an AI model to classify the aesthetic. I am currently working on building a dataset of labeled pictures by aesthetic to train the model, so if anyone has any websites or resources where I might be able to find aesthetics and images that match them that would be helpful. right now im working on scraping all the pictures from the aesthetics wiki website but any other resources would be much appreciated!
# hey everyone! ive been working on a website that matches images to aesthetics so you can upload an image and it will tell you what aesthetic it is. it uses a finetuned machine learning model trained on all images from the aesthetics wiki. i finally got it to a working state so i wanted to share it with yall! its still a work in progress so im open to suggestions and it is running on my local machine so it might be a bit slow and possibly buggy but the website is kevinatruong.com/aesthetic-matcher/
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import requests
import torch
import os

# import aesthetics
from listaesthetics import aesthetics

# List of aesthetics
aesthetics_list = aesthetics

# huggingface-cli download "kevinoli/clip-finetuned-csu-p14-336-e4l57-l" --include "checkpoint-28000/*" --local-dir ./models/

# Load pre-trained model and processor
# # model_name = "laion/CLIP-ViT-bigG-14-laion2B-39B-b160k"
# # model_name = "openai/clip-vit-large-patch14-336"
# model_name = "openai/clip-vit-large-patch14"
# model_name = "openai/clip-vit-base-patch16"
# model_name = "openai/clip-vit-base-patch32"
# model_name = "kevinoli/clip-finetuned-csu-p14-336-e4l27-l"
# model_name = "kevinoli/clip-finetuned-csu-p14-336-e3l87-l"
# model_name = "openai/clip-vit-large-patch14-336"
# model_name = "kevinoli/clip-finetuned-csu-p14-336-e4l97-l"
# model_name = "kevinoli/clip-finetuned-csu-p14-336-e3l37-l"
# model_name = "/Users/kevintruong/programming/projects/aesthetic-matcher/models/checkpoint-28000"
# model_name = "kevinoli/clip-finetuned-csu-p14-336-e3l17-l"
model_name = "kevinoli/clip-finetuned-csu-p14-336-e3l57-l"
print("============",model_name)
process_name = "openai/clip-vit-base-patch32"
process_name = "openai/clip-vit-large-patch14-336"
processor = CLIPProcessor.from_pretrained(process_name)
model = CLIPModel.from_pretrained(model_name)

# Check if CUDA is available and move the model to GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
print("CUDA Availability: ", torch.cuda.is_available(), flush=True)

# Function to process image with CLIP model
def process_image(image,features):
    # Process features
    inputs = processor(text=features, images=[image], return_tensors="pt", padding=True)
    # Move tensors to GPU
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)

    # Concatenate probabilities
    all_probs = probs.cpu()

    # Get the indices of the top 5 categories with highest probabilities
    top_indices = torch.argsort(all_probs, descending=True)[0][:10]

    # Retrieve and print the top 5 categories and their probabilities
    top_categories = [(features[idx.item()], round(all_probs[0, idx].item()*100, 2)) for idx in top_indices]
    # for i, (category, probability) in enumerate(top_categories, 1):
    #     print(f"{i} {category} {probability:.2f}")
    return top_categories

# List of image URLs
urls = [
    # ("cat", "https://i.ibb.co/MkBbFn7/image.jpg"),
    # ("pale grunge", "https://static.wikia.nocookie.net/aesthetics/images/3/3d/Pale_grunge_moodboard.png"),
    # ("trillwave", "https://static.wikia.nocookie.net/aesthetics/images/d/dd/Screenshot_154.jpg"),
    # ("scandi girl winter", "https://static.wikia.nocookie.net/aesthetics/images/4/4a/Scandi_Girl_Winter_1.jpg/revision/latest?cb=20230809142838"),
    # ("cottage core", "https://i0.wp.com/makenstitch.com/wp-content/uploads/Cottagecore-Beginners-Guide-intro.jpg?resize=720%2C720&ssl=1"),
    # ("grunge", "https://media.gq-magazine.co.uk/photos/65256607c60c63ce892623fc/1:1/w_1080,h_1080,c_limit/GQ_OCTOBER_ONLINE_GRUNGE_HEADER.jpg"),
    # ("dark nymphet", "https://static.wikia.nocookie.net/aesthetics/images/e/e7/Dark_parfum.jpeg/revision/latest?cb=20230904082153"),
    # ("weeb nymphet", "https://i.ibb.co/T1c20wn/Screenshot-2024-08-03-at-12-39-54-PM.png")
    ("yt", "https://img.youtube.com/vi/igAML-08IJo/maxresdefault.jpg")
]

for caption, url in urls:
    try:
        image = Image.open(requests.get(url, stream=True).raw)
        print(caption,"---------", url)
        stats = process_image(image,aesthetics_list)
        for cat, prob in stats[:10]:
            print(" - ",cat, prob)
    except Exception as e:
        print(f"Error processing {url}: {e}")

# ssh -fN -L 8888:localhost:8888 
# watch -n0.1 nvidia-smi
# nohup jupyter notebook --no-browser --port=8888
