function switch_css(value) {
	var block = $(".block");
	var block0 = $(".block0");
	var block1 = $(".block1");
	var block2 = $(".block2");
	var head = $(".head");
	var head0 = $(".head0");
	var head1 = $(".head1");
	var head2 = $(".head2");
	var desc = $(".desc");
	var desc0 = $(".desc0");
	var desc1 = $(".desc1");
	var desc2 = $(".desc2");
	var cost = $(".cost");
	var cost0 = $(".cost0");
	var cost1 = $(".cost1");
	var cost2 = $(".cost2");
	var img = $(".img");
	var img0 = $(".img0");
	var img1 = $(".img1");
	var img2 = $(".img2");
	var imgc = $(".imgc");
	var imgc0 = $(".imgc0");
	var imgc1 = $(".imgc1");
	var imgc2 = $(".imgc2");
	var button = $(".button");
	var button0 = $(".button0");
	var button1 = $(".button1");
	var button2 = $(".button2");
	var buttonc = $(".buttonc");
	var buttonc0 = $(".buttonc0");
	var buttonc1 = $(".buttonc1");
	var buttonc2 = $(".buttonc2");
    switch (value) {
        case "0":
            block.removeClass("advRetBlock");
            block.removeClass("advRecBlock");
            block.addClass("advBlock");
            head.removeClass("advRetHeader");
            head.removeClass("advRecHeader");
            head.addClass("advHeader");
            desc.removeClass("advRetDescription");
            desc.removeClass("advRecDescription");
            desc.addClass("advDescription");
            cost.removeClass("advRetCost");
            cost.removeClass("advRecCost");
            cost.addClass("advCost");
            img.removeClass("advRetImageS");
            img.removeClass("advRecImageS");
            img.addClass("advImageS");
            imgc.removeClass("advRetImageConS");
            imgc.removeClass("advRecImageConS");
            imgc.addClass("advImageConS");
            button.removeClass("advRetButton");
            button.removeClass("advRecButton");
            button.addClass("advButton");
            buttonc.removeClass("advRetButtonCon");
           	buttonc.removeClass("advRecButtonCon");
            buttonc.addClass("advButtonCon");
            break;
        case "1":
            block.removeClass("advBlock");
            block.removeClass("advRecBlock");
            block.addClass("advRetBlock");
            head.removeClass("advHeader");
            head.removeClass("advRecHeader");
            head.addClass("advRetHeader");
            desc.removeClass("advDescription");
            desc.removeClass("advRecDescription");
            desc.addClass("advRetDescription");
            cost.removeClass("advCost");
            cost.removeClass("advRecCost");
            cost.addClass("advRetCost");
            img.removeClass("advImageS");
            img.removeClass("advRecImageS");
            img.addClass("advRetImageS");
            imgc.removeClass("advImageConS");
            imgc.removeClass("advRecImageConS");
            imgc.addClass("advRetImageConS");
            button.removeClass("advButton");
            button.removeClass("advRecButton");
            button.addClass("advRetButton");
            buttonc.removeClass("advButtonCon");
            buttonc.removeClass("advRecButtonCon");
            buttonc.addClass("advRetButtonCon");
            break;
        case "2":
            block.removeClass("advRetBlock");
            block.removeClass("advBlock");
            block.addClass("advRecBlock");
            head.removeClass("advRetHeader");
            head.removeClass("advHeader");
            head.addClass("advRecHeader");
            desc.removeClass("advRetDescription");
            desc.removeClass("advDescription");
            desc.addClass("advRecDescription");
            cost.removeClass("advRetCost");
            cost.removeClass("advCost");
            cost.addClass("advRecCost");
            img.removeClass("advRetImageS");
            img.removeClass("advImageS");
            img.addClass("advRecImageS");
            imgc.removeClass("advRetImageConS");
            imgc.removeClass("advImageConS");
            imgc.addClass("advRecImageConS");
            button.removeClass("advRetButton");
            button.removeClass("advButton");
            button.addClass("advRecButton");
            buttonc.removeClass("advRetButtonCon");
            buttonc.removeClass("advButtonCon");
            buttonc.addClass("advRecButtonCon");
            break;
        case "3":
            block2.removeClass("advRetBlock");
            block2.removeClass("advRecBlock");
            block2.addClass("advBlock");
            head2.removeClass("advRetHeader");
            head2.removeClass("advRecHeader");
            head2.addClass("advHeader");
            desc2.removeClass("advRetDescription");
            desc2.removeClass("advRecDescription");
            desc2.addClass("advDescription");
            cost2.removeClass("advRetCost");
            cost2.removeClass("advRecCost");
            cost2.addClass("advCost");
            img2.removeClass("advRetImageS");
            img2.removeClass("advRecImageS");
            img2.addClass("advImageS");
            imgc2.removeClass("advRetImageConS");
            imgc2.removeClass("advRecImageConS");
            imgc2.addClass("advImageConS");
            button2.removeClass("advRetButton");
            button2.removeClass("advRecButton");
            button2.addClass("advButton");
            buttonc2.removeClass("advRetButtonCon");
            buttonc2.removeClass("advRecButtonCon");
            buttonc2.addClass("advButtonCon");
            block0.removeClass("advBlock");
            block0.removeClass("advRecBlock");
            block0.addClass("advRetBlock");
            head0.removeClass("advHeader");
            head0.removeClass("advRecHeader");
            head0.addClass("advRetHeader");
            desc0.removeClass("advDescription");
            desc0.removeClass("advRecDescription");
            desc0.addClass("advRetDescription");
            cost0.removeClass("advCost");
            cost0.removeClass("advRecCost");
            cost0.addClass("advRetCost");
            img0.removeClass("advImageS");
            img0.removeClass("advRecImageS");
            img0.addClass("advRetImageS");
            imgc0.removeClass("advImageConS");
            imgc0.removeClass("advRecImageConS");
            imgc0.addClass("advRetImageConS");
            button0.removeClass("advButton");
            button0.removeClass("advRecButton");
            button0.addClass("advRetButton");
            buttonc0.removeClass("advButtonCon");
            buttonc0.removeClass("advRecButtonCon");
            buttonc0.addClass("advRetButtonCon");
            block1.removeClass("advRetBlock");
            block1.removeClass("advBlock");
            block1.addClass("advRecBlock");
            head1.removeClass("advRetHeader");
            head1.removeClass("advHeader");
            head1.addClass("advRecHeader");
            desc1.removeClass("advRetDescription");
            desc1.removeClass("advDescription");
            desc1.addClass("advRecDescription");
            cost1.removeClass("advRetCost");
            cost1.removeClass("advCost");
            cost1.addClass("advRecCost");
            img1.removeClass("advRetImageS");
            img1.removeClass("advImageS");
            img1.addClass("advRecImageS");
            imgc1.removeClass("advRetImageConS");
            imgc1.removeClass("advImageConS");
            imgc1.addClass("advRecImageConS");
            button1.removeClass("advRetButton");
            button1.removeClass("advButton");
            button1.addClass("advRecButton");
            buttonc1.removeClass("advRetButtonCon");
            buttonc1.removeClass("advButtonCon");
            buttonc1.addClass("advRecButtonCon");
            break;
    }
    $('div [data-image-id]').each(function(i, el) {
    	var data_image_id = $(el).attr('data-image-id');
    	var slide = $('div [data-image-id='+ data_image_id +']>ul>li>img');
        var slideCount = $('div [data-image-id='+ data_image_id +']>ul>li').length;
        var slideWidth = slide.width();
        var slideHeight = slide.height();
        var sliderUlWidth = slideCount * slideWidth;
        $(el).css({ width: slideWidth, height: slideHeight });
        $('div [data-image-id='+ data_image_id +']>ul').css({ width: sliderUlWidth, marginLeft: - slideWidth });
        $('div [data-image-id='+ data_image_id +']>ul>li:last-child').prependTo('div [data-image-id='+ data_image_id +']>ul');
    });

    function moveLeft(el) {
        var data = $(el).parent().attr('data-image-id');
        var slideWidth = $('div [data-image-id='+ data +']>ul>li>img').width();
        $('div [data-image-id='+ data +']>ul').animate({
            left: + slideWidth
        }, 1000, function () {
            $('div [data-image-id='+ data +']>ul>li:last-child').prependTo('div [data-image-id='+ data +']>ul');
            $('div [data-image-id='+ data +']>ul').css('left', '');
        });
    }

    function moveRight(el) {
        var data = $(el).parent().attr('data-image-id');
        var slideWidth = $('div [data-image-id='+ data +']>ul>li>img').width();
        $('div [data-image-id='+ data +']>ul').animate({
            left: - slideWidth
        }, 1000, function () {
            $('div [data-image-id='+ data +']>ul>li:first-child').appendTo('div [data-image-id='+ data +']>ul');
            $('div [data-image-id='+ data +']>ul').css('left', '');
        });
    }

    var control_prev = $('div.control_prev');
    var control_next = $('div.control_next');

    control_prev.unbind();
    control_next.unbind();
    control_prev.click(function (event) {
        event.preventDefault();
        var target = $( event.target );
        moveLeft(target);
    });

    control_next.click(function (event) {
        event.preventDefault();
        var target = $( event.target );
        moveRight(target);
    });
}

