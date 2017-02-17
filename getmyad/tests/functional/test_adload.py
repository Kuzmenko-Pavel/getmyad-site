from getmyad.tests import *

class TestAdloadController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='adload', action='index'))
        # Test response...
