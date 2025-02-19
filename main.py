import streamlit as st
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import json
import os

# Streamlit Title
st.title("PDF OCR & Text Detection App")

# File Uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    # Save uploaded PDF temporarily
    pdf_path = "temp.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Convert PDF to images
    st.write("Converting PDF to images...")
    pages = convert_from_path(pdf_path)

    annotated_images = []
    text_data = []

    for page_num, page in enumerate(pages, start=1):
        st.write(f"Processing Page {page_num}...")

        # Convert to editable image
        img = page.copy()
        draw = ImageDraw.Draw(img)

        # Perform OCR with bounding box detection
        ocr_data = pytesseract.image_to_data(page, output_type=pytesseract.Output.DICT)

        # Loop through detected text elements
        for i in range(len(ocr_data["text"])):
            if ocr_data["text"][i].strip():  # Ignore empty text
                x0, y0, width, height = (
                    ocr_data["left"][i],
                    ocr_data["top"][i],
                    ocr_data["width"][i],
                    ocr_data["height"][i],
                )
                x1, y1 = x0 + width, y0 + height  # Bottom-right corner
                
                # Draw bounding box
                draw.rectangle([(x0, y0), (x1, y1)], outline="red", width=2)

                # Append extracted data for display
                text_data.append({
                    "page": page_num,
                    "text_start": ocr_data["text"][i][:10],  # First 10 characters
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1
                })

        # Convert PIL image to Streamlit displayable format
        annotated_images.append(img)

    # Display extracted text
    st.write("### Extracted Text Positions:")
    st.json(text_data)

    # Display annotated images
    st.write("### Annotated Images with Bounding Boxes:")
    for img in annotated_images:
        st.image(img, caption="Annotated Page", use_column_width=True)

    # Save JSON file
    json_path = "text_positions.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(text_data, f, indent=4)

    # Provide download link for JSON
    with open(json_path, "rb") as f:
        st.download_button(
            label="Download Text Positions JSON",
            data=f,
            file_name="text_positions.json",
            mime="application/json",
        )

    # Clean up temporary files
    os.remove(pdf_path)
    os.remove(json_path)