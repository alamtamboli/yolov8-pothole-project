import os

# Change these paths if needed
images_path = "dataset/images/train"
labels_path = "dataset/labels/train"

# Get file names without extension
images = [os.path.splitext(f)[0] for f in os.listdir(images_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
labels = [os.path.splitext(f)[0] for f in os.listdir(labels_path) if f.lower().endswith('.txt')]

# Find mismatches
missing_labels = set(images) - set(labels)
missing_images = set(labels) - set(images)

print("Images without labels:", missing_labels)
print("Labels without images:", missing_images)

# Optionally delete extra images
for img_name in missing_labels:
    for ext in ['.jpg', '.jpeg', '.png']:
        img_file = os.path.join(images_path, img_name + ext)
        if os.path.exists(img_file):
            print(f"Deleting {img_file} (no label found)")
            os.remove(img_file)

# Optionally delete extra labels
for lbl_name in missing_images:
    lbl_file = os.path.join(labels_path, lbl_name + ".txt")
    if os.path.exists(lbl_file):
        print(f"Deleting {lbl_file} (no image found)")
        os.remove(lbl_file)

print("Cleanup complete ✅")
