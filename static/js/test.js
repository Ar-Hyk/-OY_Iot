var url = '20.187.248.206'
var port = 12588
var token = 'iot_test'

const d_info = document.getElementById('info')
const d_key = document.getElementById('key')

var settings = {
    "url": "http://" + url + ":" + port + "/iot/list",
    "method": "GET",
};
$.ajax(settings).done(function (response) {
    if (response.code == 200) {
        for (let i = 0; i < response.data.length; i++) {
            const key = response.data[i];
            const wrapper = document.createElement('li')
            wrapper.innerHTML = `<a class='dropdown-item'>${key}</a>`,
                d_key.append(wrapper)
        }
    } else {
        alert(response, danger)
    }
});


// 警告框
const alert = (message, type) => {
    const wrapper = document.createElement('div')
    wrapper.innerHTML = [
        `<div class="alert alert-${type} alert-dismissible" role="alert">`,
        `   <div>${message}</div>`,
        '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
        '</div>'
    ].join('')
    d_info.append(wrapper)
}

function updata(key, unit, st, et) {
    var settings = {
        "url": "http://" + url + ":" + port + "/query?token=" + token + "&key=" + key + "&unit=" + unit + "&st=" + st + "&et=" + et,
        "method": "GET",
    };

    $.ajax(settings).done(function (response) {
        if (response.code === 200) {
            d_info.innerHTML = [
                `<h3>更新时间${new Date()}</h3>`,
                '<h4>返回结果如下：</h4>',
                `<span>${JSON.stringify(response)}</span>`
            ]
        } else {
            alert(response, 'danger')
        }
    });
}


setInterval(function () {
    updata('CH2O', 'PPM', parseInt(Date.now() / 100), parseInt(Date.now() / 100) - 3600)
}, 2000);