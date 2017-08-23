# -*- coding: utf-8 -*-
import re
from pymongo import Connection


def dec2hex(i):
    return baseconvert(i, BASE10, BASE16)

def hex2dec(i):
    return baseconvert(i, BASE16, BASE10)

def rgb(r , g , b):
    try:
        if len(str(r)) == 1:
            r = str(r) + '0'
        if len(str(g)) == 1:
            g = str(g) + '0'
        if len(str(b)) == 1:
            b = str(b) + '0'                
        return dec2hex(int(r)) + dec2hex(int(g)) + dec2hex(int(b))
    except Exception, ex:
        print "string 23"
        print ex
        exit(1)

BASE2 = "01"
#BASE8 = "01234567"
BASE10 = "0123456789"
BASE16 = "0123456789ABCDEF"
#BASE62 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz"

def baseconvert(number, fromdigits, todigits):

    if str(number)[0] == '-':
        number = str(number)[1:]
        neg = 1
    else:
        neg = 0

    # make an integer out of the number
    x = long(0)
    for digit in str(number):
        x = x * len(fromdigits) + fromdigits.index(digit)
    
    # create the result in base 'len(todigits)'
    res = ""
    while x > 0:
        digit = x % len(todigits)
        res = todigits[digit] + res
        x /= len(todigits)
    if neg:
        res = "-" + res

    return res


