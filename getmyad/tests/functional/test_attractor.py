from getmyad.tests import *

class TestAttractorController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='attractor', action='index'))
        # Test response...
