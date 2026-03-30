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
    # Load and prepare image
    image = Image.open(uploaded_file).convert("RGBA")

    # Resize for stability (important for Streamlit Cloud)
    max_size = 512
    image.thumbnail((max_size, max_size))

    img_array = np.array(image)

    st.subheader("Original Image")
    st.image(image, use_column_width=True)

    # Brush size
    brush_size = st.slider("Brush Size", 5, 50, 20)

    st.subheader("Draw over the area you want to erase")

    # Canvas (FIXED)
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=brush_size,
        stroke_color="white",
        background_image=image,  # ✅ FIX: Use PIL image (not numpy)
        update_streamlit=True,
        height=image.height,
        width=image.width,
        drawing_mode="freedraw",
        key="canvas",
    )

    # Process result
    if canvas_result.image_data is not None:
        # Extract alpha mask safely
        mask = canvas_result.image_data[:, :, 3]

        # Convert to binary mask
        mask = (mask > 0).astype(np.uint8) * 255

        # Resize mask to match image
        mask = cv2.resize(mask, (img_array.shape[1], img_array.shape[0]))

        # Convert RGBA → RGB for OpenCV
        img_rgb = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)

        # Inpaint (erase selected area)
        result = cv2.inpaint(img_rgb, mask, 3, cv2.INPAINT_TELEA)

        st.subheader("🧼 Erased Image")
        st.image(result, use_column_width=True)

        # Download button (FIXED)
        result_pil = Image.fromarray(result)

        import io
        buf = io.BytesIO()
        result_pil.save(buf, format="PNG")

        st.download_button(
            label="📥 Download Image",
            data=buf.getvalue(),
            file_name="erased_image.png",
            mime="image/png"
        )
