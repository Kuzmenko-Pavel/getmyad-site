/**
 *    Вспомогательные методы для работы с графиками
 */
window.isAdvertiseChartEnabled = {};			// Словарь отмеченных выгрузкок {title: true|false}
var plotOptions = {
    series: {
        points: {show: true},
        lines: {show: true}
    },
    grid: {
        hoverable: true,
        backgroundColor: {colors: ["#fff", "#e7e7e7"]},
        mouseActiveRadius: 15
    },
    xaxis: {
        mode: "time",
        monthNames: ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'],
        timeformat: '%d %b'
    },
    legend: {
        noColumns: 1,
        labelFormatter: function (label, series) {
            'use strict';
            var enabled = 'window.isAdvertiseChartEnabled["' + label + '"]';
            var res = "<input type='checkbox' ";
            if (window.isAdvertiseChartEnabled[label]) {
                res += 'checked ';
            }
            res += "onclick='" + enabled + " = !" + enabled + "; drawChartUsingFilter(); '/>" + label;
            return res;
        },
        container: "#chartLegend"
    }
};

// Строит графики c учётом выставленных параметров
function drawChartUsingFilter() {
    'use strict';
    var data = [];
    $.each(window.account_data.chartData, function (index, one) {
        if (window.isAdvertiseChartEnabled[one.adv.domain + ', ' + one.adv.title]) {
            data.push({
                label: one.adv.domain + ', ' + one.adv.title,
                data: one.data
            });
        }
        else {
            data.push({
                label: one.adv.domain + ', ' + one.adv.title,
                data: []
            });
        }
    });
    $.plot($("#chart"), data, plotOptions);
}
/*********************************************************************************/