function AdMaker()
{
	Array.prototype.has = function(value) {
		for (var i=0; i<this.length; i++)
			if (this[i] === value){
				return true;
			}
		return false;
	}
	
	function createColorPicker(selector){
		$(selector).ColorPicker({
			color: '#0000ff',
			onShow: function(colpkr){
				$(colpkr).fadeIn(200);
				return false;
			},
			onHide: function(colpkr){
				$(colpkr).fadeOut(200);
				return false;
			},
			onChange: function(hsb, hex, rgb){
				$(selector).css('color', '#' + hex);
				$(selector).val(hex);
				render();
			}
		}).bind('keyup', function(){
			$(this).ColorPickerSetColor(this.value);
		});
	}
	
	/**
	 * Создаёт аккордион настроек
	 */
	function createOptionsSelector() {
		function blockSizeOptions(selector, group) {
			$(selector).append('<div><span class="optionsGroup">Размер:</span>' +
						' <span>	ширина <input type="text" onkeyup="admaker.render()" id="width' + group + '" value="0" size="4" />' +
						' высота <input type="text" onkeyup="admaker.render()" id="height' + group + '" value="0" size="4" /> </span> ' +
                        ' <br style="clear: both" />' +
						'<span class="optionsGroup">Положение:</span>' +
						'<span>слева <input onkeyup="admaker.render()" type="text" id="left' + group + '" value="0" size="5" />' +
						'сверху <input onkeyup="admaker.render()" type="text" id="top' + group + '" value="0" size="5"/> </span>' +
                        ' <br style="clear: both" />' +
                        '<span class="optionsGroup">HTML: </span> ' +
                        '<span><textarea name="html' + group + '" onkeyup="admaker.render()" id="html' + group + '" cols="40" rows="10"></textarea> </span>' +
                        '</div>');
		}
		function blockOptions(selector, group) {
			$(selector).append('<div><span class="optionsGroup">Размер:</span>' +
						' <span>	ширина <input type="text" onkeyup="admaker.render()" id="width' + group + '" value="auto" size="4" />' +
						' высота <input type="text" onkeyup="admaker.render()" id="height' + group + '" value="auto" size="4" /> </span> ' + 
						' <br style="clear: both" />' +
						'<span class="optionsGroup"> Граница: </span> ' +
						'<span> цвет <input type="text" id="borderColor' + group + '" value="000000" size="6" />'+
						'ширина: <input type="text" onkeyup="admaker.render()" id="borderWidth' + group + '" value="0" size="1" /> </span>' +
                        ' <br style="clear: both" />' +
                        '<span class="optionsGroup"> Закругление границы: </span> ' +
						'верх лево: <input type="text" onkeyup="admaker.render()" id="border_top_left_radius' + group + '" value="0" size="1" /> </span>' +
						'верх право: <input type="text" onkeyup="admaker.render()" id="border_top_right_radius' + group + '" value="0" size="1" /> </span>' +
						'низ право: <input type="text" onkeyup="admaker.render()" id="border_bottom_right_radius' + group + '" value="0" size="1" /> </span>' +
						'низ лево: <input type="text" onkeyup="admaker.render()" id="border_bottom_left_radius' + group + '" value="0" size="1" /> </span>' 
                        );
            if (group === 'Advertise')
            {
			$(selector).append(
                        '<span class="optionsGroup">Внешний отступ: </span> ' +
						'верх: <input type="text" onkeyup="admaker.render()" id="margin_top' + group + '" value="0" size="1" /> </span>' +
						'право: <input type="text" onkeyup="admaker.render()" id="margin_right' + group + '" value="0" size="1" /> </span>' +
						'низ: <input type="text" onkeyup="admaker.render()" id="margin_bottom' + group + '" value="0" size="1" /> </span>' +
						'лево: <input type="text" onkeyup="admaker.render()" id="margin_left' + group + '" value="0" size="1" /> </span>' +
						' <br style="clear: both" />' +
						'<span class="optionsGroup"> Граница ретаргетинговых: </span> ' +
						'<span> цвет <input type="text" id="borderColorRet' + group + '" value="000000" size="6" />'+
						'ширина: <input type="text" onkeyup="admaker.render()" id="borderWidthRet' + group + '" value="0" size="1" /> </span>'+
						' <br style="clear: both" />' +
						'<span class="optionsGroup"> Граница рекомендованых: </span> ' +
						'<span> цвет <input type="text" id="borderColorRec' + group + '" value="000000" size="6" />'+
						'ширина: <input type="text" onkeyup="admaker.render()" id="borderWidthRec' + group + '" value="0" size="1" /> </span>' +
						' <br style="clear: both" />' +
                        '<span class="optionsGroup">Цвет фона: </span> ' +
                        '<span><input type="text" id="backgroundColor' + group + '" value="ffffff" size="6" /></span>' +
						'<span>прозрачный<input type="checkbox" onchange="admaker.render()" id="backgroundColorStatus' + group + '"/> </span>' +
						' <br style="clear: both" />' +
                        '<span class="optionsGroup">Цвет фона ретаргетинга: </span> ' +
                        '<span><input type="text" id="backgroundColorRet' + group + '" value="ffffff" size="6" /></span>' +
						'<span>прозрачный<input type="checkbox" onchange="admaker.render()" id="backgroundColorRetStatus' + group + '"/> </span>' +
						' <br style="clear: both" />' +
                        '<span class="optionsGroup">Цвет фона рекомендованых: </span> ' +
                        '<span><input type="text" id="backgroundColorRec' + group + '" value="ffffff" size="6" /></span>' +
						'<span>прозрачный<input type="checkbox" onchange="admaker.render()" id="backgroundColorRecStatus' + group + '"/> </span>' 
                        );
            }
            if (group === 'Button' || group === 'RetButton' || group === 'RecButton')
            {
			$(selector).append(
						' <br style="clear: both" />' +
                        '<span class="optionsGroup">Цвет фона: </span> ' +
                        '<span><input type="text" id="backgroundColor' + group + '" value="ffffff" size="6" /></span>' +
                        '<span><input type="text" id="backgroundColor2' + group + '" value="ffffff" size="6" /></span>' +
						' <br style="clear: both" />' +
                        '<span class="optionsGroup">Текст кнопки: </span> ' +
                        '<span><input type="text" id="content' + group + '" value="Купить" onkeyup="admaker.render()" size="6" /></span>'
                        );
            }
			$(selector).append('<br style="clear: both" />' + 
						'<span class="optionsGroup">Положение:</span>' +
						'<span>слева <input type="text" onkeyup="admaker.render()" id="left' + group + '" value="0" size="5" />' +
							 'сверху <input type="text" onkeyup="admaker.render()" id="top' + group + '" value="0" size="5"/> </span>' +
						'<br style="clear: both" />' +
						'<span class="optionsGroup">Спрятать:</span>' +
								'<input type="checkbox" onchange="admaker.render()" id="hide' + group + '" value="hide"/> </span>' +
						'<br style="clear: both" />' +
						'<span class="optionsGroup">Выравнивание:</span>' +
						'	<select onchange="admaker.render()" id="align' + group + '" name="align' + group + '"> ' +
						'	<option value="center">по центру</option>' + 
						'	<option value="left">слева</option>' + 
						'	<option value="right">справа</option>' + 
						'	</select>' + 
						'<br style="clear: both" />' +
					'</div>');
					

			createColorPicker('#borderColor' + group);
            if (group == 'Advertise')
            {
			    createColorPicker('#backgroundColor' + group);
			    createColorPicker('#backgroundColorRet' + group);
			    createColorPicker('#backgroundColorRec' + group);
			    createColorPicker('#borderColorRet' + group);
			    createColorPicker('#borderColorRec' + group);
            }
            if (group == 'Button' || group == 'RetButton' || group == 'RecButton')
            {
			    createColorPicker('#backgroundColor' + group);
			    createColorPicker('#backgroundColor2' + group);
            }
		}
		
		function fontOptions(selector, group) {
			$(selector).append(
						'<span class="optionsGroup">Шрифт:</span>' +
						'<span>цвет <input type="text" onkeyup="admaker.render()" id="fontColor' + group + '" value="000000" size="6" />' +
						'размер <input type="text" onkeyup="admaker.render()" id="fontSize' + group + '" value="12" size="2"/> </span>' +
						'<select onchange="admaker.render()" id="fontFamily' + group + '" name="fontFamily' + group + '"> ' +
						'<option value=\'Arial, Helvetica, sans-serif;\'>Arial</option>' + 
						'<option value=\'Georgia, serif;\'>Georgia</option>' + 
						'<option value=\'Verdana, Geneva, sans-serif;\'>Verdana</option>' + 
						'<option value=\'"Times New Roman", Times, serif;\'>Times New Roman</option>' + 
						'<option value=\'Tahoma, Geneva, sans-serif;\'>Tahoma</option>' + 
						'<option value=\'"Trebuchet MS", Helvetica, sans-serif;\'>Trebuchet MS</option>' + 
						'<option value=\'"Courier New", Courier, monospace;\'>Courier New</option>' + 
						'<option value=\'"Lucida Console", Monaco, monospace;\'>Lucida Console</option>' + 
						'</select>' + 
						'<br style="clear: both" />'+
						'<span class="optionsGroup">&nbsp;</span>' +
                        '<span><b>b</b> <input type="checkbox" onchange="admaker.render()" id="fontBold' + group + '" value="true"/> </span>' + 
                        '<span><u>u</u> <input type="checkbox" onchange="admaker.render()" id="fontUnderline' + group + '" value="true"/> </span>' + 
                        '<span><b>капитель</b> <input type="checkbox" onchange="admaker.render()" id="font_variant' + group + '" value="true"/> </span>' + 
						'<br style="clear: both" />'+
						'<span class="optionsGroup">Межстрочный интервал:</span>' +
						'<span><input type="text" onkeyup="admaker.render()" id="line_height' + group + '" value="1.2" size="2"/> </span>' +
						'<br style="clear: both" />'+
						'<span class="optionsGroup">Межбуквенный интервал:</span>' +
						'<span><input type="text" onkeyup="admaker.render()" id="letter_spacing' + group + '" value="0" size="2"/> </span>' +
						'<br style="clear: both" />'
                        );
			createColorPicker('#fontColor' + group);
		}
		
		function loadOptions(options) {
			for (var group in options) {
				for (var o in options[group]) {
					var edit = document.getElementById(o + group);
					var newValue = options[group][o];
					if (edit && edit.value)
                    {
						edit.value = newValue;
                    }
					if (edit && (newValue === true)){
						edit.checked = true;
					}
					if (edit && edit.tagName === 'TEXTAREA'){
						edit.value = newValue;
					}
				}
			}
		}
		
		blockOptions("#mainOptions", 'Main', render);
		blockSizeOptions("#mainHeaderOptions", 'MainHeader', render);
		blockSizeOptions("#mainFooterOptions", 'MainFooter', render);
		var mainOptions = $("#mainOptions");
		mainOptions.append('<span>цвет фона<input type="text" id="backgroundColorMain" value="ffffff" size="6" /></span>');
		mainOptions.append('<span>прозрачный<input type="checkbox" onchange="admaker.render()" id="backgroundColorStatusMain" value="hide"/></span>');
		mainOptions.append('<span>кол-во предложений<input type="text" onkeyup="admaker.render()" id="itemsNumberMain" value="6" size="2" /></span>');

		createColorPicker("#backgroundColorMain");
		
		blockOptions('#advertiseOptions', 'Advertise');
		
		blockOptions('#headerOptions', 'Header');
		fontOptions('#headerOptions', 'Header');
		
		blockOptions('#descriptionOptions', 'Description');
		fontOptions('#descriptionOptions', 'Description');
		
		blockOptions('#costOptions', 'Cost');
		fontOptions('#costOptions', 'Cost');
		
		blockOptions('#buttonOptions', 'Button');
		fontOptions('#buttonOptions', 'Button');
		
		blockOptions('#imageOptions', 'Image');

		blockOptions('#headerRetOptions', 'RetHeader');
		fontOptions('#headerRetOptions', 'RetHeader');
		
		blockOptions('#descriptionRetOptions', 'RetDescription');
		fontOptions('#descriptionRetOptions', 'RetDescription');
		
		blockOptions('#costRetOptions', 'RetCost');
		fontOptions('#costRetOptions', 'RetCost');
		
		blockOptions('#buttonRetOptions', 'RetButton');
		fontOptions('#buttonRetOptions', 'RetButton');
		
		blockOptions('#imageRetOptions', 'RetImage');
		
        blockOptions('#headerRecOptions', 'RecHeader');
		fontOptions('#headerRecOptions', 'RecHeader');
		
		blockOptions('#descriptionRecOptions', 'RecDescription');
		fontOptions('#descriptionRecOptions', 'RecDescription');
		
		blockOptions('#costRecOptions', 'RecCost');
		fontOptions('#costRecOptions', 'RecCost');
		
		blockOptions('#buttonRecOptions', 'RecButton');
		fontOptions('#buttonRecOptions', 'RecButton');

		blockOptions('#imageRecOptions', 'RecImage');

		$("#navOptions").append(
						'<br style="clear: both" />' +
						'<span class="optionsGroup">Стрелка:</span>' +
						'<span>цвет<input type="text" id="colorNav" value="ffffff" size="6" /></span>' + 
						'<span>фон<input type="text" id="backgroundColorNav" value="7070ff" size="6" /></span>' +
						'<select onchange="admaker.render()" id="navPositionNav" name="navPositionNav"> ' +
						'<option value="top-left">слева вверху</option>' + 
						'<option value="bottom-left">слева внизу</option>' + 
						'<option value="top-right">справа вверху</option>' + 
						'<option value="bottom-right">справа внизу</option>' +
						'</select>' + 
						'<br style="clear: both" />' +
						'<span class="optionsGroup">Логотип:</span>' +
						'<select onchange="admaker.render()" id="logoPositionNav" name="logoPositionNav"> ' +
						'<option value="top-left">слева вверху</option>' + 
						'<option value="bottom-left">слева внизу</option>' + 
						'<option value="top-right">справа вверху</option>' + 
						'<option value="bottom-right">справа внизу</option>' +
						'</select>' + 
						'<select onchange="admaker.render()" id="logoColorNav" name="logoColorNav"> ' +
						'<option value="black">чёрный</option>' + 
						'<option value="color">цветной</option>' + 
						'<option value="blue">синий</option>' + 
						'<option value="white">белый</option>' + 
						'</select>' + 
						'Спрятать: <input type="checkbox" onchange="admaker.render()" id="logoHideNav" value="hide"/>' +
                        '<br style="clear: both" />' +
                        '<span class="optionsGroup">Время прокрутки</span>' +
                        '<span><input type="text" id="auto_reload" size="6" /></span>' + 
                        '<br style="clear: both" />' +
                        '<span>Blink после прокрутки <input type="checkbox" id="blinking_reload"/></span>'+
						'<br style="clear: both" />' +
                        '<span>Shake перед прокруткой <input type="checkbox" id="shake_reload"/></span>'+
						'<br style="clear: both" />' +
                        '<span>Shake от движения мышью <input type="checkbox" id="shake_mouse"/></span>'+
						'<br style="clear: both" />' +
                        '<span class="optionsGroup">Blink блока по времени</span>' +
                        '<span><input type="text" id="blinking" size="6" /></span>' + 
                        '<br style="clear: both" />' +
                        '<span class="optionsGroup">Shake блока по времени</span>' +
                        '<span><input type="text" id="shake" size="6" /></span>' + 
						'<br style="clear: both" />' +
						'</span');
		$("#advOptions").append(
						'<br style="clear: both" />' +
						'<span class="optionsGroup">Отображение рекламы:</span>' +
						'<br style="clear: both" />' +
                        '<span>Всплывашка <input type="checkbox" id="html_notification"/></span>'+
						'<br style="clear: both" />' +
                        '<span>Включить ветку мест размешения <input type="checkbox" id="plase_branch"/></span>'+
						'<br style="clear: both" />' +
                        '<span>Включить ветку ретаргетинга <input type="checkbox" id="retargeting_branch"/></span>'+
						'<br style="clear: both" />' +
                        '<span>Порог рейтинга <input type="text" id="rating_division" size="6" /></span>'+
						'<br style="clear: both" />' +
						'<span>Жесткое ограничение рейтинга <input type="checkbox" id="rating_hard_limit"/></span>'+
						'<br style="clear: both" />' +
						'<span class="optionsGroup">При отсутствии релевантной рекламы:</span>' +
						'<select  id="action" name="action"> ' +
						'<option value="social">отображать социальную рекламу</option>' + 
						'<option value="usercode">выводить пользовательский код</option>' + 
						'</select>' + 
						'<br style="clear: both" />' +
						'<span class="optionsGroup">Пользовательский код:</span>' +
					    '<textarea id="user-code" style="width: 100%; height:100px;"></textarea>'
						);
        var d = document.createElement("div");
        d.innerHTML = non_relevant["userCode"];
        $("#user-code").val(d.innerText);
        $("#auto_reload").val(auto_reload);
        $("#blinking").val(blinking);
        $("#shake").val(shake);
        $("#rating_division").val(rating_division);
        $("#rating_hard_limit").attr('checked', rating_hard_limit);
        $("#html_notification").attr('checked', html_notification);
        $("#blinking_reload").attr('checked', blinking_reload);
        $("#shake_reload").attr('checked', shake_reload);
        $("#shake_mouse").attr('checked', shake_mouse);
        $("#plase_branch").attr('checked', plase_branch);
        $("#retargeting_branch").attr('checked', retargeting_branch);
        $("#action option[value=" + non_relevant['action'] + "]").attr('selected', 'true');
		createColorPicker("#backgroundColorNav");
		createColorPicker("#colorNav");		
		loadOptions(initialOptions);
		
	}
	
	

	$("#admakerOptions").accordion().draggable();	
	createOptionsSelector();
	$("#refreshButton").click(render);
	$("#printButton").click(function() {
		var data = getData();
	    var result = TrimPath.processDOMTemplate("styleTemplate", data);
		var items = [];
        var header = data.MainHeader.html;
        var footer = data.MainFooter.html;
		for (var i=0; i<data.Main.itemsNumber; i++)			// Шаблонизатор не умеет делать циклы по счётчику :(
			items.push(i);
		result += TrimPath.processDOMTemplate("contentTemplate", {
            items: items, header: header, footer:footer
		});
	});
	
	$("#saveButton").click(function() {
		var data = getData();
        var seting = getSeting();
        var save_url = 'save';
        if (dynamic){
        	save_url = 'save_dynamic';
		}
		$.ajax({
			url: '/advertise/'+ save_url +'?adv_id=' + CurrentAdvertiseId,
			type: 'POST',
			data: JSON.stringify({
				options: data,
                nonRelevant: seting['nonRelevant'],
                html_notification: seting['html_notification'],
                blinking_reload: seting['blinking_reload'],
                shake_reload: seting['shake_reload'],
                shake_mouse: seting['shake_mouse'],
                plase_branch: seting['plase_branch'],
                auto_reload: seting['auto_reload'],
                blinking: seting['blinking'],
                shake: seting['shake'],
                rating_division: seting['rating_division'],
				rating_hard_limit: seting['rating_hard_limit'],
                retargeting_branch: seting['retargeting_branch'],
				css: TrimPath.processDOMTemplate("styleTemplate", data)
			}),
			dataType: 'json',
			contentType: "application/json; charset=utf-8",
			success: function (result) {
				if (!result.error)
					alert('OK!');
                else
                    alert("Ошибка сохранения: \n" + result.message);
			} 
		})
	});
	
    $("#savePatternButton").click(function() {
		var data = getData();
		$.ajax({
			url: '/advertise/pattern_save?adv_id=' + CurrentAdvertiseId,
			type: 'POST',
			data: JSON.stringify({
				options: data,
			}),
			dataType: 'json',
			contentType: "application/json; charset=utf-8",
			success: function (result) {
				if (!result.error)
					alert('OK!');
                else
                    alert("Ошибка сохранения: \n" + result.message);
			} 
		})
	});

    function getSeting()
    {
        var data = {};
        data.nonRelevant = {
        	action: $("#action").val(),
        	userCode: $("#user-code").val(),
        };
        data.html_notification = $('#html_notification').is(":checked");
        data.blinking_reload = $('#blinking_reload').is(":checked");
        data.shake_reload = $('#shake_reload').is(":checked");
        data.shake_mouse = $('#shake_mouse').is(":checked");
        data.auto_reload = $('#auto_reload').val();
        data.blinking = $('#blinking').val();
        data.shake = $('#shake').val();
        data.rating_division = $('#rating_division').val();
        data.rating_hard_limit = $('#rating_hard_limit').is(":checked");
        data.plase_branch = $('#plase_branch').is(":checked");
        data.retargeting_branch = $('#retargeting_branch').is(":checked");
        return data;
    }
	
	function getData() {
		function selectedValue(id) {
			var o = document.getElementById(id);
			var value = null;
			try {
				value = o.options[o.selectedIndex].value;
			} catch(e) {
			}
			return value;
		} // end selectedValue()
		
		
		var sections = ["Header", 'Main', 'MainHeader', 'MainFooter', 'Advertise', 'Description', 'Cost', 'Button', 'Image', "RetHeader", 'RetDescription', 'RetCost', 'RetButton', 'RetImage', "RecHeader", 'RecDescription', 'RecCost', 'RecButton', 'RecImage'];
		var data = {};
		for (var i=0; i<sections.length; i++) {
			var group = sections[i];
			data[group] = {
				left:		$('#left' + group).val(),
				top: 		$('#top' + group).val(),
				width: 		$('#width' + group).val(),
				height:		$('#height' + group).val(),
				borderColor:$('#borderColor' + group).val(),
				borderWidth:$('#borderWidth' + group).val(),
                border_top_left_radius: $('#border_top_left_radius' + group).val(),
                border_top_right_radius: $('#border_top_right_radius' + group).val(),
                border_bottom_right_radius: $('#border_bottom_right_radius' + group).val(),
                border_bottom_left_radius: $('#border_bottom_left_radius' + group).val(),
                margin_top: $('#margin_top' + group).val(),
                margin_right: $('#margin_right' + group).val(),
                margin_bottom: $('#margin_bottom' + group).val(),
                margin_left: $('#margin_left' + group).val(),
				fontColor: 	$('#fontColor' + group).val(),
				html: 	$('#html' + group).val(),
				fontSize: 	$('#fontSize' + group).val(),
				line_height: 	$('#line_height' + group).val(),
				letter_spacing: 	$('#letter_spacing' + group).val(),
				fontBold:	$("#fontBold" + group).is(":checked"),
				font_variant:	$("#font_variant" + group).is(":checked"),
				fontUnderline: $("#fontUnderline" + group).is(":checked"),
                fontFamily: $("#fontFamily" + group).val(),
				hide:		$("#hide" + group).is(":checked"),
				align:		$("#align" + group).val()
			};
            if (group === 'Advertise')
            {
				data[group].borderColorRet=$('#borderColorRet' + group).val();
				data[group].borderWidthRet=$('#borderWidthRet' + group).val();
				data[group].borderColorRec=$('#borderColorRec' + group).val();
				data[group].borderWidthRec=$('#borderWidthRec' + group).val();
				data[group].backgroundColorStatus=$('#backgroundColorStatus' + group).is(":checked");
				data[group].backgroundColorRetStatus=$('#backgroundColorRetStatus' + group).is(":checked");
				data[group].backgroundColorRecStatus=$('#backgroundColorRecStatus' + group).is(":checked");
		        data[group].backgroundColor = $('#backgroundColor' + group).val();
		        data[group].backgroundColorRet = $('#backgroundColorRet' + group).val();
		        data[group].backgroundColorRec = $('#backgroundColorRec' + group).val();
            }
            if (group === 'Button' || group === 'RetButton' || group === 'RecButton')
            {
		        data[group].backgroundColor = $('#backgroundColor' + group).val();
		        data[group].backgroundColor2 = $('#backgroundColor2' + group).val();
		        data[group].content = $('#content' + group).val();
            }
            if (data[group].fontFamily === 'Verdana, "Geneva CY", "DejaVu Sans", sans-serif;'){
            	data[group].fontSize -= 2;
			}

		}
		data.Main.backgroundColor = document.getElementById('backgroundColorMain').value;
		data.Main.itemsNumber = document.getElementById('itemsNumberMain').value;
		data.Main.backgroundColorStatus = $('#backgroundColorStatusMain').is(":checked");
		data.Nav = {};
		data.Nav.backgroundColor = document.getElementById('backgroundColorNav').value;
		data.Nav.color = document.getElementById('colorNav').value;
		data.Nav.navPosition = selectedValue('navPositionNav');
		data.Nav.logoPosition = selectedValue('logoPositionNav');
		data.Nav.logoColor = selectedValue('logoColorNav');
		data.Nav.logoHide = $("#logoHideNav").is(":checked");
		return data;
	}
	
	
	function render() {
		var data = getData();
        var header = data.MainHeader.html;
        var footer = data.MainFooter.html;
	    var result = TrimPath.processDOMTemplate("styleTemplate", data);
		var items = [];
		for (var i=0; i<data.Main.itemsNumber; i++)	{
			items.push(i);
		}		// Шаблонизатор не умеет делать циклы по счётчику :(
		result += TrimPath.processDOMTemplate("contentTemplate", {items: items, header: header, footer:footer});
	    document.getElementById('admakerPreview').innerHTML = result;
        switch_css($("#render_type" ).val());	
	}
	render();

	
	return {
		render: render
	};
}

var admaker = AdMaker();
