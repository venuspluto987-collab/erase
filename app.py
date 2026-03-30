import streamlit as st
import numpy as np
import cv2
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io

st.set_page_config(page_title="Image Spot Eraser", layout="centered")

st.title("🖌️ Image Spot Eraser Tool")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Load image
    image = Image.open(uploaded_file).convert("RGB")
    image.thumbnail((512, 512))

    img_array = np.array(image)

    st.subheader("Original Image")
    st.image(image, use_column_width=True)

    st.subheader("Draw area to erase (same position as image)")

    # Brush size
    brush_size = st.slider("Brush Size", 5, 50, 20)

    # Blank canvas (NO background_image → avoids crash)
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=brush_size,
        stroke_color="white",
        background_color="rgba(0,0,0,0)",  # transparent
        height=image.height,
        width=image.width,
        drawing_mode="freedraw",
        key="canvas",
    )

    if canvas_result.image_data is not None:
        # Extract mask
        mask = canvas_result.image_data[:, :, 3]
        mask = (mask > 0).astype(np.uint8) * 255

        mask = cv2.resize(mask, (img_array.shape[1], img_array.shape[0]))

        # Inpaint
        result = cv2.inpaint(img_array, mask, 3, cv2.INPAINT_TELEA)

        st.subheader("🧼 Erased Image")
        st.image(result, use_column_width=True)

        # Download
        result_pil = Image.fromarray(result)
        buf = io.BytesIO()
        result_pil.save(buf, format="PNG")

        st.download_button(
            label="📥 Download Image",
            data=buf.getvalue(),
            file_name="erased_image.png",
            mime="image/png"
        )
