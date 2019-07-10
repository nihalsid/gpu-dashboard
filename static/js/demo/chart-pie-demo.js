// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

window.xhr_json = function (type, url) {
    return new Promise((resolve, reject) => {
        let xhr0 = new XMLHttpRequest();
        xhr0.onreadystatechange = function() {
            if (this.readyState === 4 && this.status === 200) {
                let res = JSON.parse(this.response);
                resolve(res);
            }
        };
        xhr0.open(type, url, true);
        xhr0.send();
    });
};

// Pie Chart Example
xhr_json("GET", "user_distribution").then(data => {
  let ctx = document.getElementById("myPieChart");
  let myPieChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data['user'],
      datasets: [{
        data: data['usage'],
        backgroundColor: ["#0074D9", "#FF4136", "#2ECC40", "#FF851B", "#7FDBFF", "#B10DC9", "#FFDC00", "#001f3f", "#39CCCC", "#01FF70", "#85144b", "#F012BE", "#3D9970", "#111111", "#AAAAAA"],
        //backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc'],
        //hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
        hoverBorderColor: "rgba(234, 236, 244, 1)",
      }],
    },
    options: {
      maintainAspectRatio: false,
      tooltips: {
        backgroundColor: "rgb(255,255,255)",
        bodyFontColor: "#858796",
        borderColor: '#dddfeb',
        borderWidth: 1,
        xPadding: 15,
        yPadding: 15,
        displayColors: false,
        caretPadding: 10,
      },
      legend: {
        display: true,
        position: 'right'
      },
      cutoutPercentage: 80,
    },
  });  
})
