/**
 * Date: 2015/6/4
 * Update: 2015/6/4
 */

define(function (require, exports, module) {

    var $ = require('$'),
        Popup = require('abc/x-dialog/0.0.2/dialog');

    require('abc/jqgrid/4.6.0/grid.locale-cn');
    require('abc/jqgrid/4.6.0/jquery.jqGrid');
    $('head').append('<style>#gbox_table,#gview_table,.ui-jqgrid-hdiv,.ui-jqgrid-bdiv,#pager2,.ui-jqgrid-btable,.ui-jqgrid-htable{width: 100% !important;}</style>');
    var selector = $('#table');

    selector.jqGrid({
        datatype: "json",
        url: window.gridUrl,
        rowNum: 15,
        autoWidth: false,
        shrinkToFit: true,
        //rowList:[10,20,30],
        loadtext: "",
        height:  540,
        pager: '#table-pager',
        viewrecords: true,
        recordpos: 'right',
        colNames:['任务ID','任务名','状态','时间规则','所属项目','所属应用','功能','操作'],
        cmTemplate: {sortable: false, search: false},
        colModel: [{
            width: 50
        },{
            width: 90
        },{
            width: 60
        },{
            width: 70
        },{
            width: 80
        },{
            width: 80
        },{
            width: 100
        },{
            width: 150,
            formatter: function (value, options, rData) {

                return '<a href="#">禁用</a> <a href="#">修改</a> <a href="#">运行记录</a> <a href="#">立刻触发</a>';
            }
        }],
        loadComplete: function () {
            selector.setGridWidth($('.main-container').width());
        }
    });



    var dialog;

    $('#create-button').click(function () {
        dialog = Popup.show({
            content: $('#exampleModal').html()
        })
    });

    $(document).on('click', '.x-dialog-main .btn-default', function () {
        dialog.hide();
    }).on('submit', '#form1', function (e) {
        e.preventDefault();

        $.post(this.action, $(this).serialize(), function (d) {
             Popup.alert(d.message, d.status);
             if (d.status) {
                 dialog.hide();
                 selector.jqGrid().trigger('reloadGrid');
             }
        }, 'json');

        return false;

    }).on('submit','#form2', function (e) {
        e.preventDefault();

        var item = $(this).find('select, input[type="text"]');
        var obj = {
            page: 1,
            url: this.action + '?' + $(this).serialize()
        };

        selector.jqGrid('setGridParam', obj).trigger('reloadGrid');

        return false;
    });

    $(window).on('resize', function () {
        selector.setGridWidth($('.main-container').width())
    });

});
