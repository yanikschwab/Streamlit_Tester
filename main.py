import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import json

# Path to the PDF file
pdf_path = "/Users/yschwab/Downloads/w2.png.pdf"

# Convert PDF to images
pages = convert_from_path(pdf_path)

# Iterate over each page
for page_num, page in enumerate(pages, start=1):
    # Convert to editable image
    img = page.copy()
    draw = ImageDraw.Draw(img)

    # Perform OCR with bounding box detection
    ocr_data = pytesseract.image_to_data(page, output_type=pytesseract.Output.DICT)

    text_data = []  # Store extracted text positions

    # Loop through detected text elements
    for i in range(len(ocr_data["text"])):
        if ocr_data["text"][i].strip():  # Ignore empty text
            x0, y0, width, height = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
            x1, y1 = x0 + width, y0 + height  # Bottom-right corner
            
            # Draw bounding box
            draw.rectangle([(x0, y0), (x1, y1)], outline="red", width=2)

            # Append extracted data for saving
            text_data.append({
                "page": page_num,
                "text_start": ocr_data["text"][i][:10],  # First 10 characters
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1
            })

    # Save the annotated image
    annotated_image_path = f"/Users/yschwab/Downloads/annotated_page_{page_num}.png"
    img.save(annotated_image_path)
    print(f"Saved annotated image: {annotated_image_path}")

    # Save extracted text positions to JSON
    json_path = f"/Users/yschwab/Downloads/text_positions_page_{page_num}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(text_data, f, indent=4)
    print(f"Saved text positions to {json_path}")