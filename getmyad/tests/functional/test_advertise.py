from getmyad.tests import *

class TestAdvertiseController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='advertise', action='index'))
        # Test response...
