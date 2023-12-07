let CELL_HTML = '<div class="{0} cell col-xs-24 col-sm-24 col-md-24 radius4"><div class="title"><div>{0}</div></div><div class="info">这里预留的{0}图表</div></div>'
let KEYS = []
let UNIT = {}

String.prototype.format = function () {
    if (arguments.length === 0) {
        return this;
    }
    for (var s = this, i = 0; i < arguments.length; i++) {
        s = s.replace(new RegExp("\\{" + i + "\\}", "g"), arguments[i]);
    }
    return s;

};

function add_cell() {
    for (let n = 0; n < KEYS.length; n++) {
        let d = KEYS[n]
        d = d.replace(' ', '_')
        $(".main-content").append(CELL_HTML.format(d))
    }

}

function getKEYS() {
    $.ajax({
        url: "/iot/list",
        type: "GET",
        success: function (res) {
            let data;
            if (res.code === 200 && res.data.length !== 0) {
                KEYS = res.data
            }
            add_cell()
        },
        error: function (err) {
            console.log(err);
        }
    })
}


function getUNIT() {
    let key;
    for (let i = 0; i < KEYS.length; i++) {
        key = KEYS[i]
        $.get('/iot/{0}'.format(key), function (data, status) {
            UNIT.key = data
        })
    }
    console.log(UNIT)
}

getKEYS()
getUNIT()

