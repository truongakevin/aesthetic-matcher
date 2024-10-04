from PIL import Image, ImageFile, UnidentifiedImageError
import os
import re
from torchvision.io import read_image, ImageReadMode

# To handle truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

def remove_special_characters(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_split = file.split('.')
            new_name = re.sub(r'[^a-zA-Z0-9_\-]', '', file_split[0])
            if '.' in file:
                new_name = f"{new_name}.{file_split[-1]}"
            if new_name != file:
                os.rename(os.path.join(root, file), os.path.join(root, new_name))
                print(f"{os.path.join(root, file)}\n{os.path.join(root, new_name)}\n")

def add_jpg_extension(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if not file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.PNG', '.JPG')):  # Check if file has a common image extension
                try:
                    # Try to open the file with PIL to check if it's an image
                    with Image.open(file_path) as img:
                        img.verify()  # Verifies if it's a valid image
                    file_split = file_path.split('.')
                    new_file_path = f"{file_split[0]}.jpg"
                    print(file_path)
                    print(new_file_path)
                    print()
                    os.rename(file_path, new_file_path)
                except (IOError, SyntaxError) as e:
                    print(f"File {file_path} is not a valid image or has a different format.")
                    os.remove(file_path)

def convert_images(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            image_path = os.path.join(root, filename)
            
            try:
                # Attempt to read the image using torchvision
                img = read_image(image_path, mode=ImageReadMode.RGB)
            except Exception as e:
                print(image_path)
                print(f"Failed to read image: {filename} with error {e}")

                try:
                    # Handle corrupt images and image profile issues
                    with Image.open(image_path) as img:
                        img.verify()  # Check if the image file is corrupted
                        img = Image.open(image_path)  # Reopen the image to process it
                        img.info.pop('icc_profile', None)
                        rgb_img = img.convert('RGB')
                        new_path = os.path.splitext(image_path)[0] + '.jpeg'
                        rgb_img.save(new_path, 'JPEG', quality=95)  # Save with high quality
                        os.remove(image_path)
                        print(f"Converted {image_path} to {new_path}")

                        try:
                            # Retry reading the converted image
                            img = read_image(new_path, mode=ImageReadMode.RGB)
                            print(f"Successfully read converted image: {filename}")
                        except Exception as e:
                            print(f"----Failed to read converted image: {new_path} with error {e}")

                except (UnidentifiedImageError, IOError) as e:
                    print(f"File {image_path} is not a valid image or has a different format. Removing file.")
                    os.remove(image_path)
        target_format = 'jpeg'
    for subdir, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('gif', 'bmp', 'tiff')):
                image_path = os.path.join(subdir, file)
                with Image.open(image_path) as img:
                    rgb_img = img.convert('RGB')
                    new_path = os.path.splitext(image_path)[0] + f'.{target_format}'
                    rgb_img.save(new_path, format=target_format.upper())
                    os.remove(image_path)  # Remove the old file
                    print(f"Converted {image_path} to {new_path}")
                
def convert_images2(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            image_path = os.path.join(root, filename)
            
            # Attempt to read the image
            try:
                img = read_image(image_path, mode=ImageReadMode.RGB)
#                 print(f"Successfully read image: {filename}")
            except Exception as e:
                print(f"Failed to read image: {filename} with error: {e}")

                # If reading fails, try to convert the image
                try:
                    with Image.open(image_path) as img:
                        # Ensure image is in RGB mode and save as JPEG
                        rgb_img = img.convert('RGB')
                        new_path = os.path.splitext(image_path)[0] + '.jpg'

                        # Prevent overwriting the original file with the same name
                        if new_path.lower() == image_path.lower():
                            new_path = os.path.splitext(image_path)[0] + '_converted.jpg'

                        rgb_img.save(new_path, 'JPEG')
                        os.remove(image_path)
                        print(f"Converted {image_path} to {new_path}")

                        # Retry reading the converted image
                        try:
                            img = read_image(new_path, mode=ImageReadMode.RGB)
#                             print(f"Successfully read converted image: {os.path.basename(new_path)}")
                        except Exception as e:
                            print(f"Failed to read converted image: {new_path} with error: {e}")
                except Exception as e:
                    print(f"Error processing {image_path}: {e}")
                        
def verify_images(directory):
    suc = 0
    fail = 0
    for root, dirs, files in os.walk(directory):
        for filename in files:
            image_path = os.path.join(root, filename)
            # Attempt to read the image
            try:
                img = read_image(image_path, mode=ImageReadMode.RGB)
                suc += 1
            except Exception as e:
                print(image_path)
                fail += 1
    print(suc, "sucessfully read")     
    print(fail, "failed read")
    
# Specify your folder path here
folder_path = 'aesthetics_images_3_cleaned'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Remove special characters from filenames
remove_special_characters(folder_path)

# Add .jpg extension where needed
add_jpg_extension(folder_path)

# Convert images and handle edge cases
convert_images(folder_path)
convert_images2(folder_path)

# verify images
print("=============================")
print("=============================")
print("=============================")
print("=============================")
print("=============================")
verify_images(folder_path)