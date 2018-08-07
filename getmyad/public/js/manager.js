window.CheckUser = function () {
    "use strict";
            if (document.cookie.indexOf('getmyad=') === -1){
                window.location.replace('/');
            }
};
var userDetailsTabs = false;
var ManagerUI = function () {
    "use strict";
    window.CheckUser();
    $(document).ready(function () {
        /**
         * Проверка текстового поля на допустимое число
         */
        // function checkFloat(o) {
        //     return o && /^-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?$/.test(o.val());
        // }


        /**
         * Создание пользовательского интерфейса
         */
        function prepareUi() {
            $("#tabs").tabs({
                add: function (
                    event,
                    ui
                ) {
                    $('#tabs').tabs('select', '#' + ui.panel.id);
                    var match = ui.tab.hash.match('#user-details:(.+)');
                    if (match && match[1]) {
                        var login = match[1].replace(/_/g, '.');
                        var tabs = $.tabs();
                        $(ui.panel).append(tabs);
                    }
                }
            });
            $("#tabs2").tabs();

            /**
             * Форма заявки на вывод денежных средств.
             */
            $("#moneyOut").dialog({
                autoOpen: false,
                modal: true,
                width: 450,
                height: 'auto',
                resizable: false,
                title: 'Заявка на вывод средств',
                open: function (
                    event,
                    ui
                ) {
                    $("#moneyOut_summ").val(Math.round(0).toString()).focus();
                    $("#moneyOut_comment").val('');
                },
                buttons: {
                    'Отмена': function () {
                        $(this).dialog('close');
                    },
                    'Отправить заявку': function () {
                        $('#moneyOut_form').ajaxSubmit({
                            dataType: 'json',
                            beforeSubmit: function () {
                                $("#moneyOut_wait").show();
                            },
                            success: function (reply) {
                                if (reply.error) {
                                    if (reply.error_type == "authorizedError"){
                                        window.location.replace("/main/index");
                                    }
                                    else if (reply.msg) {
                                        $("#moneyOut_errorMessage").html(reply.msg);
                                    }
                                    else{
                                        $("#moneyOut_errorMessage").html("Неизвестная ошибка.");
                                    }
                                }
                                else {
                                    $("#moneyOut").dialog('close');
                                    $("<p>Заявка успешно принята!</p>").dialog({
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
                    }
                }
            });

            $(".linkMoneyOut").click(function () {
                $("#moneyOut").dialog('open');
            });


            // Диалог одобрения заявки
            $("#dialogMoneyOutApprove").dialog({
                autoOpen: false,
                modal: true,
                width: 'auto',
                buttons: {
                    'Да': function () {
                        $.getJSON("/manager/approveMoneyOut", {
                            user: $("#dialogMoneyOutApprove_user").html(),
                            date: $("#dialogMoneyOutApprove_date").html(),
                            protectionCode: $('#dialogMoneyOutApprove > input[name="protectionCode"]')[0].value,
                            protectionPeriod: $('#dialogMoneyOutApprove > input[name="protectionPeriod"]')[0].value,
                            approved: 'true',
                            token: window.token
                        }, function (data) {
                            if (data.error) {
                                if (data.error_type === "authorizedError")
                                {
                                    window.location.replace("/main/index");
                                }
                                else if (data.msg) {
                                    alert(data.msg);
                                    return;
                                }
                                else {
                                    alert("Неизвестная ошибка.");
                                    return;
                                }
                            }
                            else {
                                $('#dialogMoneyOutApprove').dialog('close');
                                $('#tableMoneyOutRequest').trigger('reloadGrid');
                            }
                        });
                    },
                    'Нет': function () {
                        $(this).dialog('close');
                    }
                }
            });

            // Диалог разрешения заявки
            $("#dialogMoneyOutAgree").dialog({
                autoOpen: false,
                modal: true,
                buttons: {
                    'Да': function () {
                        $.getJSON("/manager/agreeMoneyOut", {
                            user: $("#dialogMoneyOutAgree_user").html(),
                            date: $("#dialogMoneyOutAgree_date").html(),
                            approved: 'true',
                            token: window.token
                        }, function (data) {
                            if (data.error) {
                                if (data.error_type === "authorizedError"){
                                    window.location.replace("/main/index");
                                }
                                else if (data.msg) {
                                    alert(data.msg);
                                    return;
                                }
                                else {
                                    alert("Неизвестная ошибка.");
                                    return;
                                }
                            }
                            else {
                                $('#dialogMoneyOutAgree').dialog('close');
                                $('#tableMoneyOutRequest').trigger('reloadGrid');
                            }
                        });
                    },
                    'Нет': function () {
                        $(this).dialog('close');
                    }
                }
            });

            $("#dialogMoneyOutUpdateProtectionCode").dialog({
                autoOpen: false,
                modal: true,
                buttons: {
                    'OK': function () {
                        $.getJSON("/manager/updateProtection", {
                            user: $("#dialogMoneyOutUpdateProtectionCode_user").html(),
                            date: $("#dialogMoneyOutUpdateProtectionCode_date").html(),
                            protectionCode: $('#dialogMoneyOutUpdateProtectionCode > input[name="protectionCode"]')[0].value,
                            protectionPeriod: $('#dialogMoneyOutUpdateProtectionCode > input[name="protectionPeriod"]')[0].value,
                            token: window.token
                        }, function (data) {
                            if (data.error) {
                                if (data.error_type === "authorizedError"){
                                    window.location.replace("/main/index");
                                    }
                                else if (data.msg) {
                                    alert(data.msg);
                                    return;
                                }
                                else {
                                    alert("Неизвестная ошибка.");
                                    return;
                                }
                            }
                            else {
                                $('#dialogMoneyOutUpdateProtectionCode').dialog('close');
                                $('#tableMoneyOutRequest').trigger('reloadGrid');
                            }
                        });
                    },
                    'Нет': function () {
                        $(this).dialog('close');
                    }
                }
            });

            // Диалог блокировки менеджера
            $('#dialogBlockManager').dialog({
                autoOpen: false,
                modal: true,
                buttons: {
                    'Да': function () {
                        $.getJSON("/manager/block", {
                            manager: $("#dialogBlockManager_manager").html(),
                            token: window.token
                        }, function (data) {
                            $("#managersSummary").trigger("reloadGrid");
                            $('#dialogBlockManager').dialog('close');
                        });
                    },
                    'Нет': function () {
                        $(this).dialog('close');
                    }
                }
            });

            // Таблица менеджеров
            $("#managersSummary").jqGrid({
                url: '/manager/managersSummary',
                datatype: 'json',
                mtype: 'GET',
                loadComplete: function () {
                    $('#managersSummary .actionLink').click(openUserDetails);
                },
                colNames: [
                    'Менеджер',
                    'Статус',
                    'Тип'
                ],
                colModel: [
                    {
                        name: 'manager',
                        index: 'manager',
                        width: 150,
                        align: 'center',
                        sortable: true,
                        classes: 'actionLink'
                    },
                    {
                        name: 'status',
                        index: 'status',
                        width: 90,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'type',
                        index: 'type',
                        width: 100,
                        align: 'center',
                        sortable: true
                    }
                ],
                viewrecords: true,
                caption: "Сводная информация по менеджерам",
                gridview: true,
                rownumbers: true,
                height: 'auto',
                toolbar: [
                    true,
                    'top'
                ],
                hiddengrid: true,
                beforeSelectRow: function (
                    rowid,
                    e
                ) {
                    if (rowid) {
                        blockManagerButton.attr('disabled', false);
                    }
                    return true;
                }
            });


            var blockManagerButton = $('<input type="button" value="Блокировать" />');
            blockManagerButton.attr('disabled', true).click(function () {
                var id = $("#managersSummary").jqGrid('getGridParam', 'selrow');
                if (!id)
                {
                    return;
                }
                var row = $("#managersSummary").jqGrid('getRowData', id);
                $("#dialogBlockManager_manager").html(row.manager);
                $("#dialogBlockManager").dialog('open');
            });
            $("#t_managersSummary").append(blockManagerButton);


            // Таблица цен за уникального посетителя
            $("#tableClickCost").jqGrid({
                url: '/manager/currentClickCost?onlyActive=true',
                datatype: 'json',
                mtype: 'get',
                colNames: [
                    'Аккаунт',
                    'Процент цены</br>за клик',
                    'Минимальная цена</br>за клик',
                    'Максимальная цена</br>за клик'
                ],
                colModel: [
                    {
                        name: 'title',
                        index: 'title',
                        sortable: false,
                        width: 150,
                        align: 'center'
                    },
                    {
                        name: 'click_percent',
                        index: 'click_percent',
                        sortable: false,
                        width: 100,
                        align: 'center'
                    },
                    {
                        name: 'click_cost_min',
                        index: 'click_cost_min',
                        sortable: false,
                        width: 125,
                        align: 'center'
                    },
                    {
                        name: 'click_cost_max',
                        index: 'click_cost_max',
                        sortable: false,
                        width: 125,
                        align: 'center'
                    }
                ],
                caption: "Текущие цены за уникального посетителя",
                rownumbers: false,
                sortable: false,
                hiddengrid: true,
                rowNum: 900,
                toolbar: [
                    true,
                    'top'
                ],
                height: '400px',
                subGrid: true,
                subGridRowExpanded: function (
                    subgrid_id,
                    row_id
                ) {
                    var subgrid_table_id, pager_id;
                    subgrid_table_id = subgrid_id + "_t";
                    pager_id = "p_" + subgrid_table_id;
                    $("#" + subgrid_id).html("<table id='" + subgrid_table_id + "' class='scroll'></table><div id='" + pager_id + "' class='scroll'></div>");
                    var req = $(this).getRowData(row_id);
                    $("#" + subgrid_table_id).jqGrid({
                        url: ['/manager/currentClickCost?',
                              'subgrid=true&id=', req.title,
                              '&click_percent=', req.click_percent,
                              '&click_cost_min=', req.click_cost_min,
                              '&click_cost_max=', req.click_cost_max
                        ].join(''),
                        datatype: 'json',
                        mtype: 'get',
                        colNames: [
                            'Рекламный блок',
                            'Процент цены</br>за клик',
                            'Минимальная цена</br>за клик',
                            'Максимальная цена</br>за клик'
                        ],
                        colModel: [
                            {
                                name: 'btitle',
                                index: 'btitle',
                                align: 'center',
                                sortable: false,
                                width: 150
                            },
                            {
                                name: 'bclick_percent',
                                index: 'bclick_percent',
                                sortable: false,
                                width: 100,
                                align: 'center'
                            },
                            {
                                name: 'bclick_cost_min',
                                index: 'bclick_cost_min',
                                sortable: false,
                                width: 125,
                                align: 'center'
                            },
                            {
                                name: 'bclick_cost_max',
                                index: 'bclick_cost_max',
                                sortable: false,
                                width: 125,
                                align: 'center'
                            }
                        ],
                        rownumbers: false,
                        loadonce: true,
                        sortable: false,
                        hiddengrid: true,
                        autowidth: true,
                        rowNum: 900,
                        height: '100%'
                    });
                },
                pager: "#pagerCurrentClickCost"
            });


            // Фильтр, скрывающий неактивные аккаунты из таблицы цен
            var filterOnlyActiveCost = $('<input type="checkbox" value="filterOnlyActiveCost" checked>Только активные</input>');
            filterOnlyActiveCost.click(function () {
                function reloadClickCostGrid() {
                    $('#tableClickCost').jqGrid('setGridParam', {
                        datatype: "json"
                    }).jqGrid('setGridParam', {
                        url: "/manager/currentClickCost?onlyActive=" + filterOnlyActiveCost.is(":checked")
                    }).trigger("reloadGrid");
                }

                reloadClickCostGrid();

            });
            $("#t_tableClickCost").append(filterOnlyActiveCost);


            // Таблица заявок на вывод средств
            $("#tableMoneyOutRequest").jqGrid({
                url: '/manager/dataMoneyOutRequests',
                datatype: 'json',
                mtype: 'get',
                loadComplete: function () {
                    $('#tableMoneyOutRequest .actionLink').click(openUserDetails);
                },
                colNames: [
                    'Пользователь',
                    'Дата',
                    'Сумма заявки',
                    'Сумма на счету',
                    'Доступно к выводу',
                    'Подтверждено',
                    'Разрешено',
                    'Оплачено',
                    'Телефон',
                    'Оплата',
                    'Код протекции',
                    'Истекает',
                    'Примечания'
                ],
                colModel: [
                    {
                        name: 'user',
                        index: 'user',
                        width: 115,
                        align: 'center',
                        sortable: true,
                        classes: 'actionLink pseudoLink'
                    },
                    {
                        name: 'date',
                        index: 'date',
                        width: 70,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'summ',
                        index: 'summ',
                        width: 70,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'summin',
                        index: 'summin',
                        width: 70,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'summout',
                        index: 'summout',
                        width: 70,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'user_confirmed',
                        index: 'user_confirmed',
                        width: 100,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'manager_agreed',
                        index: 'manager_agreed',
                        width: 80,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'approved',
                        index: 'approved',
                        width: 80,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'phone',
                        index: 'phone',
                        width: 100,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'paymentType',
                        index: 'paymentType',
                        width: 90,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'protectionCode',
                        index: 'protectionCode',
                        width: 100,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'protectionDate',
                        index: 'protectionDate',
                        width: 100,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'comments',
                        index: 'comments',
                        width: 400,
                        align: 'left',
                        sortable: true
                    }
                ],
                caption: "Заявки на вывод средств",
                rownumbers: true,
                height: '100%',
                rownumWidth: 20,
                rowNum: 10,
                hiddengrid: false,
                autowidth: true,
                pager: "#pagerMoneyOutRequest",
                forceFit: true,
                toolbar: [
                    true,
                    'top'
                ],
                beforeSelectRow: function (
                    rowid,
                    e
                ) {
                    if (!rowid)
                        return false;
                    var row = $("#tableMoneyOutRequest").jqGrid('getRowData', rowid);
                    buttonApproveMoneyOutRequest.attr('disabled', row.approved === 'Да' ||
                        row.user_confirmed !== 'Да' ||
                        row.manager_agreed !== 'Да');
                    buttonAgreeMoneyOutRequest.attr('disabled', row.approved === 'Да' ||
                        row.manager_agreed === 'Да');


                    buttonUpdateProtectionCodeMoneyOutRequest.attr('disabled', ((row.approved !== 'Да') ||
                        (row.user_confirmed !== 'Да') ||
                        (row.manager_agreed !== 'Да')) ||
                        ((row.paymentType !== 'webmoney_z') &&
                            (row.paymentType !== 'yandex')));

                    return true;
                }
            });

            var toolbar = $("#t_tableMoneyOutRequest");

            var buttonApproveMoneyOutRequest = $("<input type='button' value='Одобрить заявку' />");
            buttonApproveMoneyOutRequest.attr('disabled', true).click(function () {
                var table = $("#tableMoneyOutRequest");
                var id = table.jqGrid('getGridParam', 'selrow');
                if (!id){
                    return;
                }
                var row = table.jqGrid('getRowData', id);
                $('#dialogMoneyOutApprove_summ').html(row.summ);
                $('#dialogMoneyOutApprove_user').html(row.user);
                $('#dialogMoneyOutApprove_date').html(row.date);

                if (row.paymentType === 'card' || row.paymentType === 'счёт-фактура') {
                    $('.protection_code_info').hide();
                }
                else {
                    $('.protection_code_info').show();
                }
                $('#information_money_approve').empty();
                $(row.comments).appendTo($('#information_money_approve'));

                $('#dialogMoneyOutApprove > input[name="protectionCode"]')[0].value = '';
                $('#dialogMoneyOutApprove > input[name="protectionPeriod"]')[0].value = '';

                $("#dialogMoneyOutApprove").dialog('open');
                console.log(row);
            }).appendTo(toolbar);

            var buttonAgreeMoneyOutRequest = $("<input type='button' value='Разрешить' />");
            buttonAgreeMoneyOutRequest.attr('disabled', true).click(function () {
                var table = $("#tableMoneyOutRequest");
                var id = table.jqGrid('getGridParam', 'selrow');
                if (!id)
                    return;
                var row = table.jqGrid('getRowData', id);
                $('#dialogMoneyOutAgree_summ').html(row.summ);
                $('#dialogMoneyOutAgree_user').html(row.user);
                $('#dialogMoneyOutAgree_date').html(row.date);
                $("#dialogMoneyOutAgree").dialog('open');
            }).appendTo(toolbar);

            var buttonUpdateProtectionCodeMoneyOutRequest = $("<input type='button' value='Обновить код протекции' />");
            buttonUpdateProtectionCodeMoneyOutRequest.attr('disabled', true).click(function () {
                var table = $("#tableMoneyOutRequest");
                var id = table.jqGrid('getGridParam', 'selrow');
                if (!id){
                    return;
                }
                var row = table.jqGrid('getRowData', id);
                $('#dialogMoneyOutUpdateProtectionCode_summ').html(row.summ);
                $('#dialogMoneyOutUpdateProtectionCode_user').html(row.user);
                $('#dialogMoneyOutUpdateProtectionCode_date').html(row.date);
                $("#dialogMoneyOutUpdateProtectionCode").dialog('open');
            }).appendTo(toolbar);

            // Таблица о сводной фин статистике по дням
            $("#tableOverallSumSummary").jqGrid({
                url: '/manager/overallSumSummaryByDays',
                datatype: 'json',
                mtype: 'GET',
                colNames: [
                    '',
                    'Дата',
                    'Аккаунтов<br/>(Акт Аккаунтов/Сайтов)',
                    'Средняя цена',
                    'Процент<br/>отчисления',
                    'Начислено<br/>партнёрам',
                    'Отчислено<br/>Adload',
                    'Осталось'
                ],
                colModel: [
                    {
                        name: 'color',
                        index: 'color',
                        width: 75,
                        align: 'center',
                        sortable: false,
                        hidden: true
                    },
                    {
                        name: 'date',
                        index: 'date',
                        width: 75,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'AccountSiteCount',
                        index: 'AccountSiteCount',
                        width: 145,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'click_profit',
                        index: 'click_profit',
                        width: 85,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'profit2',
                        index: 'profit2',
                        width: 85,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'profit1',
                        index: 'profit1',
                        width: 85,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'profit3',
                        index: 'profit3',
                        width: 85,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'profit4',
                        index: 'profit4',
                        width: 85,
                        align: 'center',
                        sortable: false
                    }
                ],
                caption: "Общая статистика движения средств",
                gridview: true,
                rowNum: 10,
                rownumbers: false,
                height: '100%',
                rowList: [
                    10,
                    15,
                    20,
                    30,
                    100
                ],
                sortname: 'date',
                sortorder: 'desc',
                autowidth: true,
                pager: '#pagerOverallSumSummary',
                gridComplete: function () {
                    var _rows = $(".jqgrow");
                    for (var i = 0; i < _rows.length; i++) {
                        if (_rows[i].childNodes[0].textContent > 4) {
                            _rows[i].attributes["class"].value += " sunday";
                        }
                    }
                }
            });


            // Таблица о сводной статистике по дням
            $("#tableOverallSummary").jqGrid({
                url: '/manager/overallSummaryByDays',
                datatype: 'json',
                mtype: 'GET',
                colNames: [
                    '',
                    'Дата',
                    'Аккаунтов<br/>(Акт Аккаунтов/Сайтов)',
                    'Показы блоков</br>не гарантированные',
                    'Показы<br/>блоков',
                    'Клики<br/>уникальные',
                    'CTR<br/>Блоков',
                    'Процент видимых показов',
                    'Социал<br/>клики',
                    'Ср.время</br>до клика',
                    'Подозри</br>тельные</br>клики',
                    'Отфильтро</br>ванные</br>клики',
                    'Забаненые</br>клики'
                ],
                colModel: [
                    {
                        name: 'color',
                        index: 'color',
                        width: 75,
                        align: 'center',
                        sortable: false,
                        hidden: true
                    },
                    {
                        name: 'date',
                        index: 'date',
                        width: 75,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'AccountSiteCount',
                        index: 'AccountSiteCount',
                        width: 145,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'impressions_block_not_valid',
                        index: 'impressions_block_not_valid',
                        width: 70,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'impressions_block',
                        index: 'impressions_block',
                        width: 70,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'clicksUnique',
                        index: 'clicksUnique',
                        width: 70,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'ctr_block',
                        index: 'ctr_block',
                        width: 70,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'viewPort',
                        index: 'viewPort',
                        width: 70,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'social_clicks',
                        index: 'social_clicks',
                        width: 70,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'view_seconds_avg',
                        index: 'view_seconds_avg',
                        width: 70,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'click_warning',
                        index: 'click_warning',
                        width: 50,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'click_filtered',
                        index: 'click_filtered',
                        width: 50,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'click_bann',
                        index: 'click_bann',
                        width: 50,
                        align: 'center',
                        sortable: true
                    }
                ],
                caption: "Общая статистика",
                gridview: true,
                rowNum: 10,
                rownumbers: false,
                height: '100%',
                rowList: [
                    10,
                    15,
                    20,
                    30,
                    100
                ],
                sortname: 'date',
                sortorder: 'desc',
                pager: '#pagerOverallSummary',
                gridComplete: function () {
                    var _rows = $(".jqgrow");
                    for (var i = 0; i < _rows.length; i++) {
                        if (_rows[i].childNodes[0].textContent > 4) {
                            _rows[i].attributes["class"].value += " sunday";
                        }
                    }
                }
            });

            // Таблица о тизерной сводной статистике по дням
            $("#tableTeaserOverallSummary").jqGrid({
                url: '/manager/overallTeaserSummaryByDays',
                datatype: 'json',
                mtype: 'GET',
                colNames: [
                    '',
                    'Дата',
                    'Аккаунтов<br/>(Акт Аккаунтов/Сайтов)',
                    'Показы Блоков</br> не гарантированные',
                    'Показы<br/>Блоков',
                    'Показы РП</br> не гарантированные',
                    'Показы<br/>РП',
                    'Клики',
                    'Клики<br/>уник.',
                    'Сумма',
                    'Соц. Показы РП</br> не гарантированные',
                    'Соц. Показы<br/>РП',
                    'Соц. Клики',
                    'CTR<br/>РП',
                    'CTR<br/>Блоков',
                    'Цена',
                    'Ср.время</br>до клика'
                ],
                colModel: [
                    {
                        name: 'color',
                        index: 'color',
                        width: 75,
                        align: 'center',
                        sortable: false,
                        hidden: true
                    },
                    {
                        name: 'date',
                        index: 'date',
                        width: 75,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'AccountSiteCount',
                        index: 'AccountSiteCount',
                        width: 145,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'impressions_block_not_valid',
                        index: 'impressions_block_not_valid',
                        width: 105,
                        align: 'center',
                        classes: 'block-column',
                        sortable: false
                    },
                    {
                        name: 'impressions_block',
                        index: 'impressions_block',
                        width: 70,
                        align: 'center',
                        classes: 'block-column',
                        sortable: false
                    },
                    {
                        name: 'impressions_not_valid',
                        index: 'impressions_not_valid',
                        width: 105,
                        align: 'center',
                        classes: 'offer-column',
                        sortable: false
                    },
                    {
                        name: 'impressions',
                        index: 'impressions',
                        width: 70,
                        align: 'center',
                        classes: 'offer-column',
                        sortable: false
                    },
                    {
                        name: 'clicks',
                        index: 'clicks',
                        width: 70,
                        align: 'center',
                        classes: 'offer-column',
                        sortable: false
                    },
                    {
                        name: 'clicksUnique',
                        index: 'clicksUnique',
                        width: 70,
                        align: 'center',
                        classes: 'offer-column',
                        sortable: false
                    },
                    {
                        name: 'profit',
                        index: 'profit',
                        width: 70,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'social_impressions_not_valid',
                        index: 'social_impressions_not_valid',
                        width: 105,
                        align: 'center',
                        classes: 'social-column',
                        sortable: false
                    },
                    {
                        name: 'social_impressions',
                        index: 'social_impressions',
                        width: 70,
                        align: 'center',
                        classes: 'social-column',
                        sortable: false
                    },
                    {
                        name: 'social_clicks',
                        index: 'social_clicks',
                        classes: 'social-column',
                        width: 70,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'ctr',
                        index: 'ctr',
                        width: 70,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'ctr_block',
                        index: 'ctr_block',
                        width: 70,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'click_cost',
                        index: 'click_cost',
                        width: 70,
                        align: 'center',
                        sortable: false
                    },
                    {
                        name: 'view_seconds_avg',
                        index: 'view_seconds_avg',
                        width: 70,
                        align: 'center',
                        sortable: false
                    }
                ],
                caption: "Общая статистика предложений",
                gridview: true,
                rowNum: 10,
                rownumbers: false,
                height: '100%',
                rowList: [
                    10,
                    15,
                    20,
                    30,
                    100
                ],
                sortname: 'date',
                sortorder: 'desc',
                autowidth: true,
                pager: '#pagerTeaserOverallSummary',
                gridComplete: function () {
                    var _rows = $(".jqgrow");
                    for (var i = 0; i < _rows.length; i++) {
                        if (_rows[i].childNodes[0].textContent > 4) {
                            _rows[i].attributes["class"].value += " sunday";
                        }
                    }
                }
            });

            // Таблица с данными об обшем доходе пользователей GetMyAd
            $("#tableUsersSummary").jqGrid({
                datatype: "json",
                url: '/manager/dataUsersSummary',
                loadComplete: function () {
                    $('#tableUsersSummary .actionLink').click(openUserDetails);
                },
                mtype: 'GET',
                colNames: [
                    'Пользователь',
                    'Сегодня',
                    'Вчера',
                    'Позавчера',
                    'За неделю',
                    'За месяц',
                    'За год',
                    'Сумма на счету'
                ],
                colModel: [
                    {
                        name: 'user',
                        index: 'user',
                        width: 150,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'summToday',
                        index: 'summToday',
                        width: 90,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'summYesterday',
                        index: 'summYesterday',
                        width: 90,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'summBeforeYesterday',
                        index: 'summBeforeYesterday',
                        width: 90,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'summWeek',
                        index: 'summWeek',
                        width: 95,
                        align: 'center',
                        sortable: true,
                        hidden: !window.permissionViewAllUserStats
                    },
                    {
                        name: 'summMonth',
                        index: 'summMonth',
                        width: 95,
                        align: 'center',
                        sortable: true,
                        hidden: !window.permissionViewAllUserStats
                    },
                    {
                        name: 'summYear',
                        index: 'summYear',
                        width: 90,
                        align: 'center',
                        sortable: true,
                        hidden: !window.permissionViewAllUserStats
                    },
                    {
                        name: 'summ',
                        index: 'summ',
                        width: 135,
                        align: 'center',
                        sortable: true,
                        hidden: !window.permissionViewAllUserStats
                    }
                ],
                viewrecords: false,
                caption: "Суммарная статистика",
                hiddengrid: true,
                gridview: true,
                rownumbers: true,
                height: 420,
                rownumWidth: 40,
                rowNum: 900,
                footerrow: true,
                userDataOnFooter: true,
                onSortCol: function (
                    index,
                    iCol,
                    sortorder
                ) {
                    $('#tableUsersSummary').jqGrid('setGridParam', {datatype: "json"}).jqGrid('setGridParam',
                        {
                            url: "/manager/dataUsersSummary?sortcol=" + iCol + "&sortreverse=" + sortorder
                        });
                }
            });

            // Таблица с данными об тизерном доходе пользователей GetMyAd
            $("#tableTeaserUsersSummary").jqGrid({
                datatype: "json",
                url: '/manager/dataTeaserUsersSummary',
                loadComplete: function () {
                    $('#tableTeaserUsersSummary .actionLink').click(openUserDetails);
                },
                mtype: 'GET',
                colNames: [
                    'Пользователь',
                    'Сегодня',
                    'Вчера',
                    'Позавчера',
                    'За неделю',
                    'За месяц',
                    'За год',
                    'Средняя цена<br/>за сегодня',
                    'Средняя цена<br/>за вчера',
                    'Средняя цена<br/>за неделю',
                    'CTR Блока<br/>за сегодня',
                    'CTR Блока<br/>за вчера',
                    'CTR Блока<br/>за неделю',
                    'CTR РП<br/>за сегодня',
                    'CTR РП<br/>за вчера',
                    'CTR РП<br/>за неделю'
                ],
                colModel: [
                    {
                        name: 'user',
                        index: 'user',
                        width: 150,
                        align: 'center',
                        sortable: true,
                        classes: 'actionLink'
                    },
                    {
                        name: 'summToday',
                        index: 'summToday',
                        width: 90,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'summYesterday',
                        index: 'summYesterday',
                        width: 90,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'summBeforeYesterday',
                        index: 'summBeforeYesterday',
                        width: 90,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'summWeek',
                        index: 'summWeek',
                        width: 95,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'summMonth',
                        index: 'summMonth',
                        width: 95,
                        align: 'center',
                        sortable: true,
                        hidden: !window.permissionViewAllUserStats
                    },
                    {
                        name: 'summYear',
                        index: 'summYear',
                        width: 90,
                        align: 'center',
                        sortable: true,
                        hidden: !window.permissionViewAllUserStats
                    },
                    {
                        name: 'dayCost',
                        index: 'dayCost',
                        width: 80,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'yesterdayCost',
                        index: 'yesterdayCost',
                        width: 80,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'weekCost',
                        index: 'weekCost',
                        width: 80,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'dayCTR_block',
                        index: 'dayCTR_block',
                        width: 80,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'ydayCTR_block',
                        index: 'ydayCTR_block',
                        width: 80,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'weekCTR_block',
                        index: 'weekCTR_block',
                        width: 80,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'dayCTR',
                        index: 'dayCTR',
                        width: 80,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'ydayCTR',
                        index: 'ydayCTR',
                        width: 80,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'weekCTR',
                        index: 'weekCTR',
                        width: 80,
                        align: 'center',
                        sortable: true
                    }
                ],
                viewrecords: false,
                caption: "Суммарная статистика предложений",
                gridview: true,
                rownumbers: true,
                height: 420,
                rownumWidth: 40,
                rowNum: 900,
                width: 'auto',
                hiddengrid: true,
                footerrow: true,
                userDataOnFooter: true,
                onSortCol: function (
                    index,
                    iCol,
                    sortorder
                ) {
                    $('#tableTeaserUsersSummary').jqGrid('setGridParam', {datatype: "json"}).jqGrid('setGridParam',
                        {
                            url: "/manager/dataTeaserUsersSummary?sortcol=" + iCol + "&sortreverse=" + sortorder
                        });
                }
            });

            // Таблица с данными о количестве показов
            $("#tableUsersImpressions").jqGrid({
                url: '/manager/dataUsersImpressions',
                datatype: 'json',
                loadComplete: function () {
                    $('#tableUsersImpressions .actionLink').click(openUserDetails);
                },
                mtype: 'GET',
                colNames: [
                    'Пользователь',
                    'Сегодня<br/>РП',
                    'Сегодня<br/>Блок',
                    'Вчера<br/>РП',
                    'Вчера<br/>Блок',
                    'Позавчера<br/>РП',
                    'Позавчера<br/>Блок',
                    'За неделю<br/>РП',
                    'За неделю<br/>Блок',
                    'За месяц<br/>РП',
                    'За месяц<br/>Блок',
                    'За год<br/>РП',
                    'За год<br/>Блок'
                ],
                colModel: [
                    {
                        name: 'user',
                        index: 'user',
                        width: 150,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'impToday',
                        index: 'impToday',
                        width: 75,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impToday_block',
                        index: 'impToday_block',
                        width: 75,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impYesterday',
                        index: 'impYesterday',
                        width: 75,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impYesterday_block',
                        index: 'impYesterday_block',
                        width: 75,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impBeforeYesterday',
                        index: 'impBeforeYesterday',
                        width: 75,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impBeforeYesterday_block',
                        index: 'impBeforeYesterday_block',
                        width: 75,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impWeek',
                        index: 'impWeek',
                        width: 80,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impWeek_block',
                        index: 'impWeek_block',
                        width: 80,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impMonth',
                        index: 'impMonth',
                        width: 80,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impMonth_block',
                        index: 'impMonth_block',
                        width: 80,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impYear',
                        index: 'impYear',
                        width: 85,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impYear_block',
                        index: 'impYear_block',
                        width: 85,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    }
                ],
                viewrecords: false,
                caption: "Статистика по количеству показов",
                gridview: true,
                rownumbers: true,
                height: 420,
                rownumWidth: 40,
                rowNum: 900,
                hiddengrid: true,
                footerrow: true,
                userDataOnFooter: true,
                onSortCol: function (
                    index,
                    iCol,
                    sortorder
                ) {
                    $('#tableUsersImpressions').jqGrid('setGridParam', {datatype: "json"}).jqGrid('setGridParam',
                        {
                            url: "/manager/dataUsersImpressions?sortcol=" + iCol + "&sortreverse=" + sortorder
                        });
                }
            });

            // Таблица с данными о количестве показов
            $("#tableTeaserUsersImpressions").jqGrid({
                url: '/manager/dataTeaserUsersImpressions',
                datatype: 'json',
                loadComplete: function () {
                    $('#tableTeaserUsersImpressions .actionLink').click(openUserDetails);
                },
                mtype: 'GET',
                colNames: [
                    'Пользователь',
                    'Сегодня<br/>РП',
                    'Сегодня<br/>Блок',
                    'Вчера<br/>РП',
                    'Вчера<br/>Блок',
                    'Позавчера<br/>РП',
                    'Позавчера<br/>Блок',
                    'За неделю<br/>РП',
                    'За неделю<br/>Блок',
                    'За месяц<br/>РП',
                    'За месяц<br/>Блок',
                    'За год<br/>РП',
                    'За год<br/>Блок'
                ],
                colModel: [
                    {
                        name: 'user',
                        index: 'user',
                        width: 150,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'impToday',
                        index: 'impToday',
                        width: 75,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impToday_block',
                        index: 'impToday_block',
                        width: 75,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impYesterday',
                        index: 'impYesterday',
                        width: 75,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impYesterday_block',
                        index: 'impYesterday_block',
                        width: 75,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impBeforeYesterday',
                        index: 'impBeforeYesterday',
                        width: 75,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impBeforeYesterday_block',
                        index: 'impBeforeYesterday_block',
                        width: 75,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impWeek',
                        index: 'impWeek',
                        width: 80,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impWeek_block',
                        index: 'impWeek_block',
                        width: 80,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impMonth',
                        index: 'impMonth',
                        width: 80,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impMonth_block',
                        index: 'impMonth_block',
                        width: 80,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impYear',
                        index: 'impYear',
                        width: 85,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    },
                    {
                        name: 'impYear_block',
                        index: 'impYear_block',
                        width: 85,
                        align: 'center',
                        formatter: 'integer',
                        sorttype: 'integer',
                        sortable: true
                    }
                ],
                viewrecords: false,
                caption: "Статистика по количеству показов за предложение",
                gridview: true,
                rownumbers: true,
                height: 420,
                rownumWidth: 40,
                rowNum: 900,
                hiddengrid: true,
                footerrow: true,
                userDataOnFooter: true,
                onSortCol: function (
                    index,
                    iCol,
                    sortorder
                ) {
                    $('#tableTeaserUsersImpressions').jqGrid('setGridParam', {datatype: "json"}).jqGrid('setGridParam',
                        {
                            url: "/manager/dataTeaserUsersImpressions?sortcol=" + iCol + "&sortreverse=" + sortorder
                        });
                }
            });

            // Таблица рейтинга рекламных предложений
            $("#tableOfferRating").jqGrid({
                url: '/manager/rating',
                datatype: 'json',
                mtype: 'GET',
                colNames: [
                    'РП',
                    'РК',
                    'Показы',
                    'Клики',
                    'CTR',
                    'Цена',
                    'Рейтинг',
                    'Время обнавления</br>Рейтинга',
                    'Показы<br/>до<br/>пересчета',
                    'Клики<br/>до<br/>пересчета',
                    'Старый<br/>CTR',
                    'Все<br/>показы',
                    'Все<br/>клики',
                    'Обший<br/>рейтинг',
                    'Время обнавления</br> Общего Рейтинга',
                    'Обший<br/>CTR'
                ],
                colModel: [
                    {
                        name: 'title',
                        index: 'title',
                        align: 'center'
                    },
                    {
                        name: 'campaignTitle',
                        index: 'campaignTitle',
                        align: 'center'
                    },
                    {
                        name: 'impressions',
                        index: 'impressions',
                        align: 'center',
                        width: '70px',
                        search: false
                    },
                    {
                        name: 'clicks',
                        index: 'clicks',
                        align: 'center',
                        width: '70px',
                        search: false
                    },
                    {
                        name: 'ctr',
                        index: 'ctr',
                        align: 'center',
                        width: '80px',
                        formatter: 'number',
                        formatoptions: {
                            decimalSeparator: ",",
                            thousandsSeparator: ",",
                            decimalPlaces: 4
                        },
                        search: false
                    },
                    {
                        name: 'cost',
                        index: 'cost',
                        align: 'center',
                        width: '70px',
                        search: false
                    },
                    {
                        name: 'rating',
                        index: 'rating',
                        align: 'center',
                        width: '85px',
                        search: false
                    },
                    {
                        name: 'last_rating_update',
                        index: 'rating',
                        align: 'center',
                        width: '85px',
                        search: false
                    },
                    {
                        name: 'old_impressions',
                        index: 'old_impressions',
                        align: 'center',
                        width: '85px',
                        search: false
                    },
                    {
                        name: 'old_clicks',
                        index: 'old_clicks',
                        align: 'center',
                        width: '85px',
                        search: false
                    },
                    {
                        name: 'old_ctr',
                        index: 'old_ctr',
                        align: 'center',
                        width: '80px',
                        formatter: 'number',
                        formatoptions: {
                            decimalSeparator: ",",
                            thousandsSeparator: ",",
                            decimalPlaces: 4
                        },
                        search: false
                    },
                    {
                        name: 'full_impressions',
                        index: 'full_impressions',
                        align: 'center',
                        width: '90px',
                        search: false
                    },
                    {
                        name: 'full_clicks',
                        index: 'full_clicks',
                        align: 'center',
                        width: '90px',
                        search: false
                    },
                    {
                        name: 'full_rating',
                        index: 'full_rating',
                        align: 'center',
                        width: '85px',
                        search: false
                    },
                    {
                        name: 'last_full_rating_update',
                        index: 'rating',
                        align: 'center',
                        width: '85px',
                        search: false
                    },
                    {
                        name: 'full_ctr',
                        index: 'full_ctr',
                        align: 'center',
                        width: '80px',
                        formatter: 'number',
                        formatoptions: {
                            decimalSeparator: ",",
                            thousandsSeparator: ",",
                            decimalPlaces: 4
                        },
                        search: false
                    }
                ],
                caption: "Обший рейтинг рекламных предложений",
                height: 'auto',
                rowNum: 10,
                rowList: [
                    10,
                    20,
                    30,
                    100
                ],
                sortname: 'title',
                sortorder: 'asc',
                rownumbers: true,
                rownumWidth: 20,
                autowidth: true,
                hiddengrid: true,
                pager: '#tableOfferRating_pager'
            });
            $("#tableOfferRating").jqGrid('filterToolbar', {searchOperators: true});
            $("#tableOfferRating").jqGrid('navGrid', '#tableOfferRating_pager', {
                del: false,
                add: false,
                edit: false,
                search: false
            }, {}, {}, {}, {});

            // Таблица рейтинга рекламных предложений по рекламным блокам
            $("#tableOfferRatingForInformers").jqGrid({
                url: '/manager/ratingForInformers',
                datatype: 'json',
                mtype: 'GET',
                colNames: [
                    '',
                    'Рекламный блок'
                ],
                colModel: [
                    {
                        name: 'adv',
                        index: 'adv',
                        align: 'center',
                        key: true,
                        hidden: true
                    },
                    {
                        name: 'title',
                        index: 'title',
                        align: 'center',
                        width: '1184px'
                    }
                ],
                caption: "Pейтинг рекламных предложений по рекламным блокам",
                rownumbers: false,
                sortable: true,
                hiddengrid: true,
                autowidth: true,
                rowNum: 10,
                rowList: [
                    10,
                    20,
                    30,
                    100
                ],
                height: '100%',
                subGrid: true,
                subGridRowExpanded: function (
                    subgrid_id,
                    row_id
                ) {
                    var subgrid_table_id, pager_id;
                    subgrid_table_id = subgrid_id + "_t";
                    pager_id = "p_" + subgrid_table_id;
                    $("#" + subgrid_id).html("<table id='" + subgrid_table_id + "' class='scroll'></table><div id='" + pager_id + "' class='scroll'></div>");
                    $("#" + subgrid_table_id).jqGrid({
                        url: '/manager/ratingForInformers?subgrid=' + row_id,
                        datatype: "json",
                        colNames: [
                            'РП',
                            'РК',
                            'Показы',
                            'Клики',
                            'CTR',
                            'Цена',
                            'Рейтинг',
                            'Время обнавления</br>Рейтинга',
                            'Показы<br/>до<br/>пересчета',
                            'Клики<br/>до<br/>пересчета',
                            'Старый<br/>CTR',
                            'Все<br/>показы',
                            'Все<br/>клики',
                            'Обший<br/>Рейтинг',
                            'Время обнавления</br> Общего Рейтинга',
                            'Обший<br/>CTR'
                        ],
                        colModel: [
                            {
                                name: 'title',
                                index: 'title',
                                align: 'center',
                                sortable: true,
                                sorttype: 'text'
                            },
                            {
                                name: 'campaignTitle',
                                index: 'campaignTitle',
                                align: 'text'
                            },
                            {
                                name: 'impressions',
                                index: 'impressions',
                                align: 'center',
                                sortable: true,
                                sorttype: 'integer',
                                width: '70px'
                            },
                            {
                                name: 'clicks',
                                index: 'clicks',
                                align: 'center',
                                sortable: true,
                                sorttype: 'integer',
                                width: '70px'
                            },
                            {
                                name: 'ctr',
                                index: 'ctr',
                                align: 'center',
                                sortable: true,
                                sorttype: 'integer',
                                width: '70px',
                                formatter: 'number',
                                formatoptions: {
                                    decimalSeparator: ",",
                                    thousandsSeparator: ",",
                                    decimalPlaces: 4
                                }
                            },
                            {
                                name: 'cost',
                                index: 'cost',
                                align: 'center',
                                sortable: true,
                                sorttype: 'integer',
                                width: '70px'
                            },
                            {
                                name: 'rating',
                                index: 'rating',
                                align: 'center',
                                sortable: true,
                                sorttype: 'integer',
                                width: '85px'
                            },
                            {
                                name: 'last_rating_update',
                                index: 'rating',
                                align: 'center',
                                width: '85px',
                                search: false
                            },
                            {
                                name: 'old_impressions',
                                index: 'old_impressions',
                                align: 'center',
                                sortable: true,
                                sorttype: 'integer',
                                width: '85px'
                            },
                            {
                                name: 'old_clicks',
                                index: 'old_clicks',
                                align: 'center',
                                sortable: true,
                                sorttype: 'integer',
                                width: '85px'
                            },
                            {
                                name: 'old_ctr',
                                index: 'old_ctr',
                                align: 'center',
                                sortable: true,
                                sorttype: 'integer',
                                width: '70px',
                                formatter: 'number',
                                formatoptions: {
                                    decimalSeparator: ",",
                                    thousandsSeparator: ",",
                                    decimalPlaces: 4
                                }
                            },
                            {
                                name: 'full_impressions',
                                index: 'full_impressions',
                                align: 'center',
                                sortable: true,
                                sorttype: 'integer',
                                width: '90px'
                            },
                            {
                                name: 'full_clicks',
                                index: 'full_clicks',
                                align: 'center',
                                sortable: true,
                                sorttype: 'integer',
                                width: '90px'
                            },
                            {
                                name: 'full_rating',
                                index: 'full_rating',
                                align: 'center',
                                sortable: true,
                                sorttype: 'integer',
                                width: '85px'
                            },
                            {
                                name: 'last_full_rating_update',
                                index: 'rating',
                                align: 'center',
                                width: '85px',
                                search: false
                            },
                            {
                                name: 'full_ctr',
                                index: 'full_ctr',
                                align: 'center',
                                sortable: true,
                                sorttype: 'integer',
                                width: '70px',
                                formatter: 'number',
                                formatoptions: {
                                    decimalSeparator: ",",
                                    thousandsSeparator: ",",
                                    decimalPlaces: 4
                                }
                            }
                        ],
                        rownumbers: false,
                        loadonce: true,
                        sortable: true,
                        hiddengrid: true,
                        autowidth: true,
                        rowNum: 900,
                        height: '100%'
                    });
                },
                pager: '#tableOfferRatingForInformers_pager'
            });
            $("#tableOfferRatingForInformers").jqGrid('filterToolbar', {searchOperators: true});
//------------------------------------------------------------------------------------------------------------------------
            // -----------------------------------------------
            // Фильтры по дате для таблицы с данными о статистики работы воркера
            // -----------------------------------------------
            var datepickerNewOptions = {
                duration: 0,
                defaultDate: null,
                onSelect: function () {
                    var data_url = '/manager/WorkerNewStats?start_date=' + $('#workerNewStatsCalendar').val();
                    $('#tableWorkerNewStats').jqGrid().clearGridData();
                    $('#tableWorkerNewStats').setGridParam({url: data_url}).trigger("reloadGrid");
                }

            };
            $("#workerNewStatsCalendar").datepicker(datepickerNewOptions);

            // Таблица с данными о статистике работы воркера
            $("#tableWorkerNewStats").jqGrid({
                url: '/manager/WorkerNewStats?start_date=' + $('#workerNewStatsCalendar').val() + '&',
                datatype: 'json',
                mtype: 'GET',
                colNames: [
                    'Ветка алгоритма',
                    'Кол-во РП',
                    'Кол-во кликов по РП',
                    '1 слово',
                    '2 слова',
                    '3 слова',
                    'Более 3 слов',
                    'Н+О',
                    'Клики Н+О',
                    'Ш',
                    'Клики Ш',
                    'Ф',
                    'Клики Ф',
                    'Т',
                    'Клики Т'
                ],
                colModel: [
                    {
                        name: 'branch',
                        index: 'branch',
                        align: 'left',
                        width: 320,
                        sortable: false
                    },
                    {
                        name: 'imp_count',
                        index: 'imp_count',
                        align: 'center',
                        width: 90,
                        sortable: false
                    },
                    {
                        name: 'click_count',
                        index: 'click_count',
                        align: 'center',
                        width: 90,
                        sortable: false
                    },
                    {
                        name: 'word1',
                        index: 'word1',
                        align: 'center',
                        width: 90,
                        sortable: false,
                        hidden: true
                    },
                    {
                        name: 'word2',
                        index: 'word2',
                        align: 'center',
                        width: 90,
                        sortable: false,
                        hidden: true
                    },
                    {
                        name: 'word3',
                        index: 'word3',
                        align: 'center',
                        width: 90,
                        sortable: false,
                        hidden: true
                    },
                    {
                        name: 'word>3',
                        index: 'word>3',
                        align: 'center',
                        width: 90,
                        sortable: false,
                        hidden: true
                    },
                    {
                        name: 'imp_td',
                        index: 'imp_td',
                        align: 'center',
                        width: 70,
                        sortable: false
                    },
                    {
                        name: 'click_td',
                        index: 'click_td',
                        align: 'center',
                        width: 70,
                        sortable: false
                    },
                    {
                        name: 'imp_bm',
                        index: 'imp_bm',
                        align: 'center',
                        width: 70,
                        sortable: false
                    },
                    {
                        name: 'click_bm',
                        index: 'click_bm',
                        align: 'center',
                        width: 70,
                        sortable: false
                    },
                    {
                        name: 'imp_ph',
                        index: 'imp_ph',
                        align: 'center',
                        width: 70,
                        sortable: false
                    },
                    {
                        name: 'click_ph',
                        index: 'click_ph',
                        align: 'center',
                        width: 70,
                        sortable: false
                    },
                    {
                        name: 'imp_em',
                        index: 'imp_em',
                        align: 'center',
                        width: 70,
                        sortable: false
                    },
                    {
                        name: 'click_em',
                        index: 'click_em',
                        align: 'center',
                        width: 70,
                        sortable: false
                    }
                ],
                caption: "Статистика работы нового воркера",
                height: 'auto',
                autowidth: true,
                scroll: false,
                hiddengrid: true,
                viewrecords: false,
                rownumbers: false,
                rowNum: 22
            });

//------------------------------------------------------------------------------------------------------------------------
            // Таблица дохода менеджера за 30 дней по дням
            $("#managersSummaryByDate").jqGrid({
                url: '/manager/managersSummaryByDays',
                datatype: 'json',
                mtype: 'GET',
                loadComplete: function () {
                    $('#managersSummaryByDate .actionLink').click(openUserDetails);
                },
                colNames: [
                    'Дата',
                    'Менеджер',
                    'Отчислено партнёрам',
                    'Процент отчисления партнёру',
                    'Остаток',
                    'Отчислено Adload',
                    'Активных сайтов',
                    'Всего сайтов'
                ],
                colModel: [
                    {
                        name: 'date',
                        index: 'date',
                        width: 140,
                        formatter: "date",
                        formatoptions: {srcformat: 'Y.m.d'},
                        sortable: false,
                        align: 'center'
                    },
                    {
                        name: 'manager',
                        index: 'manager',
                        width: 140,
                        align: 'center',
                        sortable: false,
                        classes: 'actionLink'
                    },
                    {
                        name: 'totalCost',
                        index: 'totalCost',
                        width: 140,
                        sortable: false,
                        align: 'center'
                    },
                    {
                        name: 'totalCost_persent',
                        index: 'totalCost_persent',
                        width: 140,
                        sortable: false,
                        align: 'center'
                    },
                    {
                        name: 'income',
                        index: 'income',
                        width: 140,
                        sortable: false,
                        align: 'center'
                    },
                    {
                        name: 'adload_cost',
                        index: 'adload_cost',
                        width: 140,
                        sortable: false,
                        align: 'center'
                    },
                    {
                        name: 'activ_users',
                        index: 'activ_users',
                        width: 140,
                        sortable: false,
                        align: 'center'
                    },
                    {
                        name: 'all_users',
                        index: 'all_users',
                        width: 140,
                        sortable: false,
                        align: 'center'
                    }
                ],
                caption: "Доход менеджеров за 30 дней по дням",
                gridview: true,
                hiddengrid: true,
                rowNum: "records",
                height: '100%',
                loadonce: true,
                grouping: true,
                groupingView: {
                    groupField: ['date']
                }
            });

            // Таблица дохода менеджера за 30 дней по дням
            $("#tableAccountProfit").jqGrid({
                url: '/manager/monthProfitPerDate',
                datatype: 'json',
                mtype: 'GET',
                colNames: [
                    'Дата',
                    '',
                    'Отчислено партнёрам',
                    'Процент отчисления партнёру',
                    'Остаток',
                    'Отчислено Adload',
                    'Активных сайтов',
                    'Всего сайтов'
                ],
                colModel: [
                    {
                        name: 'date',
                        index: 'date',
                        width: 140,
                        align: 'center',
                        formatter: "date"
                    },
                    {
                        name: 'manager',
                        index: 'manager',
                        width: 140,
                        hidden: true,
                        align: 'center'
                    },
                    {
                        name: 'totalCost',
                        index: 'totalCost',
                        width: 140,
                        align: 'center'
                    },
                    {
                        name: 'totalCost_persent',
                        index: 'totalCost_persent',
                        width: 140,
                        align: 'center'
                    },
                    {
                        name: 'income',
                        index: 'income',
                        width: 140,
                        align: 'center'
                    },
                    {
                        name: 'adload_cost',
                        index: 'adload_cost',
                        width: 140,
                        align: 'center'
                    },
                    {
                        name: 'activ_users',
                        index: 'activ_users',
                        width: 140,
                        align: 'center'
                    },
                    {
                        name: 'all_users',
                        index: 'all_users',
                        width: 140,
                        align: 'center'
                    }
                ],
                caption: "Отчисления за 30 дней по дням",
                hiddengrid: true,
                gridview: true,
                rowNum: 30,
                rownumbers: false,
                height: 300,
                footerrow: true
            });

            // Таблица с данными о количестве показов и кликов
            $("#tableUsersImpressionsClick").jqGrid({
                url: '/manager/dataUserImpressionsClick?' + '&start_date=' + $('#ImpClickCalendar1').val() + '&',
                datatype: 'json',
                mtype: 'GET',
                colNames: [
                    'Сайт Партнёр',
                    'Показы Блоков</br> не гарантированные',
                    'Показы<br/>Блоков',
                    'Процент видимых показов',
                    'Социальные показы РП</br> не гарантированные',
                    'Социальные показы РП',
                    'Социальные клики',
                    'Уникальные Социальные клики',
                    'Социальный CTR',
                    'Показы РП</br> не гарантированные',
                    'Показы РП',
                    'Клики',
                    'Уникальные клики',
                    'Подозри</br>тельные</br>клики',
                    'Отфильтро</br>ванные</br>клики',
                    'Забаненые</br>клики',
                    'CTR',
                    'Разница',
                    'Ср.время</br>до клика'
                ],
                colModel: [
                    {
                        name: 'domain',
                        index: 'domain',
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'impressions_block_not_valid',
                        index: 'impressions_block_not_valid',
                        align: 'center',
                        formatter: 'integer',
                        classes: 'block-column',
                        width: 100,
                        sortable: true
                    },
                    {
                        name: 'impressions_block',
                        index: 'impressions_block',
                        align: 'center',
                        formatter: 'integer',
                        classes: 'block-column',
                        width: 100,
                        sortable: true
                    },
                    {
                        name: 'viewPort',
                        index: 'viewPort',
                        align: 'center',
                        formatter: 'integer',
                        width: 100,
                        sortable: false
                    },
                    {
                        name: 'social_impressions_not_valid',
                        index: 'social_impressions_not_valid',
                        align: 'center',
                        formatter: 'integer',
                        classes: 'social-column',
                        width: 100,
                        sortable: true
                    },
                    {
                        name: 'social_impressions',
                        index: 'social_impressions',
                        align: 'center',
                        formatter: 'integer',
                        classes: 'social-column',
                        width: 100,
                        sortable: true
                    },
                    {
                        name: 'social_clicks',
                        index: 'social_clicks',
                        formatter: 'integer',
                        classes: 'social-column',
                        align: 'center',
                        width: 100,
                        sortable: true
                    },
                    {
                        name: 'social_clicksUnique',
                        index: 'social_clicksUnique',
                        formatter: 'integer',
                        classes: 'social-column',
                        align: 'center',
                        width: 100,
                        sortable: true
                    },
                    {
                        name: 'ctr_social_impressions',
                        index: 'ctr_social_impressions',
                        formatter: 'integer',
                        align: 'center',
                        classes: 'social-column',
                        width: 100,
                        sortable: true
                    },
                    {
                        name: 'impressions_not_valid',
                        index: 'impressions_not_valid',
                        align: 'center',
                        formatter: 'integer',
                        classes: 'offer-column',
                        width: 100,
                        sortable: true
                    },
                    {
                        name: 'impressions',
                        index: 'impressions',
                        align: 'center',
                        formatter: 'integer',
                        classes: 'offer-column',
                        width: 100,
                        sortable: true
                    },
                    {
                        name: 'clicks',
                        index: 'clicks',
                        formatter: 'integer',
                        align: 'center',
                        classes: 'offer-column',
                        width: 50,
                        sortable: true
                    },
                    {
                        name: 'clicksUnique',
                        index: 'clicksUnique',
                        formatter: 'integer',
                        align: 'center',
                        classes: 'offer-column',
                        width: 50,
                        sortable: true
                    },
                    {
                        name: 'click_warning',
                        index: 'click_warning',
                        width: 50,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'click_filtered',
                        index: 'click_filtered',
                        width: 50,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'click_bann',
                        index: 'click_bann',
                        width: 50,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'ctr_impressions',
                        index: 'ctr_impressions',
                        formatter: 'integer',
                        classes: 'offer-column',
                        align: 'center',
                        width: 100,
                        sortable: true
                    },
                    {
                        name: 'ctr_difference_impressions',
                        index: 'ctr_difference_impressions',
                        formatter: 'integer',
                        align: 'center',
                        width: 100,
                        sortable: true
                    },
                    {
                        name: 'view_seconds_avg',
                        index: 'view_seconds_avg',
                        width: 70,
                        align: 'center',
                        sortable: false
                    }
                ],
                caption: "Статистика пользователей GetMyAd по количеству показов и кликов",
                height: 'auto',
                rowList: [
                    10,
                    20,
                    30,
                    100
                ],
                sortname: 'domain',
                sortorder: 'asc',
                rownumbers: true,
                rowNum: 20,
                hiddengrid: true,
                autowidth: true,
                pager: '#tableUsersImpressionsClick_pager'
            });
            // -----------------------------------------------
            // Фильтры по дате для таблицы с данными о количестве социальных показов
            // -----------------------------------------------
            var datepickerOptions = {
                duration: 0,
                defaultDate: null,
                onSelect: function () {
                    var data_url = '/manager/dataUserImpressionsClick?' + '&start_date=' + $('#ImpClickCalendar1').val();
                    $('#tableUsersImpressionsClick').jqGrid().clearGridData();
                    $('#tableUsersImpressionsClick').setGridParam({url: data_url}).trigger("reloadGrid");
                }

            };
            $("#ImpClickCalendar1").datepicker(datepickerOptions);

            // Операции со счётом: вывод денег
            $("#tableAccountMoneyOut").jqGrid({
                url: '/manager/moneyOutHistory',
                datatype: 'json',
                mtype: 'GET',
                colNames: [
                    'Дата',
                    'Сумма',
                    'Примечания'
                ],
                colModel: [
                    {
                        name: 'Date',
                        index: 'Date',
                        width: 140,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'Summ',
                        index: 'Summ',
                        width: 140,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'Comment',
                        index: 'Comment',
                        width: 440,
                        align: 'center',
                        sortable: true
                    }
                ],
                caption: "Вывод денег",
                gridview: true,
                rownumbers: false,
                rowNum: 10,
                loadonce: true,
                forceFit: true,
                toolbar: [
                    true,
                    'top'
                ],
                pager: "#pagerAccountMoneyOut",
                beforeSelectRow: function (
                    rowid,
                    e
                ) {
                    if (rowid) {
                        if ($("#tableAccountMoneyOut").getRowData(rowid)['Comment'] == "заявка обрабатывается..."){
                            buttonCancelMoneyOutRequest.attr('disabled', false);
                        }
                        else
                        {
                            buttonCancelMoneyOutRequest.attr('disabled', true);
                        }
                    }
                    return true;
                }
            });

            var buttonCancelMoneyOutRequest = $("<input type='button' value='Отозвать заявку' />");
            buttonCancelMoneyOutRequest.attr('disabled', true).click(function () {
                $("#dialogCancelRequest").dialog('open');
            });
            $("#t_tableAccountMoneyOut").append(buttonCancelMoneyOutRequest);


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
                        $.ajax({
                            url: "/manager/moneyOutRemove?id=" + id + "&token=" + window.token,
                            dataType: 'json',
                            success: function (result) {
                                if (result.error) {
                                    if (result.error_type == "authorizedError"){
                                        window.location.replace("/");
                                    }
                                    else if (result.msg) {
                                        alert(result.msg);
                                    }
                                    else {
                                        alert("Неизвестная ошибка.");
                                    }
                                }
                                else{
                                    reloadMoneyOutHistoryGrid();
                                }

                            },
                            error: function (
                                error,
                                ajaxOptions,
                                thrownError
                            ) {
                                alert(error.responseText);
                            }
                        });
                        buttonApproveMoneyOutRequest.attr('disabled', true);
                        $(this).dialog("close");
                    },
                    "Отмена": function () {
                        $(this).dialog("close");
                    }
                }
            });


            /** Перезагружает таблицу истории вывода денежных средств */
            function reloadMoneyOutHistoryGrid() {
                $('#tableAccountMoneyOut').jqGrid('setGridParam', {
                    datatype: "json"
                }).jqGrid('setGridParam', {
                    url: "/manager/moneyOutHistory"
                }).trigger("reloadGrid");
            }


            // Таблица заявок на добавление домена
            $("#tableDomainRegistration").jqGrid({
                datatype: function () {
                    var data = window.dataDomainRequests;
                    for (var i = 0; i < data.rows.length; i++) {
                        data.rows[i].cell.push('<a href="javascript:;" class="actionLink">Одобрить</a>');
                        data.rows[i].cell.push('<a href="javascript:;" class="actionLink2">Отклонить</a>');
                    }
                    this.addJSONData(data);
                    $("#tableDomainRegistration .actionLink").click(function () {
                        var grid = $("#tableDomainRegistration");
                        var rowId = grid.getGridParam('selrow');
                        if (rowId === null){
                            return;
                        }
                        var row = grid.jqGrid('getRowData', rowId);
                        var message = "<p>Одобрить домен <b>" + row.domain +
                            "</b> для пользователя " +
                            row.user +
                            "?</p>";
                        var dialog = $(message).dialog({
                            modal: true,
                            buttons: {
                                'Да': function () {
                                    $.getJSON("/manager/approveDomain", {
                                        user: row.user,
                                        domain: row.domain,
                                        approved: 'true',
                                        token: window.token
                                    }, function (data) {
                                        if (data.error) {
                                            if (data.error_type == "authorizedError"){
                                                window.location.replace("/main/index");
                                            }
                                            else if (data.msg) {
                                                alert(data.msg);
                                                return;
                                            }
                                            else {
                                                alert("Неизвестная ошибка.");
                                                return;
                                            }
                                        }
                                        else {
                                            $.getJSON("/manager/domainsRequests", function (json) {
                                                window.dataDomainRequests = json;
                                                dialog.dialog('close');
                                                $('#tableDomainRegistration').trigger('reloadGrid');
                                                openUserDetailsByLogin(row.user, "edit_domain_categories");
                                            });
                                        }
                                    });
                                },
                                'Нет': function () {
                                    dialog.dialog('close');
                                }
                            }
                        });
                    });


                    $("#tableDomainRegistration .actionLink2").click(function () {
                        var grid = $("#tableDomainRegistration");
                        var rowId = grid.getGridParam('selrow');
                        if (rowId === null){
                            return;
                        }
                        var row = grid.jqGrid('getRowData', rowId);
                        var message = "<p>Отклонить заявку на добавление домена <b>" + row.domain +
                            "</b> пользователя " +
                            row.user +
                            "?</p>";
                        var dialog = $(message).dialog({
                            modal: true,
                            buttons: {
                                'Да': function () {
                                    $.getJSON("/manager/rejectDomain", {
                                        user: row.user,
                                        domain: row.domain,
                                        approved: 'true',
                                        token: window.token
                                    }, function (data) {
                                        if (data.error) {
                                            if (data.error_type == "authorizedError"){
                                                window.location.replace("/main/index");
                                            }
                                            else if (data.msg) {
                                                alert(data.msg);
                                                return;
                                            }
                                            else {
                                                alert("Неизвестная ошибка.");
                                                return;
                                            }
                                        }
                                        else {
                                            $.getJSON("/manager/domainsRequests", function (json) {
                                                window.dataDomainRequests = json;
                                                dialog.dialog('close');
                                                $('#tableDomainRegistration').trigger('reloadGrid');
                                            });
                                        }
                                    });
                                },
                                'Нет': function () {
                                    dialog.dialog('close');
                                }
                            }
                        });
                    });


                },
                colNames: [
                    'Пользователь',
                    'Дата',
                    'Домен',
                    'Примечания',
                    '',
                    ''
                ],
                colModel: [
                    {
                        name: 'user',
                        index: 'user',
                        width: 90,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'date',
                        index: 'date',
                        width: 100,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'domain',
                        index: 'domain',
                        width: 180,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'comments',
                        index: 'comments',
                        width: 400,
                        align: 'left',
                        sortable: true
                    },
                    {
                        name: 'actions',
                        index: 'actions',
                        width: 80,
                        align: 'center',
                        sortable: true
                    },
                    {
                        name: 'actions',
                        index: 'actions',
                        width: 80,
                        align: 'center',
                        sortable: true
                    }
                ],
                caption: "Заявки на добавление домена",
                rownumbers: true,
                height: 'auto',
                rownumWidth: 40,
                rowNum: 900
            });


        }


        // Сводная таблица по пользователям
        function openUserDetails() {
            var login = this.innerText || this.text || this.textContent;
            var div = "userDetails";
            openUserDetailsByLogin(login, div);
        }

        function closeUserDetails() {
            if (userDetailsTabs) {
                $("#tabs").tabs('remove', $("#tabs").tabs('length') - 1);
            }
            userDetailsTabs = false;
        }

        function openUserDetailsByLogin(
            login,
            div
        ) {
            if (window.permissionEditUserAccount) {
                $.getJSON("/manager/checkCurrentUser?token=" + window.token, function (result) {
                    if (result.error){
                        window.location.replace("/main/index");
                    }
                });
                var url = ["/manager/userDetails?login=", encodeURIComponent(login), "&token=", window.token, "&div=", div];
                closeUserDetails();
                userDetailsTabs = true;
                $("#tabs").tabs('add', url.join(''), login);
            }
        }


        prepareUi();
        $.getJSON("/manager/checkCurrentUser?token=" + window.token, function (result) {
            if (result.error){
                window.location.replace("/main/index");
            }
            $("#loading").hide();
            $("#tabs").css("visibility", "visible");
            window.checkDataUpdate();
        });
    });

};
$(document).ready(function () {
    "use strict";
    ManagerUI();
});

var UserDetailUI = function (id, login, block_cost_data, div_to_open, domains_categories, categories, accountMoneyOutHistory) {
    "use strict";
    var closeUserDetails = function () {
        if (userDetailsTabs) {
            $("#tabs").tabs('remove', $("#tabs").tabs('length') - 1);
        }
        userDetailsTabs = false;
    };
    $('tr.hide').each(function () {
        $(this).find('span').text(function (
            _,
            value
        ) {
            return value == '→' ? '↓' : '→'
        });
        $(this).nextUntil('tr.header').slideToggle(100, function () {
        });
    });
    $('tr.header').click(function () {
        $(this).find('span').text(function (
            _,
            value
        ) {
            return value == '→' ? '↓' : '→'
        });
        $(this).nextUntil('tr.header').slideToggle(100, function () {
        });
    });
    // $("#tabs").tabs();

    $("#accordion").accordion(
        {
            autoHeight: false
        }
    );
    if (window.div_to_open === "edit_domain_categories") {
        $("#accordion").accordion("activate", 1);
    }

    $("#dialogSetPassword").dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            'Сохранить': function () {
                if ($("#dialogSetPassword_psw1").val().length < 6) {
                    displayPswMessage('Длина пароля должна быть не меньше шести символов');
                    return;
                }
                if ($("#dialogSetPassword_psw1").val() != $("#dialogSetPassword_psw2").val()) {
                    displayPswMessage('Повторный пароль неверен!');
                    return;
                }
                $.getJSON("/manager/setNewPassword", {
                    psw: $("#dialogSetPassword_psw1").val(),
                    login: $("#login").val(),
                    token: $("#token").val()
                }, function (json) {
                    if (json.error) {
                        if (json.error_type = "authorizedError"){
                            window.location.replace("/main/index");
                        }
                        else{
                            displayPswMessage('Ошибка сохранения пароля!');
                        }
                        return;
                    }
                    else {
                        $("#dialogSetPassword").dialog('close');
                    }

                });
            },
            'Отменить': function () {
                $(this).dialog('close');
            }

        }

    });
    $("#dialogDeleteAccount").dialog({
        autoOpen: false,
        modal: true,
        buttons: {
            'Удалить': function () {
                $.getJSON("/manager/deleteAccount", {
                    login: $("#login").val(),
                    token: $("#token").val()
                }, function (json) {
                    if (json.error) {
                        if (json.error_type === "authorizedError")
                        {
                            window.location.replace("/main/index");
                        }
                        else{
                            displayDeleteMessage('Ошибка удаления!');
                        }
                        return;
                    }
                    else {
                        $("#dialogDeleteAccount").dialog('close');
                        closeUserDetails();
                    }

                });
            },
            'Отменить': function () {
                $(this).dialog('close');
            }

        }

    });

    $("#generate-psw-button").click(function () {
        $.getJSON("/manager/generateNewPassword", function (json) {
            if (json.error) {
                displayPswMessage('Ошибка генерации пароля!');
            } else {
                $('#dialogSetPassword_psw1').val(json.new_password);
                $('#dialogSetPassword_psw2').val(json.new_password);
            }
        });
        return false;
    });

    $("#edit-psw-button").click(function () {
        $('#dialogSetPassword_psw1').val('');
        $('#dialogSetPassword_psw2').val('');
        $('#psw-error-message').html('');
        $('#dialogSetPassword_user').html($('#login').val());
        $("#dialogSetPassword").dialog('open');
    });
    $("#delete-account-button").click(function () {
        $('#delete-error-message').html('');
        $('#dialogDeleteAccount_user').html($('#login').val());
        $("#dialogDeleteAccount").dialog('open');
    });

    function displayMessage(message) {
        $("#error-message").show().text(message).fadeOut(2500);
    }

    function displayCategoriesMessage(message) {
        $("#categories-error-message").show().text(message).fadeOut(2500);
    }

    function displayPswMessage(message) {
        $("#psw-error-message").show().text(message);
    }

    function displayDeleteMessage(message) {
        $("#delete-error-message").show().text(message);
    }

    function displayFieldsMessage(message) {
        $("#fields-error-message").show().text(message);
    }

    $('#user-details-'+ id +' button.submit-button').click(function () {
        $('#user-details-'+ id).ajaxSubmit({
            dataType: 'json',
            beforeSubmit: function () {
                $('#user-details-'+ id +' button.submit-button').attr('disabled', true);
            },
            success: function (result) {
                if (result.error === false) {
                    displayFieldsMessage('');
                    displayMessage("Изменения успешно сохранены.");
                }
                else {
                    if (result.error_type === "authorizedError"){
                        window.location.replace("/main/index");
                    }
                    else if (result.msg) {
                        displayFieldsMessage(result.msg);
                        displayMessage("Ошибка сохранения!");
                    }
                    else{
                        displayMessage("Ошибка сохранения!");
                    }

                }
            },
            error: function () {
                displayMessage("Ошибка сохранения! Попробуйте сохранить ещё раз.");
            },
            complete: function () {
                $('#user-details-'+ id +' button.submit-button').attr('disabled', false);
            }
        });
        return false;

    });


    $("#account_domains").change(function () {
        var domain = $("#account_domains").val();
        var cat_count = categories.length;
        var i = 0;
        while (i < cat_count) {
            var selected = false;
            for (var j = 0; j < domains_categories[domain].length; j++) {
                if (domains_categories[domain][j] === categories[i].guid){
                    selected = true;
                }
            }
            document.getElementById("categories").options[i] = new Option(
                categories[i].title,
                categories[i].guid,
                selected, selected);
            i++;
        }
    });

    $('#save-domain-categories-'+ id +' button.submit-button').click(function () {
        $('#save-domain-categories-'+ id).ajaxSubmit({
            dataType: 'json',
            beforeSubmit: function () {
                $('#save-domain-categories-'+ id +' button.submit-button').attr('disabled', true);
            },
            success: function (result) {
                if (result.error === false) {
                    displayCategoriesMessage("Изменения успешно сохранены.");
                    domains_categories = result.domains_categories;
                }
                else if (result.error_type === "authorizedError"){
                    window.location.replace("/main/index");
                }
                else {
                    if (result.msg){
                        displayCategoriesMessage(result.msg);
                    }
                    else{
                        displayCategoriesMessage("Ошибка сохранения!");
                    }
                }
            },
            error: function () {
                displayCategoriesMessage("Ошибка сохранения! Попробуйте сохранить ещё раз.");
            },
            complete: function () {
                $("#save-domain-categories-"+ id +" button.submit-button").attr('disabled', false);
            }
        });
        return false;

    });

        $("#accountMoneyOutHistoryTable").jqGrid({
            datatype: function () {
                this.addJSONData(accountMoneyOutHistory);
            },
            mtype: 'GET',
            colNames: [
                'Пользователь',
                'Дата',
                'Сумма',
                'Подтверждено',
                'Разрешено',
                'Оплачено',
                'Телефон',
                'Оплата',
                'Код протекции',
                'Истикает',
                'Примечания'
            ],
            colModel: [
                {
                    name: 'user',
                    index: 'user',
                    width: 110,
                    align: 'center',
                    sortable: false,
                    hidden: true
                },
                {
                    name: 'date',
                    index: 'date',
                    width: 100,
                    align: 'center',
                    sortable: false
                },
                {
                    name: 'sum',
                    index: 'sum',
                    width: 100,
                    align: 'center',
                    sortable: false
                },
                {
                    name: 'user_confirmed',
                    index: 'user_confirmed',
                    width: 80,
                    align: 'center',
                    sortable: false
                },
                {
                    name: 'manager_agreed',
                    index: 'manager_agreed',
                    width: 80,
                    align: 'center',
                    sortable: false
                },
                {
                    name: 'approved',
                    index: 'approved',
                    width: 80,
                    align: 'center',
                    sortable: false
                },
                {
                    name: 'phone',
                    index: 'phone',
                    width: 140,
                    align: 'center',
                    sortable: false
                },
                {
                    name: 'payment_type',
                    index: 'payment_type',
                    width: 110,
                    align: 'center',
                    sortable: false
                },
                {
                    name: 'protectionCode',
                    index: 'protectionCode',
                    width: 80,
                    align: 'center',
                    sortable: false
                },
                {
                    name: 'protectionDate',
                    index: 'protectionDate',
                    width: 80,
                    align: 'center',
                    sortable: false
                },
                {
                    name: 'details',
                    index: 'details',
                    width: 420,
                    align: 'left',
                    sortable: false
                }
            ],
            caption: "История вывода средств",
            gridview: true,
            rownumbers: false,
            rowNum: 30,
            forceFit: true,
            height: 250
        });

    $("#accountDomainsStatsTable").jqGrid({
        caption: "Статистика доменов пользователя",
        datatype: 'json',
        url: '/manager/userDomainDetails',
        postData: {user: login},
        mtype: 'GET',
        gridview: true,
        rowNum: 1000,
        height: 250,
        forceFit: true,
        colNames: [
            'Дата',
            'Домен',
            'Показы РБ</br>не гарантированные',
            'Показы</br>РБ',
            'Показы РП</br>не гарантированные',
            'Показы</br>РП',
            'Клики',
            'Уникальные клики',
            'Ср цена</br>РП',
            'CTR РП, %',
            'CTR РБ, %',
            'Итого',
            'Социальные</br>Клики',
            'Социальные</br>Показы</br>РП</br>не гарантированные',
            'Социальные</br>Показы</br>РП',
            'Показы в видимой области'
        ],
        colModel: [
            {
                name: 'date',
                index: 'date',
                width: 140,
                align: 'center',
                sortable: true,
                firstsortorder: 'desc'
            },
            {
                name: 'domain',
                index: 'domain',
                width: 200,
                align: 'center',
                sortable: true
            },
            {
                name: 'imp_block_nv',
                index: 'imp_block_nv',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'imp_block',
                index: 'imp_block',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'imp_nv',
                index: 'imp_nv',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'imp',
                index: 'imp',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'clicks',
                index: 'clicks',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'unique',
                index: 'unique',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'cost',
                index: 'cost',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'ctr',
                index: 'ctr',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'ctr_block',
                index: 'ctr_block',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'summ',
                index: 'summ',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'soc_clicks',
                index: 'soc_clicks',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'soc_imp_nv',
                index: 'soc_imp_nv',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'soc_imp',
                index: 'soc_imp',
                width: 80,
                align: 'center',
                sortable: false
            },
            {
                name: 'viewport',
                index: 'viewport',
                width: 80,
                align: 'center',
                sortable: false
            }
        ]
    });

    var editrulecp = {
        minValue: 1,
        maxValue: 100,
        number: true
    };
    var editrulecn = {
        minValue: 0.01,
        maxValue: 100.0,
        number: true
    };
    var editrulecm = {
        minValue: 0.01,
        maxValue: 100.0,
        number: true
    };
    $(document).ready(function () {
        $("#table_block_cost").jqGrid({
            datatype: 'local',
            data: block_cost_data,
            colNames: [
                '',
                'Ред/Сох',
                'Название',
                'Процент цены</br>за клик',
                'Минимальная цена</br>за клик',
                'Максимальная цена</br>за клик'
            ],
            colModel: [
                {
                    name: 'act',
                    index: 'act',
                    width: 45,
                    sortable: false
                },
                {
                    name: 'id',
                    index: 'id',
                    align: 'center',
                    hidden: true
                },
                {
                    name: 'title',
                    index: 'title',
                    align: 'center',
                    sortable: false,
                    editable: false,
                    width: 270
                },
                {
                    name: 'click_percent',
                    index: 'click_percent',
                    sortable: false,
                    width: 100,
                    align: 'center',
                    editable: true,
                    edittype: "text",
                    editoptions: {
                        size: 10,
                        maxlength: 5
                    },
                    editrules: editrulecp
                },
                {
                    name: 'click_cost_min',
                    index: 'click_cost_min',
                    sortable: false,
                    width: 125,
                    align: 'center',
                    editable: true,
                    edittype: "text",
                    editoptions: {
                        size: 10,
                        maxlength: 5
                    },
                    editrules: editrulecn
                },
                {
                    name: 'click_cost_max',
                    index: 'click_cost_max',
                    sortable: false,
                    width: 125,
                    align: 'center',
                    editable: true,
                    edittype: "text",
                    editoptions: {
                        size: 10,
                        maxlength: 5
                    },
                    editrules: editrulecm
                }
            ],
            gridComplete: function () {
                var table_block_cost = $("#table_block_cost");
                var ids = table_block_cost.jqGrid('getDataIDs');
                for (var i = 0; i < ids.length; i++) {
                    var cl = ids[i];
                    var be = "<input style='height:22px;width:40px;' type='button' value='Ред' " +
                        "onclick=\"$('#table_block_cost').editRow('" + cl + "');\"  />";
                    var se = "<input style='height:22px;width:40px;' type='button' value='Сох' " +
                        "onclick=\"$('#table_block_cost').saveRow('" + cl + "');\"  />";
                    var re = "<input style='height:22px;width:40px;' type='button' value='Отм' " +
                        "onclick=\"$('#table_block_cost').restoreRow('" + cl + "');\"  />";
                    table_block_cost.jqGrid('setRowData', ids[i], {act: be + se + re});
                }
            },
            caption: "Установка цен для РБ",
            editurl: "/manager/informer_cost_save",
            height: 'auto',
            sortname: 'title',
            sortorder: 'asc',
            viewrecords: true,
            rowNum: 900,
            autowidth: true,
            hiddengrid: false
        });

    });
};

