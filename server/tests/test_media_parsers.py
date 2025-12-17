import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from app.parsers import extract_text_auto
from app.parsers.image_parser import ImageParser
from app.parsers.audio_parser import AudioParser
from app.parsers.video_parser import VideoParser

@pytest.fixture
def mock_whisper():
    with patch("app.parsers.audio_parser.whisper") as mock:
        model = MagicMock()
        model.transcribe.return_value = {"text": "Transcribed text"}
        mock.load_model.return_value = model
        yield mock

@pytest.fixture
def mock_pytesseract():
    with patch("app.parsers.image_parser.pytesseract") as mock:
        mock.image_to_string.return_value = "OCR Text"
        yield mock

@pytest.fixture
def mock_pil():
    with patch("app.parsers.image_parser.Image") as mock:
        yield mock

@pytest.fixture
def mock_moviepy():
    with patch("app.parsers.video_parser.VideoFileClip") as mock:
        video_mock = MagicMock()
        video_mock.audio = MagicMock()
        mock.return_value = video_mock
        yield mock

def test_image_parser_integration(tmp_path, mock_pytesseract, mock_pil):
    p = tmp_path / "test.jpg"
    p.touch()
    
    # Direct parser usage
    parser = ImageParser()
    text = parser.parse(p)
    assert text == "OCR Text"
    
    # Auto usage
    text_auto = extract_text_auto(p)
    assert text_auto == "OCR Text"

def test_audio_parser_integration(tmp_path, mock_whisper):
    p = tmp_path / "test.mp3"
    p.touch()
    
    parser = AudioParser()
    text = parser.parse(p)
    assert text == "Transcribed text"

def test_video_parser_integration(tmp_path, mock_moviepy, mock_whisper):
    p = tmp_path / "test.mp4"
    p.touch()
    
    parser = VideoParser()
    text = parser.parse(p)
    assert text == "Transcribed text"
