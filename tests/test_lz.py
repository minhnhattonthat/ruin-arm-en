import pytest

from lz import decompress


def test_distance_zero_requires_destination_memory():
    # The title loader actually consumes this form at $AF851C.
    stream = bytes.fromhex("04 00 01 41 00 00")
    with pytest.raises(ValueError, match="initial destination RAM"):
        decompress(stream)
    assert decompress(stream, initial=b"wxyz") == (b"Axyz", len(stream))


def test_overlapping_and_negative_back_references():
    assert decompress(bytes.fromhex("05 00 01 41 11 00"))[0] == b"AAAAA"
    assert decompress(bytes.fromhex("03 00 00 30 00"))[0] == b"\0\0\0"


def test_negative_counter_wrap_matches_65816():
    # pos 1 - distance $101 = -256: the hardware zero counter truncates
    # to $FF, exits after one byte, and resumes copying at output byte 0.
    assert decompress(bytes.fromhex("04 00 01 41 10 10"))[0] == b"A\0A\0"


def test_back_reference_position_uses_signed_16_bits():
    stream = bytes.fromhex("04 80") + (b"\xff" + b"A" * 8) * 4096 + bytes.fromhex("01 41 10 00")
    assert decompress(stream)[0] == b"A" * 32769 + b"\0AA"
