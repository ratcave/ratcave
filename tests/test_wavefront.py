import unittest
from ratcave.wavefront import WavefrontReader
from ratcave import resources
from os import path

class TestWavefrontReader(unittest.TestCase):
    """
    Run tests from main project folder.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_mtl(self):
        self.reader = WavefrontReader(path.join(resources.resource_path, 'primitives'))

        assert(len(self.reader.materials) == 1)
