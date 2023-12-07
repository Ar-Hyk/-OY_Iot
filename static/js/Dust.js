var ctx = document.getElementById('Dust');
var labels = ['7', '8', '9', '10', '11', '12', '13'];  // 设置 X 轴上对应的标签
var data = {
    labels: labels,
    datasets: [{
        label: '粉尘',
        data: [65, 59, 80, 81, 56, 55, 40],
        fill: false,
        borderColor: 'rgb(54, 162, 235)', // 设置线的颜色
        backgroundColor: ['rgba(75, 192, 192, 0.2)'],// 设置点的填充色
        pointStyle: 'circle',     //设置点类型为圆点
        pointRadius: 6,    //设置圆点半径
        pointHoverRadius: 10, //设置鼠标移动上去后圆点半径
        tension: 0.1
    }]
};
var config = {
    type: 'line', // 设置图表类型
    data: data,
    options: {
        responsive: true,  // 设置图表为响应式

        interaction: {  // 设置每个点的交互
            intersect: false,
        },
        scales: {  // 设置 X 轴与 Y 轴
            x: {
                display: true,
                title: {
                    display: true,
                    text: '时间'
                }
            },
            y: {
                display: true,
                title: {
                    display: true,
                    text: 'mg/m^3'
                }
            }
        }
    }
};
new Chart(ctx, config);
