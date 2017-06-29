var AdvertiseEditor = AdvertiseEditor || (function () {

        var patterns;			// Образцы выгрузок
        var advertise;			// Редактируемый информер

        /** Выводит название и сайт информера */
        function printInformerTitle() {
            $("#informer-title").text(advertise.domain + ', ' + advertise.title);
        }

        /** Редактирование названия информера*/
        $('#edit-informer-title').keyup(function () {
            advertise.title = $(this).val();
            printInformerTitle();
        });

        /** Выбор домена информера*/
        $('#informer-site').change(function () {
            advertise.domain = $(this).val();
            printInformerTitle();
        });

        function displayMessage(message) {
            $("#error-message").show().text(message).fadeOut(2500);
        }

        /** Сохранение информера */
        function save() {
            $.ajax({
                url: '/advertise/save_dynamic' + (advertise.guid ? '?adv_id=' + advertise.guid : ''),
                type: 'POST',
                data: JSON.stringify({
                    title: advertise.title,
                    options: advertise.options,
                    domain: advertise.domain,
                    css: ' ',
                    nonRelevant: {action:'social',userCode:''},
                    height: 0,
                    width: 0,
                    height_banner: 0,
                    width_banner: 0,
                    html_notification: advertise.html_notification,
                    auto_reload: 0
                }),
                cache: false,
                dataType: 'json',
                contentType: "application/json; charset=utf-8",
                beforeSend: function () {
                    $("#saveButton").attr("disabled", true);
                },
                success: function (result) {
                    ans = result;
                    if (result.error == false && result.id) {
                        advertise.guid = result.id;
                        generateScriptCode(advertise.guid);
                        $("#div-informer-code").fadeIn();
                        displayMessage("Изменения успешно сохранены.");
                    } else {
                        if (result.error && result.error.message)
                            displayMessage("Ошибка сохранения информера: " + result.error.message);
                        else
                            displayMessage("Ошибка сохранения информера!" + result.message);
                    }
                },
                error: function () {
                    displayMessage("Ошибка сохранения запроса! Попробуйте сохранить ещё раз.");
                },
                complete: function () {
                    $('#saveButton').removeAttr("disabled");
                }
            })
        } // end save

        $("#saveButton").click(save);

        /** Составляет код рекламной выгрузки */
        function generateScriptCode(informerId) {
            $("#informer-code").val(
                '<ins class="adsbyyottos" style="display:block" \n'+
                'data-ad-client="'+ informerId +'"></ins> \n'+
                '<script async src="https://cdn.yottos.com/loader.js"></script>'
            );
        }


        /** Инициализация интерфейса */
        function initInterface() {
            // Щелчёк по вкладке "Мои информеры" */
            $("#tabs").tabs({selected: 1}).bind('tabsselect', function (e, ui) {
                if (ui.index == 0) {
                    window.location = '/private/index#informers';
                    return true;
                }
                else
                    return true;
            });

            $("#informer-code").click(function () {
                this.select();
            });

        } // end init()

        function loadPattern(id) {
            for (var i = patterns.length - 1; i >= 0; i--) {
                if (patterns[i].guid == id) {
                    var guid = patterns[i].guid;
                    var title = patterns[i].title;
                    var lead0 = function (x) {
                        return (x >= 10) ? x : "0" + x;
                    }
                    var d = new Date();
                    advertise.height = patterns[i].height;
                    advertise.width = patterns[i].width;
                    advertise.height_banner = patterns[i].height_banner;
                    advertise.width_banner = patterns[i].width_banner;
                    advertise.options = patterns[i].options;
                    advertise.title = 'Dynamic' + ', ' + lead0(d.getDate()) + '.' + lead0(d.getMonth() + 1) + '.' + d.getFullYear();
                    $("#edit-informer-title").val(advertise.title);
                    printInformerTitle();
                    break;
                }
            }
        }

        /**
         * Строит интерфейс пользователя.
         */

        function init(options) {
            advertise = options.advertise;
            patterns = options.patterns || {};
            $.map(patterns, function (n) {
                n.options = $.extend({}, options.initialOptions, n.options);
            });
            initInterface();
            if (!advertise) {
                // Создание новой выгрузки
                advertise = {};
                $($(".listSizes a")[0]).click();
                $("#div-informer-code").hide();
                $("#informer-site").change();
                loadPattern(patterns[0].guid)
            } else {
                // Редактирование существующей выгрузки
                advertise.options = $.extend({}, options.initialOptions, advertise.options);
                $("#edit-informer-title").val(advertise.title);
                $("#informer-site").val(advertise.domain);
                advertise.domain = $("#informer-site").val();
                printInformerTitle();
                generateScriptCode(advertise.guid);
            }

        }

        return {
            init: init

        }

    })();