window.checkDataUpdate = function() {
    "use strict";
    window.CheckUser();
    $.getJSON("/manager/checkCurrentUser?token=" + window.token, function (result) {
        if (result.error){
            window.location.replace("/main/index");
        }
    });

    if (window.permissionViewMoneyOut) {
        var new_notApprovedRequests = 0;
        $.get("/manager/notApprovedActiveMoneyOutRequests", function (res) {
            new_notApprovedRequests = res;
            if (Number(new_notApprovedRequests) > 0) {
                $("#href_moneyOutRequests").html('Вывод средств <font color="red"><b> ! </b></font>');
            }
            else {
                $("#href_moneyOutRequests").html("Вывод средств");
            }
            if (window.notApprovedRequests !== new_notApprovedRequests) {
                window.notApprovedRequests = new_notApprovedRequests;
                $("#notApprovedRequests").html(window.notApprovedRequests);
                $('#tableMoneyOutRequest').trigger('reloadGrid');
            }
        });
    }

    var new_dataDomainRequests;
    $.getJSON("/manager/domainsRequests", function (json) {
        new_dataDomainRequests = json;
        if (new_dataDomainRequests.records > 0) {
            $("#href_moderation").html('Модерация <font color="red"><b> ! </b></font>');
            // Поменять заголовок когда разобрались со всеми заявками!!!
        }
        else {
            $("#href_moderation").html('Модерация');
        }
        if (new_dataDomainRequests !== window.dataDomainRequests) {
            window.dataDomainRequests = new_dataDomainRequests;
            $("#tableDomainRegistration").trigger('reloadGrid');
        }
    });
};
setInterval(window.checkDataUpdate, 60000);
