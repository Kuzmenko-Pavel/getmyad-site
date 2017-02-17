# encoding: utf-8
import unittest
from getmyad.lib.admaker_validator import *


class TestAdmakerValidator(unittest.TestCase):

    def setUp(self):

        self.Description = {
            "borderColor": "ff6666",
            "fontUnderline": False,
            "fontBold": True,
            "hide": False,
            "top": "36",
            "height": "38px",
            "width": "130px",
            "fontSize": "10",
            "borderWidth": "0",
            "fontColor": "333333",
            "align": "center",
            "left": "72"
        }

        self.Image = {
            "borderColor": "6b6b78",
            "fontUnderline": False,
            "fontBold": False,
            "hide": False,
            "top": "3",
            "height": "68px",
            "width": "68px",
            "borderWidth": "0",
            "align": "center",
            "left": "3"
        }

        self.Header = {
            "borderColor": "666666",
            "fontUnderline": True,
            "fontBold": True,
            "hide": False,
            "top": "4",
            "height": "30px",
            "width": "130px",
            "fontSize": "12",
            "borderWidth": "0",
            "fontColor": "016BDB",
            "align": "center",
            "left": "71"
        }

        self.Cost = {
            "borderColor": "9f9feb",
            "fontUnderline": False,
            "fontBold": True,
            "hide": False,
            "top": "73",
            "height": "14px",
            "width": "75px",
            "fontSize": "12",
            "borderWidth": "0",
            "fontColor": "e60000",
            "align": "left",
            "left": "2"
        }

        self.Nav = {
            "logoHide": False,
            "color": "1a00ff",
            "logoColor": "color",
            "logoPosition": "bottom-right",
            "navPosition": "top-right",
            "backgroundColor": "a4c8ed"
        }

        self.Advertise = {
            "borderColor": "303030",
            "fontUnderline": False,
            "fontBold": False,
            "hide": False,
            "top": "0",
            "height": "100px",
            "width": "205px",
            "borderWidth": "0",
            "align": "center",
            "left": "0"
        }

        self.Main = {
            "borderColor": "e60000",
            "fontUnderline": False,
            "fontBold": False,
            "hide": False,
            "top": "0",
            "height": "88px",
            "width": "630px",
            "borderWidth": "1",
            "backgroundColor": "ffffcc",
            "itemsNumber": "3",
            "align": "center",
            "left": "0"
        }

        self.valid_options = {
            "Description": self.Description,
            "Image": self.Image,
            "Header": self.Header,
            "Cost": self.Cost,
            "Nav": self.Nav,
            "Advertise": self.Advertise,
            "Main": self.Main
        }

    def test_validate(self):
        # Параметры должны нормально пройти валидацию
        validated = validate_admaker(self.valid_options)

        # hoverColor должен был вычислиться
        self.assertEquals(validated['Nav']['hovercolor'], "5f64f6")

    def test_mix_colors(self):
        from getmyad.lib.admaker_validator import _mix_colors
        c1 = "486a00"
        c2 = "ffffff"
        self.assertEquals(_mix_colors(c1, c2), "a3b47f")

        

if __name__ == '__main__':
    unittest.main()
