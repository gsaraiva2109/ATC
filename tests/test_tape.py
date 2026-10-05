from tm import Tape


def test_blank_by_default():
    tape = Tape("B")
    assert tape.read() == "B"
    assert tape.window() == ("B", 0)
    assert tape.content() == ""


def test_load_places_word_at_origin():
    tape = Tape("B")
    tape.load("abc")
    assert tape.head == 0
    assert tape.read() == "a"
    assert tape.window() == ("abc", 0)
    assert tape.content() == "abc"


def test_grows_to_the_left_and_right():
    tape = Tape("B")
    tape.load("a")
    tape.move("L")
    tape.write("x")
    tape.move("L")
    tape.move("L")
    tape.write("y")
    for _ in range(5):
        tape.move("R")
    tape.write("z")
    assert tape.content() == "yBxaBz"
    assert tape.window() == ("yBxaBz", 5)


def test_writing_blank_frees_the_cell():
    tape = Tape("B")
    tape.load("ab")
    assert len(tape) == 2
    tape.write("B")
    assert len(tape) == 1
    assert tape.content() == "b"


def test_stay_does_not_move():
    tape = Tape("B")
    tape.load("a")
    tape.move("S")
    assert tape.head == 0


def test_window_includes_head_outside_content():
    tape = Tape("B")
    tape.load("ab")
    for _ in range(4):
        tape.move("R")
    assert tape.window() == ("abBBB", 4)
    for _ in range(7):
        tape.move("L")
    assert tape.window() == ("BBBab", 0)


def test_far_travel_keeps_memory_constant():
    tape = Tape("B")
    tape.load("a")
    for _ in range(100_000):
        tape.move("L")
    assert len(tape) == 1


def test_invalid_direction():
    import pytest

    with pytest.raises(ValueError):
        Tape("B").move("X")
