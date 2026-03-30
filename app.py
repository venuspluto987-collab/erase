import streamlit as st
import numpy as np
import cv2
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import io
import base64

st.set_page_config(page_title="Image Spot Eraser", layout="centered")

st.title("🖌️ Image Spot Eraser Tool")

# Function to convert image → base64
def pil_to_base64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

# Upload image
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Load image
    image = Image.open(uploaded_file).convert("RGBA")

    # Resize (important)
    image.thumbnail((512, 512))

    img_array = np.array(image)

    st.subheader("Original Image")
    st.image(image, use_column_width=True)

    # Brush size
    brush_size = st.slider("Brush Size", 5, 50, 20)

    # Convert image → base64 (🔥 KEY FIX)
    img_base64 = pil_to_base64(image)

    st.subheader("Draw over the area you want to erase")

    # Canvas (FINAL FIX)
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=brush_size,
        stroke_color="white",
        background_image=img_base64,  # ✅ FIXED HERE
        update_streamlit=True,
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

        # Convert RGBA → RGB
        img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)

        # Inpaint
        result = cv2.inpaint(img_rgb, mask, 3, cv2.INPAINT_TELEA)

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
