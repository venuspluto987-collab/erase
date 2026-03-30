import streamlit as st
import numpy as np
import cv2
from PIL import Image
from streamlit_drawable_canvas import st_canvas

st.title("🖌️ Image Spot Eraser Tool")

# 1️⃣ Upload Image
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    img_array = np.array(image)

    st.subheader("Original Image")
    st.image(image, use_column_width=True)

    st.subheader("Draw over the area you want to erase")

    # 2️⃣ Canvas to select area
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",  # transparent red
        stroke_width=20,
        stroke_color="white",
        background_image=image,
        update_streamlit=True,
        height=image.height,
        width=image.width,
        drawing_mode="freedraw",
        key="canvas",
    )

    if canvas_result.image_data is not None:
        mask = canvas_result.image_data[:, :, 3]  # alpha channel

        # Convert mask to binary
        mask = (mask > 0).astype(np.uint8) * 255

        # Resize mask if needed
        mask = cv2.resize(mask, (img_array.shape[1], img_array.shape[0]))

        # 3️⃣ Inpaint (erase selected area)
        result = cv2.inpaint(img_array, mask, 3, cv2.INPAINT_TELEA)

        st.subheader("🧼 Erased Image")
        st.image(result, use_column_width=True)

        # 4️⃣ Download
        result_img = Image.fromarray(result)
        st.download_button(
            label="Download Image",
            data=result_img.tobytes(),
            file_name="erased_image.png",
            mime="image/png"
        )