( function ($) {
    'use strict';

    $(document).ready(function () {
        var dateRangeParams = {};

        /**
         * Создание пользовательского интерфейса
         */
        function prepareUi() {
            $(".spanAccountSumm").html(Math.round(window.account_data.accountSumm * 100) / 100 + "грн");
            $(".spanAccountOutSumm").html(Math.round(window.account_data.accountOutSumm * 100) / 100 + "грн");
            // Сводный отчёт по всем рекламным выгрузкам
            // Форматирует дату для передачи серверу
            function formatDate(date) {
                if (!date.getMonth) {
                    return date;
                }
                var m = date.getMonth() + 1;
                var d = date.getDate();
                return (d < 10 ? "0" + d : d) + '.' + (m < 10 ? "0" + m : m) + "." + date.getFullYear();
            }

            var dayStart = new Date();
            var today = new Date();
            dayStart.setDate(today.getDate() - 29);
            dayStart = formatDate(dayStart);
            var dayEnd = formatDate(today);
            dateRangeParams = $.param({
                'dateStart': dayStart,
                'dateEnd': dayEnd
            });
            var surl = '/advertise/allAdvertises?' + dateRangeParams;
            $("#tableAllAdvertise").jqGrid({
                datatype: "json",
                url: surl,
                mtype: 'GET',
                colNames: ['Рекламные блоки', 'Показы', 'Клики',
                    'CTR', 'Показы в видимой части экрана', 'Средняя цена', 'Расчетный доход'],
                colModel: [
                    {name: 'Title', index: 'Title', width: 200, align: 'left', sortable: false},
                    {name: 'Impressions', index: 'Impressions', width: 80, align: 'center', sortable: false},
                    {name: 'Clicks', index: 'Clicks', width: 80, align: 'center', sortable: false},
                    {name: 'CTR', index: 'CTR', width: 90, align: 'center', sortable: false},
                    {name: 'ViewPort', index: 'ViewPort', width: 90, align: 'center', sortable: false},
                    {name: 'Cost', index: 'Cost', width: 85, align: 'center', sortable: false},
                    {name: 'Summ', index: 'Summ', width: 80, align: 'center', sortable: false},
                ],
                caption: "Заработок по всем рекламным блокам",
                footerrow: true,
                userDataOnFooter: true,
                rownumbers: false,
                height: 'auto',
                autowidth: true,
                rownumWidth: 30,
                rowNum: 100,
                forceFit: true,
                multiselect: false,
                subGrid: true,
                subGridRowExpanded: function (subgrid_id, row_id) {
                    var subgrid_table_id = subgrid_id + "_t";
                    var pager_id = "p_" + subgrid_table_id;
                    $('#' + subgrid_id).html('<table id="' + subgrid_table_id + '" class="scroll"></table><div id="' + pager_id + '" class="scroll"></div>');
                    var url = '/advertise/daysSummary?' + dateRangeParams + '&adv=' + row_id;

                    $("#" + subgrid_table_id).jqGrid({
                        url: url,
                        datatype: 'json',
                        mtype: 'GET',
                        colNames: ['Дата', 'Показы', 'Клики',
                            'CTR', 'Показы в видимой части экрана', 'Средняя цена', 'Расчетный доход'],
                        colModel: [
                            {
                                name: 'Title',
                                index: 'Title',
                                width: 200,
                                align: 'left',
                                sortable: false,
                                classes: 'subgrid_cell'
                            },
                            {
                                name: 'Impressions',
                                index: 'Impressions',
                                width: 80,
                                align: 'center',
                                sortable: false,
                                classes: 'subgrid_cell'
                            },
                            {
                                name: 'Clicks',
                                index: 'Clicks',
                                width: 80,
                                align: 'center',
                                sortable: false,
                                classes: 'subgrid_cell'
                            },
                            {
                                name: 'CTR',
                                index: 'CTR',
                                width: 90,
                                align: 'center',
                                sortable: false,
                                classes: 'subgrid_cell'
                            },
                            {
                                name: 'ViewPort',
                                index: 'ViewPort',
                                width: 90,
                                align: 'center',
                                sortable: false,
                                classes: 'subgrid_cell'
                            },
                            {
                                name: 'Cost',
                                index: 'Cost',
                                width: 85,
                                align: 'center',
                                sortable: false,
                                classes: 'subgrid_cell'
                            },
                            {
                                name: 'Summ',
                                index: 'Summ',
                                width: 80,
                                align: 'center',
                                sortable: false,
                                classes: 'subgrid_cell'
                            }
                        ],
                        pager: pager_id,
                        rowNum: 10,
                        autowidth: true,
                        forceFit: true,
                        height: 'auto',
                        beforeSelectRow: function () {
                            return false;
                        }

                    });
                },
            });


            // Статистика, разбитая по датам
            $("#tableStatsByDays").jqGrid({
                url: '/advertise/daysSummary',
                datatype: 'json',
                mtype: 'GET',
                colNames: ['Дата', 'Показы', 'Клики', 'CTR', 'Показы в видимой части экрана', 'Средняя цена', 'Расчетный доход'],
                colModel: [
                    {name: 'Date', index: 'Date', width: 100, align: 'center', sortable: false},
                    {name: 'Impressions', index: 'Impressions', width: 90, align: 'center', sortable: false},
                    {name: 'Clicks', index: 'Clicks', width: 95, align: 'center', sortable: false},
                    {name: 'CTR', index: 'CTR', width: 100, align: 'center', sortable: false},
                    {name: 'ViewPort', index: 'ViewPort', width: 100, align: 'center', sortable: false},
                    {name: 'Cost', index: 'Cost', width: 100, align: 'center', sortable: false, hidden: true},
                    {name: 'Summ', index: 'Summ', width: 100, align: 'center', sortable: false, hidden: true}
                ],
                caption: "Статистика за каждый день по всем рекламным блокам",
                gridview: true,
                rownumbers: true,
                rownumWidth: 40,
                rowNum: 10,
                height: 'auto',
                forceFit: true,
                hiddengrid: true,
                pager: "#pagerStasByDays"
            });


            // Операции со счётом: приход
            $("#tableAccountIncome").jqGrid({
                url: '/private/accountIncome',
                datatype: 'json',
                mtype: 'GET',
                colNames: ['Дата', 'Показы', 'Клики', 'Средняя цена', 'Расчетный доход'],
                colModel: [
                    {name: 'Date', index: 'Date', width: 120, align: 'center', sortable: false},
                    {name: 'Impressions', index: 'Impressions', width: 90, align: 'center', sortable: false},
                    {name: 'Clicks', index: 'Clicks', width: 120, align: 'center', sortable: false},
                    {name: 'Cost', index: 'Cost', width: 120, align: 'center', sortable: false},
                    {name: 'Summ', index: 'Summ', width: 120, align: 'center', sortable: false}
                ],
                caption: "Начисления на счёт",
                gridview: true,
                rownumbers: true,
                rownumWidth: 40,
                rowNum: 10,
                forceFit: true,
                width: 'auto',
                height: 'auto',
                pager: "#pagerAccountIncome"
            });

            // Операции со счётом: вывод денег
            $("#tableAccountMoneyOut").jqGrid({
                url: '/private/moneyOutHistory',
                datatype: 'json',
                mtype: 'GET',
                colNames: ['Дата', 'Тип платежа', 'Сумма', 'Код Протекции', 'Действителен до', 'Примечания'],
                colModel: [
                    {name: 'Date', index: 'Date', width: 120, align: 'center', sortable: false},
                    {name: 'PaymentType', index: 'PaymentType', width: 120, align: 'center', sortable: false},
                    {name: 'Summ', index: 'Summ', width: 120, align: 'center', sortable: false},
                    {name: 'protectionCode', index: 'protectionCode', width: 120, align: 'center', sortable: false},
                    {name: 'protectionDate', index: 'protectionDate', width: 120, align: 'center', sortable: false},
                    {name: 'Comment', index: 'Comment', width: 300, align: 'center', sortable: false}],
                caption: "Вывод средств",
                gridview: true,
                rownumbers: false,
                rowNum: 30,
                loadonce: true,
                forceFit: true,
                toolbar: [true, 'top'],
                pager: "#pagerAccountMoneyOut",
                beforeSelectRow: function (rowid) {
                    if (rowid) {
                        if ($("#tableAccountMoneyOut").getRowData(rowid).Comment === "заявка обрабатывается...") {
                            buttonRejectMoneyOutRequest.attr('disabled', false);
                        }
                        else {
                            buttonRejectMoneyOutRequest.attr('disabled', true);
                        }
                    }
                    return true;
                }
            });

            var buttonRejectMoneyOutRequest = $("<input type='button' id='btnRejectMoneyOut' value='Отозвать заявку'/>");
            buttonRejectMoneyOutRequest.attr('disabled', true).click(function () {
                $("#dialogCancelRequest").dialog('open');
            });
            $("#t_tableAccountMoneyOut").append(buttonRejectMoneyOutRequest);
//--------------------------------------------------------------------------------------

            // Список существующих информеров (для редактирования)
            $("#tableExistingInformers").jqGrid({
                datatype: function () {
                    this.addJSONData(window.domains);
                    var tableExistingInformers = $("#tableExistingInformers");
                    for (var i = 0; i < tableExistingInformers.getGridParam("reccount"); i++) {
                        if (tableExistingInformers.getCell(i + 1, 'Domain') === '') {
                            tableExistingInformers.setCell(i + 1, 'Domain', 'Информеры, не привязанные к домену');
                        }
                    }

                },
                mtype: 'GET',
                height: 'auto',
                colNames: ['Сайт'],
                colModel: [{name: 'Domain', index: 'Domain', width: 565}],
                caption: "Список существующих рекламных блоков",
                rownumbers: true,
                rowNum: 50,
                subGrid: true,
                subGridBeforeExpand: function (subgrid_id, row_id) {
                    var index = $("#tableExistingInformers").jqGrid('getRowData', row_id).Domain.indexOf('ожидает подтверждения', 0);
                    if (index != -1) {
                        return false;
                    }
                },
                subGridRowExpanded: function (subgrid_id, row_id) {
                    var subgrid_table_id = subgrid_id + "_t";
                    var pager_id = "p_" + subgrid_table_id;
                    $('#' + subgrid_id).html('<table id="' + subgrid_table_id + '" class="scroll"></table><div id="'
                        + pager_id + '" class="scroll"></div>');
                    var row = $("#tableExistingInformers").jqGrid('getRowData', row_id);
                    var domain = '';
                    if (row.Domain === 'Информеры, не привязанные к домену') {
                        domain = '';
                    }
                    else {
                        domain = row.Domain;
                    }
                    var url = '/advertise/domainsAdvertises?domain=' + domain;
                    $("#" + subgrid_table_id).jqGrid({
                        url: url,
                        height: 'auto',
                        datatype: 'json',
                        mtype: 'GET',
                        colNames: ['Информер', '', ''],
                        colModel: [
                            {
                                name: 'Title',
                                index: 'Title',
                                width: 340,
                                align: 'center',
                                sortable: false,
                                classes: 'subgrid_cell'
                            },
                            {
                                name: 'GuidE',
                                index: 'GuidE',
                                width: 100,
                                align: 'center',
                                sortable: false,
                                classes: 'subgrid_cell'
                            },
                            {
                                name: 'GuidR',
                                index: 'GuidR',
                                width: 100,
                                align: 'center',
                                sortable: false,
                                classes: 'subgrid_cell'
                            },
                        ],
                        //pager: pager_id,
                        //beforeSelectRow: function(rowid, e) {
                        //	return false;
                        //},
                        rowNum: 50,
                        loadComplete: function () {
                            var $subgrid_table_id = $("#" + subgrid_table_id);
                            for (var i = 0; i < $subgrid_table_id.getGridParam("reccount"); i++) {
                                var guid = $subgrid_table_id.getCell(i + 1, 'GuidE');
                                var dyn = $subgrid_table_id.getCell(i + 1, 'GuidR');
                                $subgrid_table_id.setCell(i + 1, 'GuidR', "<input type='button' class='" + subgrid_table_id + "-GuidR' data=" + guid + " value='Удалить' />");
                                $subgrid_table_id.setCell(i + 1, 'GuidE', "<input type='button' class='" + subgrid_table_id + "-GuidE' data=" + guid + " dynamic=" + dyn + " value='Править' />");

                            }
                            var editExistingInformers = $('.' + subgrid_table_id + '-GuidE');
                            editExistingInformers.click(function () {
                                var id = $(this).attr('data');
                                var dynamic = $(this).attr('dynamic');
                                if (!id) {
                                    return;
                                }

                                if (dynamic === 'true') {
                                    document.location.assign('/advertise/edit_dynamic?ads_id=' + id + '#ready');
                                }
                                else {
                                    document.location.assign('/advertise/edit?ads_id=' + id + '#size');
                                }
                            });
                            var removeExistingInformers = $('.' + subgrid_table_id + '-GuidR');
                            removeExistingInformers.click(function () {
                                var id = $(this).attr('data');
                                var form = $('#formRemoveBlock');
                                form.get(0).setAttribute('action', '/advertise/remove?ads_id=' + id);
                                $("#dialogRemoveBlock").dialog('open');
                            });

                        }

                    });
                }

            });


            var datePickerOptions = {
                duration: '',
                onSelect: function () {
                    refreshData();
                }
            };

            $("#dateStart").datepicker(datePickerOptions).datepicker('hide');
            $("#dateEnd").datepicker(datePickerOptions).datepicker('hide');
            $("#dateFilterOneDay").datepicker(datePickerOptions).datepicker('hide');


            // Строим графики. Изначально показываем все выгрузки
            for (var i = 0; i < window.advertiseList.length; i++) {
                window.isAdvertiseChartEnabled[window.advertiseList[i].domain + ', ' + window.advertiseList[i].title] = true;
            }
            // Показываем выбранный диапазон на графике
            var date1 = null, //new Date(2000,0,0),
                date2 = null; //new Date(2020,0,0);
            if (dayStart !== '') {
                date1 = new Date(Number(dayStart.slice(6, 10)),
                    Number(dayStart.slice(3, 5)) - 1,
                    Number(dayStart.slice(0, 2)));
            }
            if (dayEnd !== '') {
                date2 = new Date(Number(dayEnd.slice(6, 10)),
                    Number(dayEnd.slice(3, 5)) - 1,
                    Number(dayEnd.slice(0, 2)));
            }

            if (date1 && date2 && (date2 - date1 < 1000 * 60 * 60 * 24 * 7)) {
                date1.setDate(date2.getDate() - 7);
            }
            var utc = (new Date()).getTimezoneOffset() * 60000;
            plotOptions.xaxis.min = date1 ? date1.getTime() + utc : null;
            plotOptions.xaxis.max = date2 ? date2.getTime() + utc : null;
            window.drawChartUsingFilter();


            function showTooltip(x, y, contents) {
                $('<div id="tooltip">' + contents + '</div>').css({
                    position: 'absolute',
                    display: 'none',
                    top: y + 10,
                    left: x + 10,
                    border: '1px solid #fdd',
                    padding: '2px',
                    'background-color': '#fee',
                    opacity: 0.80
                }).appendTo("body").show();
            }

            var prevPoint = null;
            $("#chart").bind("plothover", function (event, pos, item) {
                if (item) {
                    if (prevPoint === item.datapoint) {
                        return;
                    }
                    prevPoint = item.datapoint;
                    $("#tooltip").remove();
                    var y = item.datapoint[1].toFixed(2);
                    var dt = new Date(item.datapoint[0]);
                    var monthNames = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'];
                    showTooltip(item.pageX, item.pageY,
                        "<p style='text-align: center; font-weight: bold; margin: 0'>" + item.series.label + "</p>" +
                        "Сумма заработка: " + y + "грн<br />" +
                        "Дата: " + dt.getDate() + " " + monthNames[dt.getMonth()] + " " + dt.getFullYear());
                }
                else {
                    $("#tooltip").remove();
                    prevPoint = null;
                }
            });


            $("#tabs").tabs({
                select: function (event, ui) {
                    if (ui.index === 3) {
                        document.title = "YOTTOS | GetMyAd — Узнайте больше о GetMyAd!";
                    } else {
                        document.title = "YOTTOS | GetMyAd — " + "бесплатная программа для заработка в Интернете. Заработай на своем сайте";
                    }

                }
            });
            $("#tabs>ul>li:last-child").attr('style', 'position: absolute; right: 10px; top:5px');	// Отодвигаем вкладку "Помощь" вправо


            $("#showGrowingInfo, #showGrowingInfo2").click(function () {
                $("#tabs").tabs("select", 3);
                nextContents();
                return false;
            });

            $("#btnRegisterDomain").click(function () {
                $("#dialogRegisterDomain").dialog('open');
            });
            $("#btnRemoveDomain").click(function () {
                $("#dialogRemoveDomain").dialog('open');
            });


            if (document.getElementById("moneyOut_factura")) {
                $("#removeUploadFactura").hide();
                $("#removeUploadFactura").click(function () {
                    $.getJSON("/private/removeUploadFactura", function (data) {
                        if (data.error) {
                            if (data.msg) {
                                $("#moneyOut_errorMessage").html(data.msg);
                            }
                            else {
                                $("#moneyOut_errorMessage").html('Ошибка удаления файла!');
                            }
                        }
                        else {
                            $("#removeUploadFactura").hide();
                            $("#uploadButton").show();
                            $('#factura_files').text('');
                        }
                    });
                });

                new Ajax_upload('uploadButton', {
                    action: "/private/uploadFactura",
                    responseType: "json",
                    onSubmit: function (file) {
                        $('#uploadButton').text('Загружается ' + file);
                        this.disable();
                    },
                    onComplete: function (file, response) {
                        if (response.error) {
                            $('#factura_files').text('Ошибка добавления файла!');
                            $("#moneyOut_wait").hide();
                            $('#uploadButton').text('Добавить счёт-фактуру');
                            $('#uploadBUtton').show();
                            $('#removeUploadFactura').hide();
                        }
                        else {
                            this.enable();
                            $('#uploadButton').hide();
                            $('#uploadButton').text('Добавить счёт-фактуру');
                            $('#removeUploadFactura').show();
                            $("#moneyOut_wait").hide();
                            $('#factura_files').text(file);
                        }
                    }
                });
            }


        }  // end prepareUi()

        // -----------------------------------------

        /* В диалоге вывода средств отображение полей в соответствии с типом вывода средств*/
        function showRightMoneyOutBlock() {
            var val = $("#moneyOut_paymentType").val();
            var moneyOut_cash = $("#moneyOut_cash");
            var moneyOut_yandex = $("#moneyOut_yandex");
            var moneyOut_card = $("#moneyOut_card");
            var moneyOut_card_pb_ua = $("#moneyOut_card_pb_ua");
            var moneyOut_card_pb_us = $("#moneyOut_card_pb_us");
            var moneyOut_webmoney = $("#moneyOut_webmoney");
            var moneyOut_webmoney_r = $("#moneyOut_webmoney_r");
            var moneyOut_webmoney_u = $("#moneyOut_webmoney_u");
            var moneyOut_factura = $("#moneyOut_factura");
            var moneyOut_errorMessage = $("#moneyOut_errorMessage");
            var moneyOut_linkHelp = $("#moneyOut_linkHelp");
            moneyOut_cash.hide();
            moneyOut_yandex.hide();
            moneyOut_card.hide();
            moneyOut_card_pb_ua.hide();
            moneyOut_card_pb_us.hide();
            moneyOut_webmoney.hide();
            moneyOut_webmoney_r.hide();
            moneyOut_webmoney_u.hide();
            moneyOut_factura.hide();
            moneyOut_errorMessage.html('');
            moneyOut_linkHelp.hide();
            switch (val) {
                case 'cash':
                    moneyOut_cash.show();
                    break;
                case 'card':
                    moneyOut_card.show();
                    break;
                case 'card_pb_ua':
                    moneyOut_card_pb_ua.show();
                    break;
                case 'card_pb_us':
                    moneyOut_card_pb_us.show();
                    break;
                case 'webmoney_z':
                    moneyOut_webmoney.show();
                    break;
                case 'webmoney_r':
                    moneyOut_webmoney_r.show();
                    break;
                case 'webmoney_u':
                    moneyOut_webmoney_u.show();
                    moneyOut_linkHelp.show();
                    break;
                case 'factura' :
                    moneyOut_factura.show();
                    break;
                case 'yandex' :
                    moneyOut_yandex.show();
                    break;
                default:
                    moneyOut_webmoney.show();
                    moneyOut_linkHelp.show();
                    break;
            }
        }  // end showRightMoneyOutBlock()

        $("#moneyOut_paymentType").change(function () {
            showRightMoneyOutBlock();
        });

        /*----------------------------------------------*/


        /**
         * Обновляет данные с учётом текущих настроек фильтров.
         */
        function refreshData() {
            var NowDate = new Date();
            var filterPreset = document.getElementById("filterpreset");
            var dayStart = new Date();
            var dayEnd = new Date();
            var today = new Date();

            switch (filterPreset.options[filterPreset.selectedIndex].value) {
                case 'today':
                    dayEnd = dayStart = today;
                    break;
                case 'yesterday':
                    dayStart.setDate(today.getDate() - 1);
                    dayEnd = dayStart;
                    break;
                case 'thisweek':
                    var CurrentDay = NowDate.getDay();
                    var LeftOffset = CurrentDay - 1;
                    var RightOffset = 7 - CurrentDay;
                    dayStart = new Date(NowDate.getFullYear(), NowDate.getMonth(), NowDate.getDate() - LeftOffset);
                    dayEnd = new Date(NowDate.getFullYear(), NowDate.getMonth(), NowDate.getDate() + RightOffset);
                    break;
                case 'lastweek':
                    dayStart.setDate(today.getDate() - 6);
                    dayEnd = today;
                    break;
                case 'thismonth':
                    dayStart = new Date(NowDate.getFullYear(), NowDate.getMonth(), 1);
                    dayEnd = new Date(NowDate.getFullYear(), NowDate.getMonth(), NowDate.getDate());
                    break;
                case 'lastmonth':
                    dayStart.setDate(today.getDate() - 29);
                    dayEnd = today;
                    break;
                case 'range':
                    dayStart = $('#dateStart').val();
                    dayEnd = $('#dateEnd').val();
                    break;
                case 'oneday':
                    dayStart = dayEnd = $('#dateFilterOneDay').val();
                    break;
                case 'off':
                    dayStart = dayEnd = '';
                    break;
                default:
                    dayStart = dayEnd = '';
                    break;
            }

            // Форматирует дату для передачи серверу
            function formatDate(date) {
                if (!date.getMonth) {
                    return date;
                }
                var m = date.getMonth() + 1;
                var d = date.getDate();
                return (d < 10 ? "0" + d : d) + '.' + (m < 10 ? "0" + m : m) + "." + date.getFullYear();
            }

            dayStart = formatDate(dayStart);
            dayEnd = formatDate(dayEnd);

            dateRangeParams = $.param({
                'dateStart': dayStart,
                'dateEnd': dayEnd
            });

            // Обновляем таблицу статистики всех выгрузок
            $('#tableAllAdvertise').jqGrid('setGridParam', {datatype: "json"})
                .jqGrid('setGridParam', {url: "/advertise/allAdvertises?" + dateRangeParams})
                .trigger("reloadGrid");
            // Показываем выбранный диапазон на графике
            var date1 = null, //new Date(2000,0,0),
                date2 = null; //new Date(2020,0,0);
            if (dayStart !== '') {
                date1 = new Date(Number(dayStart.slice(6, 10)),
                    Number(dayStart.slice(3, 5)) - 1,
                    Number(dayStart.slice(0, 2)));
            }
            if (dayEnd !== '') {
                date2 = new Date(Number(dayEnd.slice(6, 10)),
                    Number(dayEnd.slice(3, 5)) - 1,
                    Number(dayEnd.slice(0, 2)));
            }

            if (date1 && date2 && (date2 - date1 < 1000 * 60 * 60 * 24 * 7)) {
                date1.setDate(date2.getDate() - 7);
            }
            var utc = (new Date()).getTimezoneOffset() * 60000;
            plotOptions.xaxis.min = date1 ? date1.getTime() + utc : null;
            plotOptions.xaxis.max = date2 ? date2.getTime() + utc : null;
            window.drawChartUsingFilter();

        } // end refreshData()


        /** Выбор пресета фильтра */
        // Форматирует дату для передачи серверу
        function formatDate(date) {
            if (!date.getMonth) {
                return date;
            }
            var m = date.getMonth() + 1;
            var d = date.getDate();
            return (d < 10 ? "0" + d : d) + '.' + (m < 10 ? "0" + m : m) + "." + date.getFullYear();
        }

        $("#filterpreset").change(function () {
            var o = $("#filterpreset");
            var val = o.val();
            if (val === "range") {
                $("#filterByRangeOptions").css('display', 'inline');
                $("#filterByOneDayOptions").css('display', 'none');
            }
            else if (val === "oneday") {
                $("#filterByOneDayOptions").css('display', 'inline');
                $("#filterByRangeOptions").css('display', 'none');
            }
            else {
                $("#filterByOneDayOptions").hide();
                $("#filterByRangeOptions").hide();
            }
            refreshData();
        }); // end filterpreset.click()

        /** Изменяет значения поля ввода даты на daysOffset дней */
        function changeDatePickerBy(input, daysOffset) {
            var dateFormat = input.datepicker('option', 'dateFormat');
            var date = new Date();
            try {
                date = $.datepicker.parseDate(dateFormat, input.val());
                date.setDate(date.getDate() + daysOffset);
            } catch (e) {
                date = new Date();
            }
            input.datepicker('setDate', date);
        }

        $("#setPrevDay").click(function () {
            changeDatePickerBy($('#dateFilterOneDay'), -1);
            refreshData();
        });
        $("#setNextDay").click(function () {
            changeDatePickerBy($('#dateFilterOneDay'), +1);
            refreshData();
        });

        /** Перезагружает таблицу истории вывода денежных средств */
        function reloadMoneyOutHistoryGrid() {
            $('#tableAccountMoneyOut')
                .jqGrid('setGridParam', {datatype: "json"})
                .jqGrid('setGridParam', {url: "/private/moneyOutHistory"})
                .trigger("reloadGrid");
        }

        /**
         * Форма заявки на вывод денежных средств.
         */
        var ua = navigator.userAgent.toLowerCase();
        var isChrome = (ua.indexOf("chrome") != -1);
        $("#moneyOut").dialog({
            autoOpen: false,
            width: 450,
            height: 'auto',
            resizable: false,
            modal: !isChrome,
            title: 'Заявка на вывод средств',
            open: function () {
                var summ = Math.round(window.account_data.accountSumm - 0.5).toString();
                $("#moneyOut_errorMessage").html('');
                $("#moneyOut_summ").val(summ).focus();
                $("#moneyOut_summ_r").val(summ).focus();
                $("#moneyOut_summ_u").val(summ).focus();
                $("#moneyOut_yandexSumm").val(summ).focus();
                $("#moneyOut_cardSumm").val(summ).focus();
                $("#moneyOut_cardSumm_pb_ua").val(summ).focus();
                $("#moneyOut_cardSumm_pb_us").val(summ).focus();
                $("#moneyOut_cashSumm").val(summ).focus();
                $("#moneyOut_facturaSumm").val(summ).focus();
                $("#moneyOut_comment").val('');
                $.getJSON('/private/lastMoneyOutDetails', function (data) {
                    if (data.error) {
                        return;
                    }
                    var moneyOut_paymentType = $("#moneyOut_paymentType");
                    switch (data.paymentType) {
                        case 'factura':
                            moneyOut_paymentType.val(data.paymentType);
                            $("#moneyOut_facturaContact").val(data.contact);
                            $("#moneyOut_facturaPhone").val(data.phone);
                            break;
                        case 'webmoney_z':
                            moneyOut_paymentType.val(data.paymentType);
                            $("#moneyOut_webmoneyLogin").val(data.webmoneyLogin);
                            $("#moneyOut_webmoneyAccountNumber").val(data.webmoneyAccount);
                            $("#moneyOut_phone").val(data.phone);
                            break;
                        case 'webmoney_r':
                            moneyOut_paymentType.val(data.paymentType);
                            $("#moneyOut_webmoneyLogin_r").val(data.webmoneyLogin);
                            $("#moneyOut_webmoneyAccountNumber_r").val(data.webmoneyAccount);
                            $("#moneyOut_phone_r").val(data.phone);
                            break;
                        case 'webmoney_u':
                            moneyOut_paymentType.val(data.paymentType);
                            $("#moneyOut_webmoneyLogin_u").val(data.webmoneyLogin);
                            $("#moneyOut_webmoneyAccountNumber_u").val(data.webmoneyAccount);
                            $("#moneyOut_phone_u").val(data.phone);
                            break;
                        case 'card':
                            moneyOut_paymentType.val(data.paymentType);
                            $("#moneyOut_cardBank").val(data.bank);
                            $("#moneyOut_cardType").val(data.cardType);
                            $("#moneyOut_cardCurrency").val(data.cardCurrency);
                            $("#moneyOut_cardNumber").val(data.cardNumber);
                            $("#moneyOut_cardName").val(data.cardName);
                            $("#moneyOut_cardMonth").val(data.expire_month);
                            $("#moneyOut_cardYear").val(data.expire_year);
                            $("#moneyOut_cardBankMFO").val(data.bank_MFO);
                            $("#moneyOut_cardBankOKPO").val(data.bank_OKPO);
                            $("#moneyOut_cardBankTransitAccount").val(data.bank_TransitAccount);
                            $("#moneyOut_cardPhone").val(data.phone);
                            break;
                        case 'cash':
                            moneyOut_paymentType.val(data.paymentType);
                            $("#moneyOut_cashPhone").val(data.cashPhone);
                            break;
                        case 'card_pb_ua':
                            moneyOut_paymentType.val(data.paymentType);
                            $("#moneyOut_cardType_pb_ua").val(data.cardType);
                            $("#moneyOut_cardCurrency_pb_ua").val(data.cardCurrency);
                            $("#moneyOut_cardNumber_pb_ua").val(data.cardNumber);
                            $("#moneyOut_cardName_pb_ua").val(data.cardName);
                            $("#moneyOut_cardMonth_pb_ua").val(data.expire_month);
                            $("#moneyOut_cardYear_pb_ua").val(data.expire_year);
                            $("#moneyOut_cardPhone_pb_ua").val(data.phone);
                            break;
                        case 'card_pb_us':
                            moneyOut_paymentType.val(data.paymentType);
                            $("#moneyOut_cardType_pb_us").val(data.cardType);
                            $("#moneyOut_cardCurrency_pb_us").val(data.cardCurrency);
                            $("#moneyOut_cardNumber_pb_us").val(data.cardNumber);
                            $("#moneyOut_cardName_pb_us").val(data.cardName);
                            $("#moneyOut_cardMonth_pb_us").val(data.expire_month);
                            $("#moneyOut_cardYear_pb_us").val(data.expire_year);
                            $("#moneyOut_cardPhone_pb_us").val(data.phone);
                            break;
                        default:
                            break; 	// unknown method
                    }
                    showRightMoneyOutBlock();
                });
            },
            buttons: {
                'Отправить заявку': function () {
                    $('#moneyOut_form').ajaxSubmit({
                        dataType: 'json',
                        beforeSubmit: function () {
                            $("#moneyOut_wait").show();
                        },
                        success: function (reply) {
                            if (reply.error) {
                                if (reply.error_type === "authorizedError") {
                                    window.location.replace("/");
                                }
                                else if (reply.msg) {
                                    $("#moneyOut_errorMessage").html(reply.msg);
                                }
                                else {
                                    $("#moneyOut_errorMessage").html("Неизвестная ошибка.");
                                }
                            }
                            else {
                                $("#moneyOut").dialog('close');
                                $("<div>" +
                                    "<span style=\"float:left; margin:0 7px 50px 0;\"><img src=\"/img/info-icon.png\" /></span>" +
                                    "<b>Заявка успешно принята!</b><br/>" +
                                    "<p>На Ваш e-mail в течение нескольких часов поступит письмо со ссылкой подтверждения данной заявки. " +
                                    "Заявка должна быть одобрена в течение трёх дней.</p>" +
                                    "<p>Внимание!" +
                                    "Если в течение трех часов на Ваш e-mail не пришло письмо, посмотрите, пожалуйста, в спаме." +
                                    "Если письмо не обнаружено ни во входящих письмах, ни в спаме, обратитесь, пожалуйста, к своему менеджеру.<p></div>").dialog({
                                    modal: true,
                                    resizable: false,
                                    buttons: {
                                        OK: function () {
                                            reloadMoneyOutHistoryGrid();
                                            $(this).dialog('close');
                                        }
                                    }
                                });
                            }
                        },
                        complete: function () {
                            $("#moneyOut_wait").hide();
                        }
                    });
                },
                'Отмена': function () {
                    $(this).dialog('close');
                    $("#removeUploadFactura").hide();
                    $("#uploadFactura").show();
                    $('#factura_files').text('');
                    $.getJSON("/private/removeUploadFactura?location=" + $("#moneyOut_facturaLocation").val());
                }
            }
        });


        $(".linkMoneyOut").click(function () {
            $("#moneyOut").dialog('open');
            var val = $("#moneyOut_paymentType").val();
            var moneyOut_cash = $("#moneyOut_cash");
            var moneyOut_yandex = $("#moneyOut_yandex");
            var moneyOut_card = $("#moneyOut_card");
            var moneyOut_card_pb_ua = $("#moneyOut_card_pb_ua");
            var moneyOut_card_pb_us = $("#moneyOut_card_pb_us");
            var moneyOut_webmoney = $("#moneyOut_webmoney");
            var moneyOut_webmoney_r = $("#moneyOut_webmoney_r");
            var moneyOut_webmoney_u = $("#moneyOut_webmoney_u");
            var moneyOut_factura = $("#moneyOut_factura");
            var moneyOut_errorMessage = $("#moneyOut_errorMessage");
            var moneyOut_linkHelp = $("#moneyOut_linkHelp");
            moneyOut_cash.hide();
            moneyOut_yandex.hide();
            moneyOut_card.hide();
            moneyOut_card_pb_ua.hide();
            moneyOut_card_pb_us.hide();
            moneyOut_webmoney.hide();
            moneyOut_webmoney_r.hide();
            moneyOut_webmoney_u.hide();
            moneyOut_factura.hide();
            moneyOut_errorMessage.html('');
            moneyOut_linkHelp.hide();
            switch (val) {
                case 'card':
                    moneyOut_card.show();
                    break;
                case 'cash':
                    moneyOut_cash.show();
                    break;
                case 'card_pb_ua':
                    moneyOut_card_pb_ua.show();
                    break;
                case 'card_pb_us':
                    moneyOut_card_pb_us.show();
                    break;
                case 'webmoney_z':
                    moneyOut_webmoney.show();
                    moneyOut_linkHelp.show();
                    break;
                case 'webmoney_r':
                    moneyOut_webmoney_r.show();
                    moneyOut_linkHelp.show();
                    break;
                case 'webmoney_u':
                    moneyOut_webmoney_u.show();
                    moneyOut_linkHelp.show();
                    break;
                case 'factura' :
                    moneyOut_factura.show();
                    break;
                default:
                    moneyOut_webmoney.show();
                    moneyOut_linkHelp.show();
                    break;
            }
        });


        $('.dialog').find('input').keypress(function (e) {
            if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {
                $(this).parent().parent().parent().parent().find('.ui-dialog-buttonpane').find('button:first').click();
                /* Assuming the first one is the action button */
                return false;
            }
        });


        /**
         * Диалог заявки на регистрацию нового домена
         */
        $("#dialogRegisterDomain").dialog({
            modal: true,
            autoOpen: false,
            resizable: false,
            buttons: {
                'Отправить заявку': function () {
                    $("#formRegisterDomain").ajaxSubmit({
                        dataType: 'json',
                        beforeSubmit: function () {
                            $("#registerDomain_errorMessage").html('');
                            $('#registerDomain_wait').show();
                        },
                        success: function (reply) {
                            if (reply.error === false) {
                                $('#dialogRegisterDomain').dialog('close');
                                $("<p>Заявка успешно принята!</p>").dialog({
                                    modal: true,
                                    resizable: false,
                                    buttons: {
                                        OK: function () {
                                            $(this).dialog('close');
                                        }
                                    }
                                });
                                // перезагрузить таблицу
                                window.tableInformersReload();

                            }
                            else if (reply.error) {
                                if (reply.error_type === "authorizedError") {
                                    {window.location.replace("/main/index");}
                                }
                                else {
                                    var message = '';
                                    if (reply.msg) {
                                        message = reply.msg;
                                    }
                                    else {
                                        message = 'Неизвестная ошибка подачи заявки. Попробуйте позже.';
                                    }
                                    $("#registerDomain_errorMessage").html(message);
                                }
                            }
                        },
                        complete: function () {
                            $('#registerDomain_wait').hide();
                        }
                    });
                }
            }
        });
        /**
         * Диалог заявки на регистрацию нового домена
         */
        $("#dialogRemoveDomain").dialog({
            modal: true,
            autoOpen: false,
            resizable: false,
            buttons: {
                'Удалить сайт': function () {
                    $("#formRemoveDomain").ajaxSubmit({
                        dataType: 'json',
                        beforeSubmit: function () {
                            $("#removeDomain_errorMessage").html('');
                            $('#removeDomain_wait').show();
                        },
                        success: function (reply) {
                            if (reply.error === false) {
                                var d = $("#formRemoveDomain option:selected").val();
                                window.remove_domains.remove(d);
                                $('#dialogRemoveDomain').dialog('close');
                                $("<p>Сайт успешно удален!</p>").dialog({
                                    modal: true,
                                    resizable: false,
                                    buttons: {
                                        OK: function () {
                                            $(this).dialog('close');
                                        }
                                    }
                                });
                                // перезагрузить таблицу
                                window.tableInformersReload();

                            }
                            else if (reply.error) {
                                if (reply.error_type === "authorizedError")
                                {window.location.replace("/main/index");}
                                else {
                                    var message = '';
                                    if (reply.msg) {
                                        message = reply.msg;
                                    }
                                    else {
                                        message = 'Неизвестная ошибка удаления сайта. Попробуйте позже.';
                                    }
                                    $("#removeDomain_errorMessage").html(message);
                                }
                            }
                        },
                        complete: function () {
                            $('#removeDomain_wait').hide();
                        }
                    });
                }
            }
        });

        $("#dialogRemoveBlock").dialog({
            modal: true,
            autoOpen: false,
            resizable: false,
            buttons: {
                'Удалить блок': function () {
                    $("#formRemoveBlock").ajaxSubmit({
                        dataType: 'json',
                        beforeSubmit: function () {
                            $("#removeBlock_errorMessage").html('');
                            $('#removeBlock_wait').show();
                        },
                        success: function (reply) {
                            if (reply.error === false) {
                                $('#dialogRemoveBlock').dialog('close');
                                $("<p>Блок успешно удален!</p>").dialog({
                                    modal: true,
                                    resizable: false,
                                    buttons: {
                                        OK: function () {
                                            $(this).dialog('close');
                                        }
                                    }
                                });
                                // перезагрузить таблицу
                                window.tableInformersReload();

                            }
                            else if (reply.error) {
                                if (reply.error_type === "authorizedError") {
                                    window.location.replace("/main/index");
                                }
                                else {
                                    var message = '';
                                    if (reply.msg) {
                                        message = reply.msg;
                                    }
                                    else {
                                        message = 'Неизвестная ошибка удаления сайта. Попробуйте позже.';
                                    }
                                    $("#removeBlock_errorMessage").html(message);
                                }
                            }
                        },
                        complete: function () {
                            $('#removeBlock_wait').hide();
                            $('#dialogRemoveDomain').dialog('close');
                        }
                    });
                }
            }
        });
        /**
         * Диалог отмены заявки на вывод средств
         */
        $("#dialogCancelRequest").dialog({
            autoOpen: false,
            modal: true,
            buttons: {
                "Да": function () {
                    var table = $("#tableAccountMoneyOut");
                    var id = table.jqGrid('getGridParam', 'selrow');
                    var token = document.getElementById('token').value;
                    $.getJSON("/private/moneyOutRemove",
                        {
                            id: id,
                            token: token
                        },
                        function (result) {
                            if (result) {
                                if (result.error_type === 'authorizedError') {
                                    window.location.replace("/main/index");
                                }
                                else {
                                    reloadMoneyOutHistoryGrid();
                                    $("#dialogCancelRequest").dialog("close");
                                }
                            }
                        }
                    );
                    $("#btnRejectMoneyOut").attr('disabled', true);
                },
                "Отмена": function () {
                    $(this).dialog("close");
                }
            }
        });
//----------------------------------------

        $.getJSON('/private/all_account_data', function (data) {
            if (data.error) {
                window.location.replace("/");
            }
            window.account_data = data;

            prepareUi();
            $("#tabs").css("visibility", "visible");
            showRightMoneyOutBlock();
            window.tableInformersReload();


        }, function () {
            window.alert('failes');
        });
        window.tableInformersReload = function () {
            if (window.remove_domains && window.remove_domains < 1) {
                $("#RemoveDomain").hide();
                $("#CreateAdvertise").hide();
            }
            else{
                $("#RemoveDomain").show();
                $("#CreateAdvertise").show();
            }
            if (window.domains && window.domains.rows && window.domains.rows.length < 1) {
                $("#tableExistingInformers").hide();
                $("#tableInformers").hide();
            }
            else{
                $("#tableExistingInformers").show();
                $("#tableInformers").show();
            }
            if (window.advertiseList.length < 1) {
                $("#startwork").css({display: 'block'});
                $("#linkinformers").click();
            }
            $("#tableExistingInformers").trigger("reloadGrid");
        };


        window.ytt.event(['1', '2', '3'], 'remove');

    });	// end onDocumentReady

}(jQuery) );