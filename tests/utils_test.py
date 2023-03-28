from utils import file_of_format, print_exeption
import sys
import os

sys.path.append("src")

def test_file_of_format():
    assert file_of_format("avi.mp4", {"mkv", "mp4"})
    assert not file_of_format("mp4.mkv", {"mp4", "avi"})

def test_print_exeption():
    os.environ["DEBUG"] = "True"
    @print_exeption
    def foo():
        return 0/0

    try:
        foo()
        assert True
    except:
        assert False

