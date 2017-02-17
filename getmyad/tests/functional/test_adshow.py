from getmyad.tests import *

class TestAdshowController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='adshow', action='index'))
        # Test response...
