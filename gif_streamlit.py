import os
import subprocess
import streamlit as st

def convert_to_gif(input_path, output_path):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", "fps=10,scale=600:-1:flags=lanczos",
        "-c:v", "gif",
        output_path
    ]
    subprocess.run(command, check=True)

def add_watermark(input_gif, output_gif, watermark_text, font_size, opacity):
    command = [
        "ffmpeg",
        "-i", input_gif,
        "-vf", f"drawtext=text='{watermark_text}':fontcolor=white@{opacity}:fontsize={font_size}:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "gif",
        output_gif
    ]
    subprocess.run(command, check=True)

def process_files(file_paths, watermark_text, font_size, opacity):
    for file_path in file_paths:
        try:
            st.info(f"Processing {os.path.basename(file_path)}...")
            output_gif_path = os.path.splitext(file_path)[0] + ".gif"
            temp_gif_path = os.path.splitext(file_path)[0] + "_temp.gif"

            # Convert MP4 to GIF
            convert_to_gif(file_path, temp_gif_path)

            # Add watermark
            add_watermark(temp_gif_path, output_gif_path, watermark_text, font_size, opacity)

            # Delete temporary GIF file
            os.remove(temp_gif_path)

            st.success(f"Completed: {output_gif_path}")
        except Exception as e:
            st.error(f"Error processing {file_path}: {e}")

# Streamlit App
st.title("GIF 변환 및 워터마크 삽입기")

# Sidebar for user inputs
watermark_text = st.sidebar.text_input("워터마크 텍스트", value="luxmixlounge.com")
font_size = st.sidebar.slider("텍스트 크기", min_value=10, max_value=100, value=24)
opacity = st.sidebar.slider("텍스트 투명도", min_value=0.1, max_value=1.0, value=0.5, step=0.1)

# File uploader
uploaded_files = st.file_uploader("MP4 파일을 업로드하세요", type=["mp4"], accept_multiple_files=True)

if uploaded_files:
    if st.button("변환 시작"):
        # Save uploaded files locally
        file_paths = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join("temp", uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())
            file_paths.append(file_path)
        
        # Create output directory if it doesn't exist
        if not os.path.exists("temp"):
            os.makedirs("temp")

        # Process files
        process_files(file_paths, watermark_text, font_size, opacity)

        # Provide download links
        st.success("모든 변환 완료!")
        for file_path in file_paths:
            output_gif_path = os.path.splitext(file_path)[0] + ".gif"
            with open(output_gif_path, "rb") as f:
                st.download_button(
                    label=f"{os.path.basename(output_gif_path)} 다운로드",
                    data=f,
                    file_name=os.path.basename(output_gif_path),
                    mime="image/gif",
                )

        # Clean up temp directory
        for file_path in file_paths:
            os.remove(file_path)
