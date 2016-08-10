import unittest
from ratcave.wavefront import WavefrontReader


class TestWavefrontReader(unittest.TestCase):
    """
    Run tests from main project folder.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_mtl(self):
        self.reader = WavefrontReader('ratcave/assets/primitives')

        assert(len(self.reader.materials) == 1)
