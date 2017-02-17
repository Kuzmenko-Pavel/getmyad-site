# -*- coding: utf-8 -*-
from pymongo import Connection
import json
import time
from datetime import datetime
import re





def advertise_to_css(opt, css):
    """
        конвертация и валидация выгрузки из параметров в ксс
        
    """
    try:
        res={"status":'ok',"css":css}
        html_re = re.compile(r"<.*?<.*?>")
        s_re = re.compile(r"<.*?")
        for el in opt:
            #res = res + "=>\n"
            for x in opt[el]:
                #log.info(str(x)+":"+str(opt[el][x])+"\n")
                #res = res + str(x)+":"+str(opt[el][x])+"\n"
                if re.match(html_re,str(opt[el][x])):
                    log.info(str(opt[el][x]))
                    res['status'] = 'fail'
                    res['css'] = str(res['css']) + str(opt[el][x])+"\n" 
                if re.match(s_re,str(opt[el][x])):
                    log.info(str(opt[el][x]))
                    res['status'] = 'fail'
                    res['css'] = str(res['css']) + str(opt[el][x])+"\n"                          
    except Exception, ex:
        res['status'] = 'fail'
        log.info(str(ex))
        res['css'] = ex        
    return res
    try:
        DescriptionWidth = str(opt['Description']['width'])
        DescriptionHeight = str(opt['Description']['height'])
        DescriptionBorderWidth = str(opt['Description']['borderWidth'])
        DescriptionBorderColor = str(opt['Description']['borderColor'])
        DescriptionFontUnderline = str(opt['Description']['fontUnderline'])
        DescriptionFontBold = str(opt['Description']['fontBold'])
        DescriptionFontFamily = str(opt['Description']['fontFamily'])
        DescriptionHide = str(opt['Description']['hide'])
        DescriptionTop = str(opt['Description']['top'])
        DescriptionAlign = ''#str(opt['Description']['align'])
        DescriptionLeft = str(opt['Description']['left'])
        #DescriptionBackgroundColor = str(opt['Description']['backgroundColor'])
        mainWidth = str(opt['Main']['width'])
        mainHeight = str(opt['Main']['height'])
        mainBorderWidth = str(opt['Main']['borderWidth'])
        mainBorderColor = str(opt['Main']['borderColor'])
        mainFontUnderline = str(opt['Main']['fontUnderline'])
        mainFontBold = str(opt['Main']['fontBold'])
        mainFontFamily = str(opt['Main']['fontFamily'])
        mainHide = str(opt['Main']['hide'])
        mainTop = str(opt['Main']['top'])
        mainBackgroundColor = str(opt['Main']['backgroundColor'])
        mainAlign = ''#str(opt['Main']['align'])
        mainLeft = str(opt['Main']['left'])
        #Image
        ImageWidth = str(opt['Image']['width'])
        ImageHeight = str(opt['Image']['height'])
        ImageBorderWidth = str(opt['Image']['borderWidth'])
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
        HeaderFontFamily = str(opt['Header']['fontFamily'])
        HeaderHide = str(opt['Header']['hide'])
        HeaderTop = str(opt['Header']['top'])
        try:                    
            HeaderAlign = str(opt['Header']['align'])            
        except:
            HeaderAlign = 'center'
        HeaderLeft = str(opt['Header']['left'])
        #cost
        CostWidth = str(opt['Cost']['width'])
        CostHeight = str(opt['Cost']['height'])
        CostBorderWidth = str(opt['Cost']['borderWidth'])
        CostBorderColor = str(opt['Cost']['borderColor'])
        CostFontUnderline = str(opt['Cost']['fontUnderline'])
        CostFontBold = str(opt['Cost']['fontBold'])
        CostFontFamily = str(opt['Cost']['fontFamily'])
        CostHide = str(opt['Cost']['hide'])
        CostTop = str(opt['Cost']['top'])
        CostAlign = ''#str(opt['Cost']['align'])
        CostLeft = str(opt['Cost']['left'])
        #Nav 
        NavColor = str(opt['Nav']['color'])
        NavLogoPosition = str(opt['Nav']['logoPosition'])
        NavLogoColor = str(opt['Nav']['logoColor'])
        NavColor = str(opt['Nav']['color'])
        NavPosition = str(opt['Nav']['navPosition'])
        NavBackgroundColor = str(opt['Nav']['backgroundColor'])
        
         
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
        """ %(            
            mainWidth, 
            mainHeight, 
            mainBorderWidth,
            mainBorderColor,
            mainBackgroundColor,
            )
        
        css = css + u"""
