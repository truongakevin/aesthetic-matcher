# hello everyone!  I'm working on a university project that uses AI to classify aesthetic styles. It's going to be an app or website that allows you to take or upload a picture that will then use an AI model to classify the aesthetic. I am currently working on building a dataset of labeled pictures by aesthetic to train the model, so if anyone has any websites or resources where I might be able to find aesthetics and images that match them that would be helpful. right now im working on scraping all the pictures from the aesthetics wiki website but any other resources would be much appreciated!
# hey everyone! ive been working on a website that matches images to aesthetics so you can upload an image and it will tell you what aesthetic it is. it uses a finetuned machine learning model trained on all images from the aesthetics wiki. i finally got it to a working state so i wanted to share it with yall! its still a work in progress so im open to suggestions and it is running on my local machine so it might be a bit slow and possibly buggy but the website is kevinatruong.com/aesthetic-matcher/
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import requests
import torch
import os
import random
# import aesthetics
from listaesthetics import aesthetics

# List of aesthetics
aesthetics_list = aesthetics

# # model_name = "openai/clip-vit-large-patch14-336"
model_name = "kevinoli/clip-finetuned-csu-p14-336-e3l57-l"
print("============",model_name)
process_name = "openai/clip-vit-large-patch14-336"
processor = CLIPProcessor.from_pretrained(process_name)
model = CLIPModel.from_pretrained(model_name)

# Check if CUDA is available and move the model to GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
print("CUDA Availability: ", torch.cuda.is_available(), flush=True)

# # List of image URLs
# urls = [
#     # # ("cat", "https://i.ibb.co/MkBbFn7/image.jpg"),
#     # # ("pale grunge", "https://static.wikia.nocookie.net/aesthetics/images/3/3d/Pale_grunge_moodboard.png"),
#     # ("trillwave", "https://static.wikia.nocookie.net/aesthetics/images/d/dd/Screenshot_154.jpg"),
#     # ("scandi girl winter", "https://static.wikia.nocookie.net/aesthetics/images/4/4a/Scandi_Girl_Winter_1.jpg/revision/latest?cb=20230809142838"),
#     # # ("cottage core", "https://i0.wp.com/makenstitch.com/wp-content/uploads/Cottagecore-Beginners-Guide-intro.jpg?resize=720%2C720&ssl=1"),
#     # # ("grunge", "https://media.gq-magazine.co.uk/photos/65256607c60c63ce892623fc/1:1/w_1080,h_1080,c_limit/GQ_OCTOBER_ONLINE_GRUNGE_HEADER.jpg"),
#     ("dark nymphet", "https://static.wikia.nocookie.net/aesthetics/images/e/e7/Dark_parfum.jpeg/revision/latest?cb=20230904082153"),
#     ("weeb nymphet", "https://i.ibb.co/T1c20wn/Screenshot-2024-08-03-at-12-39-54-PM.png")
# ]

# images = []

# for caption, url in urls:
#     try:
#         image = Image.open(requests.get(url, stream=True).raw)
#         images.append(image)
#     except Exception as e:
#         print(f"Error processing {url}: {e}")

# Path to the folder containing images
image_folder_path = "datarefinement/aesthetics_images_3_cleaned/Dark Nymphet"

# Initialize an empty list to store images
images = []

# Loop through all the image files in the folder
for file_name in os.listdir(image_folder_path):
    if file_name.endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):  # Adjust the extensions as needed
        file_path = os.path.join(image_folder_path, file_name)
        try:
            # Open and load the image
            image = Image.open(file_path)
            images.append(image)
        except Exception as e:
            print(f"Error loading {file_name}: {e}")


# # Process features
# inputs = processor(text=features, images=images, return_tensors="pt", padding=True)
# inputs = {k: v.to(device) for k, v in inputs.items()}
# with torch.no_grad():
#     outputs = model(**inputs)
# logits_per_image = outputs.logits_per_image

# # Calculate probabilities for each image
# probs = logits_per_image.softmax(dim=1)
# combined_probs = probs.mean(dim=0)

# # Get top categories
# top_categories = [(aesthetics[idx.item()]) for idx in torch.argsort(combined_probs, descending=True)[:num_features*5]]

# # Recalculate on top categories
# inputs = processor(text=top_categories, images=images, return_tensors="pt", padding=True)
# inputs = {k: v.to(device) for k, v in inputs.items()}
# with torch.no_grad():
#     outputs = model(**inputs)
# logits_per_image = outputs.logits_per_image
# probs = logits_per_image.softmax(dim=1)
# combined_probs = probs.mean(dim=0)

# # Get the top 10 categories with the highest combined probabilities
# top_indices = torch.argsort(combined_probs, descending=True)[:num_features]

# # Retrieve the top categories and their combined probabilities
# tip_categories = [(top_categories[idx.item()], round(combined_probs[idx].item() * 100, 2)) for idx in top_indices]

# # Print the combined results
# for i, (category, probability) in enumerate(tip_categories, 1):
#     print(f"{i}: {category} - {probability:.2f}%")
    
    
def process_image(images, features, num_features=7, batch_splits=2):
    def process_batches(features, batch_size):
        probs_list = []
        for i in range(0, len(features), batch_size):
            batch_features = features[i:i + batch_size]
            inputs = processor(text=batch_features, images=images, return_tensors="pt", padding=True)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = model(**inputs)
            
            # Softmax probabilities for each image, averaged over all images
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1).cpu()
            combined_probs = probs.mean(dim=0)  # Average probs across images
            probs_list.append(combined_probs)
        
        # Concatenate probabilities for all batches
        return torch.cat(probs_list, dim=0)

    random.shuffle(features)
    batch_size = len(features) // batch_splits
    
    # Step 1: Process all features and get their probabilities
    all_probs = process_batches(features, batch_size)
    
    # Step 2: Select top features based on their probabilities
    top_indices = torch.argsort(all_probs, descending=True)[:num_features*10]
    top_features = [features[idx.item()] for idx in top_indices]
    
    # Step 3: Reprocess top features to get final probabilities
    top_probs = process_batches(top_features, batch_size)
    
    # Step 4: Get the top categories and their probabilities
    top_indices_final = torch.argsort(top_probs, descending=True)[:num_features]
    top_categories = [(top_features[idx.item()], round(top_probs[idx].item() * 100, 2)) for idx in top_indices_final]
    
    # Print top categories with their probabilities
    for i, (category, probability) in enumerate(top_categories, 1):
        print(f"{i}. {category} {probability:.2f}%")
    
    return top_categories

            
num_features = 10
features = aesthetics

process_image(images, features, num_features=num_features)