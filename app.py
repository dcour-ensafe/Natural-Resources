import numpy as np
import streamlit as st

from soil_analysis import analyze_soil_image, load_image_rgb


st.set_page_config(page_title="Wetland Soil Color Identifier", layout="wide")
st.title("Wetland Soil Color Identifier (Prototype)")
st.write(
    "Upload a soil sample image to estimate matrix color and secondary redoximorphic features."
)

upload = st.file_uploader("Upload soil image", type=["jpg", "jpeg", "png", "webp"])

if upload:
    file_bytes = upload.getvalue()
    rgb = load_image_rgb(file_bytes)

    col1, col2 = st.columns(2)
    with col1:
        st.image(rgb, caption="Uploaded image", use_container_width=True)

    try:
        result = analyze_soil_image(rgb)
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    matrix = result["matrix"]
    secondary = result["secondary_features"]

    with col2:
        st.subheader("Estimated soil composition")
        st.metric("Soil coverage in image", f"{result['soil_coverage_percent']}%")
        st.metric("Matrix proportion", f"{matrix.percentage}%")
        st.write(f"**Matrix Munsell:** {matrix.munsell}")
        st.color_picker(
            "Matrix representative color",
            value="#%02x%02x%02x" % tuple(np.clip(matrix.rgb, 0, 255).astype(int)),
            disabled=True,
        )

        st.write("**Secondary / redox feature estimates**")
        if not secondary:
            st.info("No meaningful secondary features detected above 2% threshold.")
        else:
            for i, feature in enumerate(secondary, start=1):
                st.write(f"{i}. **{feature.munsell}** — {feature.percentage}%")
                st.color_picker(
                    f"Feature {i} representative color",
                    value="#%02x%02x%02x" % tuple(np.clip(feature.rgb, 0, 255).astype(int)),
                    disabled=True,
                    key=f"feature_{i}",
                )

    st.subheader("Soil pixel mask preview")
    mask = result["soil_mask"]
    overlay = rgb.copy()
    overlay[~mask] = (overlay[~mask] * 0.25).astype(np.uint8)
    st.image(overlay, caption="Likely-soil regions are brighter", use_container_width=True)
