import ffmpeg
import logging

logger = logging.getLogger(__name__)

def process_video(input_path: str, output_path: str, preset: str, job_id: str):
    """
    Mock wrapper for FFmpeg
    """
    logger.info(f"[{job_id}] Running ffmpeg on {input_path} to {output_path} with {preset}")
    # Example logic using ffmpeg-python:
    # stream = ffmpeg.input(input_path)
    # stream = ffmpeg.output(stream, output_path, video_bitrate='1000k', audio_bitrate='128k', s='1280x720')
    # ffmpeg.run(stream)
    pass