.advBlock {
    width: 240px;
    height: 114px;
    border: 0px solid #303030;
    float: left;
    position: relative;
    font-family: %s
    color: #;
    overflow: hidden;
}"""%(HeaderFontFamily)
    
        css = css + u"""
.advHeader {
    position: absolute;
    top: %spx;
    left:%spx;
    width: %s;
    height:%s;
    border:  %spx solid %s;
    overflow: hidden;
    text-align: %s;

    }"""%(              
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
    color: #ffffff;
    font-size: 12px;
    font-weight: bold;
}

.advHeader:hover {
    text-decoration: underline;
}


.advDescription {
    position: absolute;
    top: %spx;
    left: %spx;
    width: %s;
    height: %s;
    border:  %spx solid %s;
    overflow: hidden;        
    text-align: %s;
}

.advDescription, .advDescription:hover, .advDescription:visited, .advDescription:active, .advDescription:link {
    text-decoration: none;
    color: #f2f2f2;
    font-size: 11px;
    font-family:%s
}

.advDescription:hover {
    text-decoration: underline;
}
    """%(
        DescriptionTop, 
        DescriptionLeft, 
        DescriptionWidth, 
        DescriptionHeight,        
        DescriptionBorderWidth,
        DescriptionBorderColor,      
        DescriptionAlign,
        DescriptionFontFamily)        
        css = css + u"""
.advCost {
    position: absolute;
    top: %spx;
    left: %spx;
    width: %spx;
    height: %spx;
    border: %spx solid %s;
    overflow: hidden;
    text-align: %s
}

.advCost, .advCost:link, .advCost:hover, .advCost:visited, .advCost:active {
    text-decoration: none;
    color: #f4ff9e;
    font-size: 13px;
    font-family:%s;
    font-weight: bold;
}

.advCost:hover {
    text-decoration: underline;
}"""%(
              CostTop, 
            CostLeft, 
            CostWidth, 
            CostHeight,        
            CostBorderWidth,
            CostBorderColor,      
            CostAlign,
            CostFontFamily
          )
        css = css + u"""
.advImage {
    position: absolute;
    width: %s
    height: %s
    top: %s
    left: %s
    border: %s solid %s
}
    """ %(
        ImageWidth, 
        ImageHeight,        
        ImageTop, 
        ImageLeft, 
        ImageBorderWidth,
        ImageBorderColor    
        )
        #return NavPosition
        NavLeft = ""
        NavBottom = ""
        NavRight = ""
        if NavPosition == "top-right":  
            NavTop = "5px;"
            NavRight = "2px;"
        elif NavPosition == "top-left": 
            NavTop = "1px;"
            NavLeft = "14px;"
        elif NavPosition == "bottom-left": 
            NavBottom = "1px;"
            NavLeft = "14px;"
        elif NavPosition == "bottom-right":
            NavBottom = "5px;"
            NavRight = "5px;"
        
        css = css + u"""
.nav {    
    position: absolute;
    width: 11px;
    height: 16px;
    
    bottom: %s;
    left:%s;
    right:%s
}""" %(
               NavBottom,
               NavLeft,
               NavRight
               )  
        css = css + u"""
.nav a, .nav a:hover, .nav a:link, .nav a:visited, .nav a:active {    
    text-decoration: none;
    /*color: %s*/
    /*background-color: %s*/
    font-family: Arial, "Helvetica CY", "Nimbus Sans L", sans-serif;;
    display: block;
    /*border: 1px solid #000;*/
    width: 11px;    
}"""%(
            NavColor,        
            NavBackgroundColor
          )
        
        css = css + u"""
.navr {    
    position: absolute;
    width: 11px;
    height: 16px; 
    bottom: %s;
    left:%s;
    right:%s
}"""% (
       NavBottom,
       NavLeft,
       NavRight
       )
        css = css + u"""
.navr a, .nav a:hover, .navr a:link, .navr a:visited, .navr a:active {
    font-size: 15px;
    text-decoration: none;
    font-family: Arial, "Helvetica CY", "Nimbus Sans L", sans-serif;
    display: block;
    width: 11px;    
}

#adInfo {
    position: absolute;
    bottom: 0;
    right: 1px;
    background-repeat: no-repeat;
    overflow:hidden;
    background-image: url('http://getmyad.yottos.com/Image/Logos/yot/whiteLogo.png');
    height: 10px;
    width: 45px;
}    
        """
        
        css = css + """
#adInfo a {
width:100%;
height:100%;
display: block;

}

.a {position: absolute; overflow-x: hidden; overflow-y: hidden; width: 1px; height: 1px;background-color:#ffffff;}
.a1 {position: absolute; overflow-x: hidden; overflow-y: hidden; width: 1px; height: 1px;background-color:#000000;}
.a2 {position: absolute; overflow-x: hidden; overflow-y: hidden; width: 1px; height: 1px;background-color:#000000;}
.b {position: absolute; overflow-x: hidden; overflow-y: hidden; width: 1px; height: 1px;background-color:#ffffff;}
.b1 {position: absolute; overflow-x: hidden; overflow-y: hidden; width: 1px; height: 1px;background-color:#000000;}
.b2 {position: absolute; overflow-x: hidden; overflow-y: hidden; width: 1px; height: 1px;background-color:#000000;}

</style>
         """
    except Exception, ex:
        log.info(ex)
        return False
    return css







