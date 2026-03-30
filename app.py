import streamlit as st
import numpy as np
import cv2
from PIL import Image
from streamlit_drawable_canvas import st_canvas

st.set_page_config(page_title="Image Spot Eraser", layout="centered")

st.title("🖌️ Image Spot Eraser Tool")

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")

    # Resize (important for Streamlit Cloud stability)
    max_size = 512
    image.thumbnail((max_size, max_size))

    img_array = np.array(image)

    st.subheader("Original Image")
    st.image(image, use_column_width=True)

    # Brush size
    brush_size = st.slider("Brush Size", 5, 50, 20)

    st.subheader("Draw over the area you want to erase")

    # Canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=brush_size,
        stroke_color="white",
        background_image=img_array,  # FIXED
        update_streamlit=True,
        height=img_array.shape[0],
        width=img_array.shape[1],
        drawing_mode="freedraw",
        key="canvas",
    )

    if canvas_result.image_data is not None:
        # Extract mask
        mask = canvas_result.image_data[:, :, 3]

        # Convert to binary mask
        mask = (mask > 0).astype(np.uint8) * 255

        # Resize mask properly
        mask = cv2.resize(mask, (img_array.shape[1], img_array.shape[0]))

        # Inpaint (erase drawn area)
        result = cv2.inpaint(img_array, mask, 3, cv2.INPAINT_TELEA)

        st.subheader("🧼 Erased Image")
        st.image(result, use_column_width=True)

        # Download
        result_pil = Image.fromarray(result)
        st.download_button(
            label="📥 Download Image",
            data=result_pil.tobytes(),
            file_name="erased_image.png",
            mime="image/png"
        )
