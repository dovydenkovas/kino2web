from convertation import check_input_path, check_output_path
import sys
sys.path.append("src")
import os


def test_check_input_file():
    assert not check_input_path("src/convertation_test.py")
    assert not check_input_path("convertation_test_python")
    assert check_input_path("tests/video.mkv")

def test_check_output_path():
    assert not check_output_path("src/convertation_test.py")
    assert not check_output_path("convertation_test_python")
    assert check_output_path("./video.mp4")