def adoptions_to_css(opt, css):
    u"""
        конвертация и валидация выгрузки из параметров в ксс
        upd: передал попроще, но нужно сделать как раньше, только учитывать, что не все параметры передаются пользователей, т.е. нужно подпрвить admaker
    """
    try:
        
        s_path = "background-image: url('http://cdnt.yottos.com/getmyad/logos/yot/"
        f_path = "background-image: url('http://cdnt.yottos.com/getmyad/logos/"
        if opt['Main']['width']<200:
            if css.find(s_path)<1:
                if css.find(f_path)>0:
                    css.replace(f_path,s_path)
        res={"status":'ok',"css":css}
        
        html_re = re.compile(r"<.*?<.*?>")
        s_re = re.compile(r"<")
        size_re = re.compile(r"[0-9]{3,}?px")
        cl_re = re.compile(r"color")
        color_re = re.compile(r"/^#?([a-f0-9]{6}|[a-f0-9]{3})$/")
        for el in opt:
            #res = res + "=>\n"
            for x in opt[el]:
                #log.info(str(x)+":"+str(opt[el][x])+"\n")
                #res = res + str(x)+":"+str(opt[el][x])+"\n"
                if re.match(html_re,str(opt[el][x])):
                    print (str(opt[el][x]))
                    res['status'] = 'fail'
                    res['css'] = str(res['css']) + str(opt[el][x])+"\n" 
                    break;
                if re.match(s_re,str(opt[el][x])):
                    print (str(opt[el][x]))
                    res['status'] = 'fail'
                    res['css'] = str(res['css']) + str(opt[el][x])+"\n"
                    break;
                if x == u"top" or x == u"left" or x == u"width" or x == u"height":
                    if not re.match(size_re,str(opt[el][x])):
                        print (str(opt[el][x]))
                        res['status'] = 'fail'
                        res['css'] = str(res['css']) + str(opt[el][x])+u"\n"
                        break;
                if re.match(cl_re,str(x)):
                    if not re.match(color_re,str(opt[el][x])):
                        print (str(opt[el][x]))
                        res['status'] = 'fail'
                        res['css'] = str(res['css']) + str(opt[el][x])+u"\n"
                        break;                    
    except Exception, ex:
        res['status'] = 'fail'
        print (str(ex))
        res['css'] = ex        
    return res

def read_advertise():
    conn = Connection()       
    db = conn.getmyad_db
    for adv in db.Advertise.find():#_one()#['admaker']
        css = advertise_to_css(adv['admaker'],adv['css'])
        if
    #css = adoptions_to_css(x['admaker'],x['css'])
    print css
    pass


read_advertise()