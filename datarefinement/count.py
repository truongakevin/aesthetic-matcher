import os

def get_folder_size(folder_path):
    """Calculate the total size of the folder in bytes."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

def print_folder_size(base_folder):
    """Print the size of the base folder."""
    if not os.path.exists(base_folder):
        print(f"Base folder '{base_folder}' does not exist.")
        return
    
    folder_size = get_folder_size(base_folder)
    print(f"Total size of '{base_folder}': {folder_size / (1024**2):.2f} MB")  # Size in MB

def count_images_in_folders(base_folder):
    full_count = 0
    """Count the number of images in each subfolder of the base folder and print the results in aligned columns, sorted by image count."""
    if not os.path.exists(base_folder):
        print(f"Base folder '{base_folder}' does not exist.")
        return

    results = []
    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        if os.path.isdir(folder_path):
            image_count = len([file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file)) and file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))])
            full_count += image_count
            results.append((folder_name, image_count))

    # Sort results by image count in descending order
    results.sort(key=lambda x: x[1], reverse=True)

    # Find the maximum length of folder names for formatting
    max_folder_name_length = max(len(folder_name) for folder_name, _ in results) if results else 0
    max_count_length = max(len(str(count)) for _, count in results) if results else 0

    # Print the results in aligned columns
    print(f"Full Files Count: {full_count}")
    # print(f"{'Folder Name'.ljust(max_folder_name_length + 2)}{'Image Count'.rjust(max_count_length)}")
    # print('-' * (max_folder_name_length + max_count_length + 2))
    # for folder_name, image_count in results:
    #     print(f"{folder_name.ljust(max_folder_name_length + 2)}{str(image_count).rjust(max_count_length)}")

base_folder = 'aesthetics_images_2'
# Print the size of the folder
print_folder_size(base_folder)
# Count and print the number of images in each folder
count_images_in_folders(base_folder)

base_folder = 'aesthetics_images_2_cleaned'
# Print the size of the folder
print_folder_size(base_folder)
# Count and print the number of images in each folder
count_images_in_folders(base_folder)

base_folder = 'aesthetics_images_3'
# Print the size of the folder
print_folder_size(base_folder)
# Count and print the number of images in each folder
count_images_in_folders(base_folder)

base_folder = 'aesthetics_images_3_cleaned'
# Print the size of the folder
print_folder_size(base_folder)
# Count and print the number of images in each folder
count_images_in_folders(base_folder)
