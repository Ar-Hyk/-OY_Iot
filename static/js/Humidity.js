var ctx = document.getElementById('Humidity');
var data = {
    labels: [
        'dry',
        'damp',
    ],
    datasets: [{
        label: '环境湿度',
        data: [0.1, 0.9],
        backgroundColor: [
            'rgb(255, 99, 132)',
            'rgb(54, 162, 235)',
        ],
        hoverOffset: 4
    }]
};
var config = {
    type: 'doughnut',
    data: data,
    options: {
        responsive: false, // 设置图表为响应式，根据屏幕窗口变化而变化
        maintainAspectRatio: false,// 保持图表原有比例
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }
    }
};
new Chart(ctx, config);
