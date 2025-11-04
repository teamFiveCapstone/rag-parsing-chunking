from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf

# !!!!!!! EXPERIMENT 1:
elements = partition(filename="../files/wwf_tigers_e_1.pdf")
with open("../files/auto-partition-output.txt", "w") as f:
    f.write("\n\n".join([str(el) for el in elements]))

# !!!!!! EXPERIMENT 2:
import os
os.makedirs("../files/images/", exist_ok=True)

# I am using extract_image_block_to_payload=False (instead I write write the images
# to the images folder)
elementsTwo = partition_pdf(filename="../files/wwf_tigers_e_1.pdf",
                            strategy="hi_res", extract_images_in_pdf=True,
                            extract_image_block_types=["Image", "Table"],
                            extract_image_block_to_payload=False,
                            extract_image_block_output_dir="../files/images/"
                            )
with open("../files/pdf-partition-output.txt", "w") as f:
    f.write("\n\n".join([str(el) for el in elements]))

# Write text content to file
with open("../files/pdf-partition-output.txt", "w") as f:
    f.write("\n\n".join([str(el) for el in elementsTwo]))

# Check how many images were saved to filesystem
import glob
saved_images = glob.glob("../files/images/*")
print(f"Total images saved to filesystem: {len(saved_images)}")
for img in saved_images:
    print(f"  {img}")
