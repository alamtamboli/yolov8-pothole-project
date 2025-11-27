import os

def check_pairs(img_dir, lbl_dir):
    imgs = {os.path.splitext(f)[0] for f in os.listdir(img_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))}
    lbls = {os.path.splitext(f)[0] for f in os.listdir(lbl_dir) if f.lower().endswith('.txt')}

    missing_labels = imgs - lbls
    missing_images = lbls - imgs

    print(f"\nChecking: {img_dir}")
    print("Images without labels:", missing_labels if missing_labels else "✅ None")
    print("Labels without images:", missing_images if missing_images else "✅ None")


if __name__ == "__main__":
    # Adjust paths if needed
    check_pairs("dataset/images/train", "dataset/labels/train")
    check_pairs("dataset/images/val", "dataset/labels/val")
