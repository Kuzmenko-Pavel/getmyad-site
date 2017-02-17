from getmyad.tests import *

class TestRegisterAdvController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='register_adv', action='index'))
        # Test response...
