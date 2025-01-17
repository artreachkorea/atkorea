import os
import subprocess
import streamlit as st
import tempfile

# FFmpeg 설치 확인 및 다운로드
def check_ffmpeg():
    try:
        # FFmpeg 버전 확인
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        st.info("FFmpeg가 설치되지 않았습니다. 설치를 진행합니다...")
        try:
            # FFmpeg 다운로드 (Linux 환경 기준)
            ffmpeg_url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-64bit-static.tar.xz"
            subprocess.run(["wget", ffmpeg_url], check=True)
            subprocess.run(["tar", "xvf", "ffmpeg-release-64bit-static.tar.xz"], check=True)
            ffmpeg_dir = "ffmpeg-release-64bit-static"
            os.environ["PATH"] += os.pathsep + os.path.abspath(ffmpeg_dir)
            st.success("FFmpeg 설치 완료!")
        except Exception as e:
            st.error(f"FFmpeg 설치 중 오류 발생: {e}")

# FFmpeg 설치 확인
check_ffmpeg()

# MP4 -> GIF 변환 함수
def convert_to_gif(input_path, output_path):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", "fps=10,scale=600:-1:flags=lanczos",
        "-c:v", "gif",
        output_path
    ]
    subprocess.run(command, check=True)

# GIF에 워터마크 추가 함수
def add_watermark(input_gif, output_gif, watermark_text, font_size, opacity):
    command = [
        "ffmpeg",
        "-i", input_gif,
        "-vf", f"drawtext=text='{watermark_text}':fontcolor=white@{opacity}:fontsize={font_size}:x=(w-text_w)/2:y=(h-text_h)/2",
        "-c:v", "gif",
        output_gif
    ]
    subprocess.run(command, check=True)

# 업로드된 파일 처리 함수
def process_files(uploaded_files, watermark_text, font_size, opacity):
    for uploaded_file in uploaded_files:
        try:
            # 임시 디렉토리에 파일 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            # GIF 변환 파일 경로
            output_gif_path = temp_file_path.replace(".mp4", ".gif")
            temp_gif_path = temp_file_path.replace(".mp4", "_temp.gif")

            # MP4 -> GIF 변환
            st.info(f"Converting {uploaded_file.name} to GIF...")
            convert_to_gif(temp_file_path, temp_gif_path)

            # GIF에 워터마크 추가
            st.info(f"Adding watermark to {uploaded_file.name}...")
            add_watermark(temp_gif_path, output_gif_path, watermark_text, font_size, opacity)

            # 결과 다운로드 버튼 제공
            with open(output_gif_path, "rb") as output_file:
                st.download_button(
                    label=f"{uploaded_file.name} - GIF 다운로드",
                    data=output_file,
                    file_name=f"{uploaded_file.name.replace('.mp4', '.gif')}",
                    mime="image/gif"
                )

            # 임시 파일 삭제
            os.remove(temp_file_path)
            os.remove(temp_gif_path)
            os.remove(output_gif_path)

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

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
        process_files(uploaded_files, watermark_text, font_size, opacity)
