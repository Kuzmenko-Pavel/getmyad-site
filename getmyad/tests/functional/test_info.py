from getmyad.tests import *

class TestInfoController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='info', action='index'))
        # Test response...
