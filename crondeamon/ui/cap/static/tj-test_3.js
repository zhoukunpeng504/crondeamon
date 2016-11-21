jQuery(function($) {
    var $body = $('body');
    var gct_s_id = $('meta[name="gct-id"]').attr('value');
    var gct_p_id = $body.data('gct');
    var $gcts = $('.gct');
    var depth = 0;
    $body.data('marked', gct_s_id+'.'+gct_p_id);

    var _find_closest_gct = function($elem) {
        var _result = [];
        var _current = $elem;
        var _continue = true;

        while(_continue) {
            var _p_current = _current.parent('.gct');

            if(_p_current.length === 0) {
                _p_current = _current.parent();
                if(_p_current.is('body')) {
                    _continue = false;
                }
            } else {
                _result.unshift(_p_current);
            }
            _current = _p_current;
        }

        return _result;
    }

    $('.gct a').each(function() {
        var _a = $(this);
        var _href = _a.attr('href');
        if(_a.is('.nogct') || _href.indexOf('javascript:')>=0 || _href.indexOf('#')===0) {
            return true;
        }
        var _p_gcts = _find_closest_gct(_a);
        _a.data('gcts', _p_gcts);
        if(_p_gcts.length > depth) {
            depth = _p_gcts.length;
        }
        $.each(_p_gcts, function(i, o) {
            var _o = $(o);
            _o.data('level', i);
            _o.addClass('gct-level-'+i);
        });
        var _parent_gct = _a.closest('.gct');
        _parent_gct.find('.gct').addClass('temp-gct');
        var _as = $('a:not(.temp-gct a)', _parent_gct);
        _a.data('mark', _as.index(_a)+1);
        _parent_gct.find('.temp-gct').removeClass('temp-gct');
    });

    for(var i = 0; i < depth; i++) {
        var _ls = $('.gct-level-'+i);
        _ls.each(function(n) {
            $(this).data('mark', n+1);
        });
    }

    $('.gct a').each(function() {
        var _a = $(this);
        var _href = _a.attr('href');
        if(_a.is('.nogct') || _href.indexOf('javascript:')>=0 || _href.indexOf('#')===0) {
            return true;
        }
        var _index = _a.data('mark');
        var _gcts = _a.data('gcts');
        var _marks = [];
        $.each(_gcts, function(i, o) {
            _marks.push($(o).data('mark'));
        });
        if(_href.indexOf('?') >= 0) {
            _href += "&gct="
        } else {
            _href += '?gct='
        }
        var _mark = gct_s_id+'.'+gct_p_id+'.'+_marks.join('-')+'.'+_index;
        _href += _mark;
        _a.attr('href', _href);
    });

    (function() {
        var _src = 'http://tj.yw.gongchang.com/gct.jpg';
        var _params = {
            url : location.href,
            refer : document.referrer,
            "gct-url" : ((location.href.match(/gct=[^\s&]*/g)||[])[0] || '').slice(4),
            "gct-refer" : ((document.referrer.match(/gct=[^\s&]*/g)||[])[0] || '').slice(4),
            "gct-cnt" : gct_s_id+'.'+gct_p_id+'.0.0',
            "devicetype" : (function(){
                var userAgentInfo = navigator.userAgent;
                var Agents = new Array("Android", "iPhone", "SymbianOS", "Windows Phone", "iPad", "iPod");
                var flag = "pc";
                for (var v = 0; v < Agents.length; v++) {
                if (userAgentInfo.indexOf(Agents[v]) > 0) { flag = "phone"; break; }
                }
                return flag;
            })()
        };
        var _params_str = $.extend(_params, window.siteConfig||{});
        new Image().src = _src+'?'+$.param(_params_str)
    })();
});
