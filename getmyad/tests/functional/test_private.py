from getmyad.tests import *

class TestPrivateController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='private', action='index'))
        # Test response...