def adv_to_css(opt):
    u"""
    Создает строку CSS из параметров Admaker
    """

    try:
        DescriptionHide = ""                
        if  str(opt['Description']['hide']) == 'True':
            print "%s" % (str(opt['Description']['hide']))
            DescriptionHide = "\n\tdisplay: none;"
        DescriptionWidth = str(opt['Description']['width'])        
        DescriptionHeight = str(opt['Description']['height'])
        DescriptionBorderWidth = str(opt['Description']['borderWidth'])
        DescriptionBorderColor = str(opt['Description']['borderColor'])
        DescriptionFontUnderline = str(opt['Description']['fontUnderline'])
        DescriptionFontBold = str(opt['Description']['fontBold'])
        DescriptionFontColor = str(opt['Description']['fontColor'])
        try:
            DescriptionFontSize = str(opt['Description']['fontSize'])            
        except:
            DescriptionFontSize = "10"
        try:
            DescriptionFontFamily = str(opt['Description']['fontFamily'])
        except:
            DescriptionFontFamily = 'Arial, "Helvetica CY",  sans-serif;'
        #DescriptionHide = str(opt['Description']['hide'])
        DescriptionTop = str(opt['Description']['top'])
        try:
            DescriptionAlign = str(opt['Description']['align'])
        except:
            DescriptionAlign = 'center'
        DescriptionLeft = str(opt['Description']['left'])
        #DescriptionBackgroundColor = str(opt['Description']['backgroundColor'])
        mainWidth = str(opt['Main']['width'])
        mainHeight = str(opt['Main']['height'])
        mainBorderWidth = str(opt['Main']['borderWidth'])
        mainBorderColor = str(opt['Main']['borderColor'])
        mainFontUnderline = str(opt['Main']['fontUnderline'])
        mainFontBold = str(opt['Main']['fontBold'])
        try:
            mainFontFamily = str(opt['Main']['fontFamily'])
        except:
            mainFontFamily = 'Arial, "Helvetica CY",  sans-serif;'
        mainHide = str(opt['Main']['hide'])
        mainTop = str(opt['Main']['top'])
        mainBackgroundColor = str(opt['Main']['backgroundColor'])
        try:
            mainAlign = str(opt['Main']['align'])
        except:
            mainAlign = 'center'
        mainLeft = str(opt['Main']['left'])
        #Image
        ImageWidth = str(opt['Image']['width'])
        ImageHeight = str(opt['Image']['height'])
        ImageBorderWidth = str(opt['Image']['borderWidth']) or "0"
        ImageBorderColor = str(opt['Image']['borderColor'])
        ImageFontUnderline = str(opt['Image']['fontUnderline'])
        ImageFontBold = str(opt['Image']['fontBold'])
        #ImageFontFamily = str(opt['Image']['fontFamily'])
        ImageHide = str(opt['Image']['hide'])
        ImageTop = str(opt['Image']['top'])
        #ImageBackgroundColor = str(opt['Image']['backgroundColor'])
        #ImageAlign = str(opt['Image']['align'])
        ImageLeft = str(opt['Image']['left'])
        #Header
        HeaderWidth = str(opt['Header']['width'])
        HeaderHeight = str(opt['Header']['height'])
        HeaderBorderWidth = str(opt['Header']['borderWidth'])
        HeaderBorderColor = str(opt['Header']['borderColor'])
        HeaderFontUnderline = str(opt['Header']['fontUnderline'])
        HeaderFontBold = str(opt['Header']['fontBold'])
        try:
            HeaderFontColor = str(opt['Header']['fontColor'])
        except:
            HeaderFontColor = "7777CC"
        try:
            HeaderFontSize = str(opt['Header']['fontSize'])
        except:
            HeaderFontSize = "10"
        try:
            HeaderFontFamily = str(opt['Header']['fontFamily'])
        except:
            HeaderFontFamily = 'Arial, "Helvetica CY",  sans-serif;'
        HeaderHide = str(opt['Header']['hide'])
        HeaderTop = str(opt['Header']['top'])
        try:                    
            HeaderAlign = str(opt['Header']['align'])            
        except:
            HeaderAlign = 'center'
        HeaderLeft = str(opt['Header']['left'])
        #cost
        CostWidth = str(opt['Cost']['width'])
        CostHide = ""
        if str(opt['Cost']['hide']) == 'True':
            CostHide = "\n\tdisplay: none;"
        CostHeight = str(opt['Cost']['height'])
        CostBorderWidth = str(opt['Cost']['borderWidth'])
        CostBorderColor = str(opt['Cost']['borderColor'])
        CostFontUnderline = str(opt['Cost']['fontUnderline'])
        CostFontBold = str(opt['Cost']['fontBold'])
        CostFontColor = str(opt['Cost']['fontColor'])
        try:
            CostFontSize = str(opt['Cost']['fontSize'])
        except:
            CostFontSize = "13" 
        try:
            CostFontFamily = str(opt['Cost']['fontFamily'])
        except:
            CostFontFamily = 'Arial, "Helvetica CY",  sans-serif;'        
        CostTop = str(opt['Cost']['top'])
        try:
            CostAlign = str(opt['Cost']['align'])
        except:
            CostAlign = 'center'
        CostLeft = str(opt['Cost']['left'])
        #Nav 
        NavColor = str(opt['Nav']['color'])
        NavLogoPosition = str(opt['Nav']['logoPosition'])
        NavLogoColor = str(opt['Nav']['logoColor'])
        NavColor = str(opt['Nav']['color'])
        NavPosition = str(opt['Nav']['navPosition'])
        NavBackgroundColor = str(opt['Nav']['backgroundColor'])
        #
        advWidth = str(opt['Advertise']['width'])                
        advHeight = str(opt['Advertise']['height'])
        advBorderWidth = str(opt['Advertise']['borderWidth'])
        advBorderColor = str(opt['Advertise']['borderColor'])
        advFontUnderline = str(opt['Advertise']['fontUnderline'])
        advFontBold = str(opt['Advertise']['fontBold'])
        try:
            advFontFamily = str(opt['Advertise']['fontFamily'])
        except:
            advFontFamily = 'Arial, "Helvetica CY",  sans-serif;'
        advHide = str(opt['Advertise']['hide'])
        advTop = str(opt['Advertise']['top'])
        try: 
            advAlign = str(opt['Advertise']['align'])
        except:
            advAlign = 'center'
        advLeft = str(opt['Advertise']['left'])
        
         
        css = u"""
<style type="text/css">
#mainContainer {
    position: relative;
    width: %s;
    height: %s;
    border: %spx solid #%s;
    background-color: #%s;
    overflow: hidden;
    border-radius: 5px;
}
        """ % (
            mainWidth,
            mainHeight,
            mainBorderWidth,
            mainBorderColor,
            mainBackgroundColor,
            )
        
        css = css + u"""
.advBlock {
    width: %s;
    height: %s;
    border: %spx solid #%s;
    float: left;
    position: relative;
    font-family: %s
    color: #;
    overflow: hidden;
}""" % (
      advWidth,
      advHeight,
      advBorderWidth,
      advBorderColor,
      advFontFamily
      )
    
        css = css + u"""
.advHeader {
    position: absolute;
    top: %spx;
    left:%spx;
    width: %s;
    height:%s;
    border:  %spx solid #%s;
    overflow: hidden;
    text-align: %s;

    }""" % (
              HeaderTop,
              HeaderLeft,
              HeaderWidth,
              HeaderHeight,
              HeaderBorderWidth,
              HeaderBorderColor,
              HeaderAlign                         
        )
        
        css = css + u"""
.advHeader, .advHeader:hover, .advHeader:visited, .advHeader:active, .advHeader:link {
    text-decoration: none;
    color: #%s;
    font-size: %spx;
    font-weight: bold;
}""" % (HeaderFontColor,
      HeaderFontSize
      )


        css = css + u"""
.advHeader:hover {
    text-decoration: underline;
}


.advDescription {
    position: absolute;
    top: %spx;
    left: %spx;
    width: %s;
    height: %s;
    border:  %spx solid #%s;
    overflow: hidden;        
    text-align: %s;%s
}""" % (
        DescriptionTop,
        DescriptionLeft,
        DescriptionWidth,
        DescriptionHeight,
        DescriptionBorderWidth,
        DescriptionBorderColor,
        DescriptionAlign,
        DescriptionHide
       )
        
        css = css + u"""
.advDescription, .advDescription:hover, .advDescription:visited, .advDescription:active, .advDescription:link {
    text-decoration: none;
    color: #%s;
    font-size: %spx;
    font-family:%s
}""" % (
      DescriptionFontColor,
      DescriptionFontSize,
      DescriptionFontFamily
     )
        css = css + u"""        
.advDescription:hover {
    text-decoration: underline;
}
    """
        css = css + u"""
.advCost {
    position: absolute;
    top: %spx;
    left: %spx;
    width: %s;
    height: %s;
    border: %spx solid #%s;
    overflow: hidden;
    text-align: %s;
}

.advCost, .advCost:link, .advCost:hover, .advCost:visited, .advCost:active {
    text-decoration: none;
    color: #%s;
    font-size: %spx;
    font-family:%s;
    font-weight: bold;%s
}

.advCost:hover {
    text-decoration: underline;
}""" % (
              CostTop,
            CostLeft,
            CostWidth,
            CostHeight,
            CostBorderWidth,
            CostBorderColor,
            CostAlign,
            CostFontColor,
            CostFontSize,
            CostFontFamily,
            CostHide
          )
        css = css + u"""
.advImage {
    position: absolute;
    width: %s;
    height: %s;
    top: %spx;
    left: %spx;
    border: %spx solid #%s;
}
    """ % (
        ImageWidth,
        ImageHeight,
        ImageTop,
        ImageLeft,
        ImageBorderWidth,
        ImageBorderColor    
        )
        #return NavPosition
        NavTop = ""        
        NavLeft = ""
        NavBottom = ""
        NavRight = ""        
        NavLeftR = ""        
        NavRightR = ""
        if NavPosition == "top-right":  
            NavTop = "top: 5px;"
            NavRight = "right: 2px;"            
            NavRightR = "right: 16px;"
        if NavPosition == "top-left": 
            NavTop = "top: 1px;"
            NavLeft = "left: 14px;"
            NavLeftR = "left: 1px;"
        if NavPosition == "bottom-left": 
            NavBottom = "bottom: 1px;"
            NavLeft = "left: 14px;"
            NavLeftR = "left: 1px;"
        if NavPosition == "bottom-right":
            NavBottom = "bottom: 5px;"
            NavRight = "right: 5px;"
            NavRightR = "right: 18px;"
        
        css = css + u"""
.nav {
    cursor:pointer;  
    position: absolute;
    width: 11px;
    height: 16px;
    %s
    %s
    %s
    %s
}""" % (
        NavTop,
        NavBottom,
        NavLeft,
        NavRight
               )  
        css = css + u"""
.nav a, .nav a:hover, .nav a:link, .nav a:visited, .nav a:active {    
    text-decoration: none;    
    font-family: Arial, "Helvetica CY", "Nimbus Sans L", sans-serif;
    display: block;
    height: 16px; 
    width: 12px;    
}"""
        
        css = css + u"""
.navr {  
    cursor:pointer;  
    position: absolute;
    width: 11px;
    height: 16px; 
    %s
    %s
    %s
    %s
}""" % (
        NavTop,
        NavBottom,
        NavLeftR,
        NavRightR
           )
        css = css + u"""
.navr a, .nav a:hover, .navr a:link, .navr a:visited, .navr a:active {    
    text-decoration: none;
    font-family: Arial, "Helvetica CY", "Nimbus Sans L", sans-serif;
    display: block;
    height: 16px; 
    width: 12px;    
}"""
        if opt['Nav']["logoColor"] == "color":
            logo = "colorLogo.gif');"
        if opt['Nav']["logoColor"] == "blue":
            logo = "blueLogo.gif');"
        if opt['Nav']["logoColor"] == "black":
            logo = "blackLogo.gif');"
        if opt['Nav']["logoColor"] == "white":
            logo = "whiteLogo.gif');"
        
        try:
            mainwidth = int(re.findall('(\d+)', opt['Main']['width'])[0])
        except (IndexError):
            mainwidth = 200  
      
        if mainwidth < 200:           
            path = "background-image: url('http://cdn.yottos.com/logos/yot/"
            logoW = "45"
        else:            
            path = "background-image: url('http://cdn.yottos.com/logos/"
            logoW = "100"
            
        if NavLogoPosition == "top-right":  
            adInfo = "top: 3px;\nright: 1px;"
                                   
        if NavLogoPosition == "top-left": 
            adInfo = "top: 3px;\nleft: 1px;"  
                     
        if NavLogoPosition == "bottom-left": 
            adInfo = "bottom: 5px;\nleft: 0px;"
                       
        if NavLogoPosition == "bottom-right":
            adInfo = "bottom: 0px;\nright: 1px;"
            
        if opt['Nav'].get('logoHide'):
            adInfo += "\ndisplay: none;\n"
           
        css = css + """
#adInfo {
    position: absolute;
    %s
    background-repeat: no-repeat;
    overflow:hidden;
    %s
    height: 10px;
    width: %spx;
}    
        """ % (adInfo, path + logo, logoW)
        
        try:
            if NavBackgroundColor == 'red':
                NavBackgroundColor = 'FF0000'
            if len(NavBackgroundColor) < 1:
                NavBackgroundColor = '000000'
            if len(NavColor) >= 6:                
                xclr = {'r':int(NavColor[0:2], 16), 'g':int(NavColor[2:4], 16), 'b':int(NavColor[4:6], 16)}
            else: 
                xclr = {'r':int(NavColor[0:1], 16), 'g':int(NavColor[1:2], 16), 'b':int(NavColor[2:3], 16)}
            if len(NavBackgroundColor) >= 6:                
                yclr = {'r':int(NavBackgroundColor[0:2], 16), 'g':int(NavBackgroundColor[2:4], 16), 'b':int(NavBackgroundColor[4:6], 16)}
            else:
                yclr = {'r':int(NavBackgroundColor[0:1], 16), 'g':int(NavBackgroundColor[1:2], 16), 'b':int(NavBackgroundColor[2:3], 16)}

            cr = 1.5
            cg = 1.5
            cb = 1.5
            

            r = int((xclr['r'] + yclr['r']) / cr)
            g = int((xclr['g'] + yclr['g']) / cg)
            b = int((xclr['b'] + yclr['b']) / cb)
            if r > 255:                
                r = int((xclr['r'] + yclr['r']) / 2.2)
            if g > 255:
                g = int((xclr['g'] + yclr['g']) / 2.2)
            if b > 255:
                b = int((xclr['b'] + yclr['b']) / 2.2)
            hoverColor = rgb(r, g, b)
                                                           
        except Exception, ex:
            print "string 460"
            print ex                 
         
            return False
            #exit(1)

        css = css + """
#adInfo a {
width:100%;
height:100%;
display: block;

}"""
        css = css + """
.c {position: absolute; overflow-x: hidden; overflow-y: hidden; width: 1px; height: 1px;background-color:#%s;}
.c1 {position: absolute; overflow-x: hidden; overflow-y: hidden; width: 1px; height: 1px;background-color:#%s;}
.c2 {position: absolute; overflow-x: hidden; overflow-y: hidden; width: 1px; height: 1px;background-color:#%s;}
.b {position: absolute; overflow-x: hidden; overflow-y: hidden; width: 1px; height: 1px;background-color:#%s;}
.b1 {position: absolute; overflow-x: hidden; overflow-y: hidden; width: 1px; height: 1px;background-color:#%s;}
.b2 {position: absolute; overflow-x: hidden; overflow-y: hidden; width: 1px; height: 1px;background-color:#%s;}

</style>
         """ % (
              NavColor,
              NavBackgroundColor,
              hoverColor,
              NavColor,
              NavBackgroundColor,
              hoverColor
              )
         
    except Exception, ex:
        print "Error: %s" % (ex)
        return False   
    return css



def read_db():
    db = Connection().getmyad_db
    k = 0;
    count = 0;
    #9E5D6900-9BD7-11DF-842A-0015175ECAD8
    #    for adv in db.informer.find({'guid':'118d5bb5-1002-4273-9cfe-20b12afc4e64'}):        
#    for adv in db.informer.find({'guid':'fb10dd26-c65c-11df-ab31-00163e0300c1'}):
    for adv in db.informer.find():#({'guid':'8946DB8F-8A85-11DF-96C5-0015175ECAD8'}):
                     
        try:
            css = adv_to_css(adv['admaker'])
            if css == False:
                print adv['guid']
                #exit(10)
            db.informer.update({'guid': adv['guid']},
                                {'$set': {'css': css}},
                                upsert=True)
        except Exception, ex:
            print str(ex) + "\n"
            #print css
            k = k + 1
            print 
            exit(1)
        count = count + 1          
    print "\n\n Errors:" + str(k)
    print "\n\n Count:" + str(count)

read_db()
