const ctx = document.getElementById('CH2O');

const data = [];
const data2 = [];
let prev = 100;
let prev2 = 80;
for (let i = 0; i < 1000; i++) {
    prev += 5 - Math.random() * 10;
    data.push({x: i, y: prev});
    prev2 += 5 - Math.random() * 10;
    data2.push({x: i, y: prev2});
}

const config = {
    type: 'line',
    data: data,
    options: {
        responsive: true,  // 设置图表为响应式
        interaction: {  // 设置每个点的交互
            intersect: false,
        },
        scales: {  // 设置 X 轴与 Y 轴
            x: {
                type: 'linear',
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
    },
    plugins: []
};


const labels = ['7', '8', '9', '10', '11', '12', '13'];  // 设置 X 轴上对应的标签


// const config = {
//   type: 'line', // 设置图表类型
//   data: data,
//   options: {
//     responsive: true,  // 设置图表为响应式
//     plugins: {
//       legend: false
//     },
//     interaction: {  // 设置每个点的交互
//       intersect: false,
//     },
//     scales: {  // 设置 X 轴与 Y 轴
//
//       x: {
//         type: 'linear',
//         display: true,
//         title: {
//           display: true,
//           text: '时间'
//         }
//       },
//       y: {
//         display: true,
//         title: {
//           display: true,
//           text: 'mg/m^3'
//         }
//       }
//     }
//   }
// };
new Chart(ctx, config);

