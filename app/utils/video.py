"""Video processing utilities using ffmpeg."""
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import BinaryIO, Optional, Tuple

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles video processing and metadata extraction."""

    @staticmethod
    def get_video_duration(file_path: str) -> float:
        """Get video duration in seconds using ffprobe.

        Args:
            file_path: Path to video file

        Returns:
            Duration in seconds
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                file_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                logger.error(f"ffprobe failed: {result.stderr}")
                return 0.0

            data = json.loads(result.stdout)
            duration = float(data.get('format', {}).get('duration', 0))

            logger.info(f"Video duration: {duration}s")
            return duration

        except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError, FileNotFoundError) as e:
            logger.error(f"Failed to get video duration: {e}")
            return 0.0

    @staticmethod
    def get_video_info(file_path: str) -> dict:
        """Get comprehensive video information using ffprobe.

        Args:
            file_path: Path to video file

        Returns:
            Dict with video metadata
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                logger.error(f"ffprobe failed: {result.stderr}")
                return {}

            data = json.loads(result.stdout)

            # Extract format info
            format_info = data.get('format', {})
            streams = data.get('streams', [])

            # Find video and audio streams
            video_stream = next((s for s in streams if s.get('codec_type') == 'video'), None)
            audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'), None)

            info = {
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'bit_rate': int(format_info.get('bit_rate', 0)),
                'format_name': format_info.get('format_name', ''),
                'has_video': video_stream is not None,
                'has_audio': audio_stream is not None,
            }

            if video_stream:
                info.update({
                    'width': int(video_stream.get('width', 0)),
                    'height': int(video_stream.get('height', 0)),
                    'video_codec': video_stream.get('codec_name', ''),
                    'frame_rate': eval(video_stream.get('r_frame_rate', '0/1')),  # Convert fraction
                })

            if audio_stream:
                info.update({
                    'audio_codec': audio_stream.get('codec_name', ''),
                    'sample_rate': int(audio_stream.get('sample_rate', 0)),
                    'channels': int(audio_stream.get('channels', 0)),
                })

            logger.info(f"Video info extracted: {info['duration']}s, {info['width']}x{info['height']}")
            return info

        except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError, FileNotFoundError) as e:
            logger.error(f"Failed to get video info: {e}")
            return {}

    @staticmethod
    def extract_gps_metadata(file_path: str) -> Optional[Tuple[float, float]]:
        """Extract GPS coordinates from video metadata.

        Args:
            file_path: Path to video file

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                file_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                return None

            data = json.loads(result.stdout)
            tags = data.get('format', {}).get('tags', {})

            # Look for GPS coordinates in various tag formats
            location_keys = [
                'location',          # QuickTime format
                'com.apple.quicktime.location.ISO6709',  # iOS format
                'location-ISO6709',  # Alternative format
                'GPS',
                'gps'
            ]

            for key in location_keys:
                location_data = tags.get(key)
                if location_data:
                    coords = VideoProcessor._parse_iso6709(location_data)
                    if coords:
                        logger.info(f"Extracted GPS coordinates: {coords}")
                        return coords

            logger.info("No GPS coordinates found in video metadata")
            return None

        except (subprocess.TimeoutExpired, json.JSONDecodeError, ValueError, FileNotFoundError) as e:
            logger.error(f"Failed to extract GPS metadata: {e}")
            return None

    @staticmethod
    def _parse_iso6709(location_string: str) -> Optional[Tuple[float, float]]:
        """Parse ISO 6709 location string format.

        Examples:
        - "+40.7589-073.9851+000.000/"
        - "+40.7589-073.9851/"
        - "40.7589,-73.9851"

        Args:
            location_string: ISO 6709 formatted location

        Returns:
            Tuple of (latitude, longitude) or None
        """
        try:
            # Remove trailing slash if present
            location_string = location_string.rstrip('/')

            # Handle ISO 6709 format with + and - signs
            if '+' in location_string or location_string.startswith('-'):
                # Split by + or - while preserving signs
                import re
                parts = re.findall(r'[+-][0-9.]+', location_string)

                if len(parts) >= 2:
                    lat = float(parts[0])
                    lon = float(parts[1])
                    return (lat, lon)

            # Handle simple comma-separated format
            elif ',' in location_string:
                parts = location_string.split(',')
                if len(parts) >= 2:
                    lat = float(parts[0].strip())
                    lon = float(parts[1].strip())
                    return (lat, lon)

            return None

        except (ValueError, IndexError) as e:
            logger.warning(f"Failed to parse location string '{location_string}': {e}")
            return None

    @staticmethod
    def validate_video_file(file_data: BinaryIO, max_duration: int = 60) -> dict:
        """Validate uploaded video file.

        Args:
            file_data: File-like object with video data
            max_duration: Maximum allowed duration in seconds

        Returns:
            Dict with validation results
        """
        validation_result = {
            'valid': False,
            'errors': [],
            'info': {}
        }

        try:
            # Save to temporary file for ffprobe
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                file_data.seek(0)
                temp_file.write(file_data.read())
                temp_file_path = temp_file.name

            try:
                # Get video info
                info = VideoProcessor.get_video_info(temp_file_path)
                validation_result['info'] = info

                if not info:
                    validation_result['errors'].append("Could not read video file")
                    return validation_result

                # Validate duration
                duration = info.get('duration', 0)
                if duration <= 0:
                    validation_result['errors'].append("Invalid video duration")
                elif duration > max_duration:
                    validation_result['errors'].append(f"Video too long ({duration}s > {max_duration}s)")

                # Validate format
                if not info.get('has_video'):
                    validation_result['errors'].append("No video stream found")

                # Check if file is reasonable size (not empty, not too large)
                size = info.get('size', 0)
                if size < 1000:  # Less than 1KB
                    validation_result['errors'].append("Video file too small")
                elif size > 100 * 1024 * 1024:  # More than 100MB
                    validation_result['errors'].append("Video file too large (>100MB)")

                # If no errors, mark as valid
                if not validation_result['errors']:
                    validation_result['valid'] = True
                    logger.info(f"Video validation passed: {duration}s, {size} bytes")

            finally:
                # Clean up temp file
                Path(temp_file_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Video validation error: {e}")
            validation_result['errors'].append(f"Validation error: {str(e)}")

        return validation_result


class MockVideoProcessor:
    """Mock video processor for development/testing."""

    @staticmethod
    def get_video_duration(file_path: str) -> float:
        """Mock video duration."""
        logger.info(f"🎭 Mock video duration for {file_path}: 15.0s")
        return 15.0

    @staticmethod
    def get_video_info(file_path: str) -> dict:
        """Mock video info."""
        info = {
            'duration': 15.0,
            'size': 2048000,  # 2MB
            'bit_rate': 1000000,
            'format_name': 'mov,mp4,m4a,3gp,3g2,mj2',
            'has_video': True,
            'has_audio': True,
            'width': 1920,
            'height': 1080,
            'video_codec': 'h264',
            'frame_rate': 30.0,
            'audio_codec': 'aac',
            'sample_rate': 44100,
            'channels': 2,
        }
        logger.info(f"🎭 Mock video info for {file_path}: {info}")
        return info

    @staticmethod
    def extract_gps_metadata(file_path: str) -> Optional[Tuple[float, float]]:
        """Mock GPS extraction."""
        # Return mock Brooklyn coordinates
        coords = (40.6782, -73.9442)
        logger.info(f"🎭 Mock GPS coordinates for {file_path}: {coords}")
        return coords

    @staticmethod
    def validate_video_file(file_data: BinaryIO, max_duration: int = 60) -> dict:
        """Mock video validation."""
        file_data.seek(0, 2)  # Seek to end
        file_size = file_data.tell()
        file_data.seek(0)  # Reset

        result = {
            'valid': True,
            'errors': [],
            'info': {
                'duration': 15.0,
                'size': file_size,
                'has_video': True,
                'has_audio': True,
                'width': 1920,
                'height': 1080,
            }
        }

        logger.info(f"🎭 Mock video validation: {result}")
        return result


def get_video_processor() -> VideoProcessor | MockVideoProcessor:
    """Get video processor (real or mock based on ffmpeg availability)."""
    try:
        # Test if ffmpeg is available
        subprocess.run(['ffprobe', '-version'], capture_output=True, timeout=5)
        logger.info("✅ ffmpeg detected, using real video processor")
        return VideoProcessor()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning("⚠️  ffmpeg not available, using mock video processor")
        return MockVideoProcessor()