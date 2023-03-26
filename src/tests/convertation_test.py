from convertation import check_input_file, check_output_path

def test_check_input_file():
    assert check_input_path("convertation_test.py")
    assert not check_input_path("convertation_test_python")

def test_check_output_path():
    assert not check_output_path("convertation_test.py")
    assert not check_output_path("convertation_test_python")
    assert check_output_path("./video.mp4")

