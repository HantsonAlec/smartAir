'use strict';
let html_sensor,
    html_menu_btn,
    html_menu,
    html_menu_icon,
    html_slider,
    html_historie_cards,
    html_tip,
    html_data_ophalen,
    html_power,
    html_datepicker,
    sensorChart,
    myChart,
    bigChart = '';
const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
var bar;
// Data tonen show__
//Door tips heen gaan
const showTips = function () {
    var current = 0,
        slides = document.getElementsByTagName('p');
    setInterval(function () {
        for (var i = 0; i < slides.length; i++) {
            slides[i].style.opacity = 0;
        }
        current = current != slides.length - 1 ? current + 1 : 0;
        slides[current].style.opacity = 1;
    }, 10000);
};
const showChart = function (jsonObject) {
    //Controleren als er data voor gekozen dag  is
    if (Object.keys(jsonObject).length === 0) {
        alertify.error('Geen data voor deze periode');
    }
    const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
    if (jsonObject.length != 0) {
        let sensor = jsonObject[0]['Sensor'];
        let beschrijving = jsonObject[0]['Beschrijving'];
        let kleur = jsonObject[0]['Kleur'];
        let converted_labels = [];
        let converted_data = [];
        for (const meting of jsonObject) {
            converted_data.push(meting.Waarde);
            converted_labels.push(meting.timestamp.substring(0, 22));
        }
        if (document.querySelector('.js-index')) {
            drawChart(converted_labels, converted_data, sensor, kleur);
        } else if (document.querySelector('.js-historiek')) {
            //Aan de hand van schermgrote bepalen welke historiek moet getoond worden
            if (vw <= 375) {
                showHistorie(jsonObject);
            }
            drawBigChart(converted_labels, converted_data, sensor, kleur, beschrijving);
        }
    }
};
const showHistorie = function (jsonObject) {
    //Historiek op gsm tonen
    let html = '';
    let dagen = {
        Mon: 'Maandag',
        Tue: 'Dinsdag',
        Wed: 'Woensdag',
        Thu: 'Donderdag',
        Fri: 'Vrijdag',
        Sat: 'Zaterdag',
        Sun: 'Zondag',
    };
    const kleur = jsonObject[0]['Kleur'];
    console.log(kleur);
    for (const meting of jsonObject) {
        const datum = meting.timestamp;
        const waarde = meting.Waarde;
        const beschrijving = meting.Beschrijving;
        const meeteenheid = meting.Meeteenheid;
        const dateNr = datum.substring(5, 7);
        const tijd = datum.substring(16, 22);
        const dagEN = datum.substring(0, 3);
        const dag = dagen[dagEN];
        html += `<div class="c-historie-card">
                        <h1 class="c-historie-datumNr">${dateNr}</h1>
                        <h2 class="c-historie-datum">${dag} ${tijd}</h2>
                        <div class="c-historie-meting">
                        <p class="c-historie-metingNaam">${beschrijving}</p>
                        <p class="c-historie-metingNr">${waarde}${meeteenheid}</p>
                        </div>
                    </div>`;
    }
    html_historie_cards.innerHTML = html;
    const nummers = document.querySelectorAll('.c-historie-metingNr');
    for (const nummer of nummers) {
        nummer.style.fontWeight = 800;
        nummer.style.color = kleur;
    }
};
// Grafiek tekenen draw__
//Kleine grafieken voor op index pagina
const drawChart = function (labels, converted_data, sensor, kleur) {
    let ctx = document.querySelector(`#${sensor}`).getContext('2d');
    var gradient = ctx.createLinearGradient(0, 0, 0, 100);
    gradient.addColorStop(0, kleur.replace(')', ', 1)').replace('rgb', 'rgba'));
    gradient.addColorStop(1, kleur.replace(')', ', 0)').replace('rgb', 'rgba'));
    let config = {
        type: 'line', //Type chart
        data: {
            labels: labels, //Labels op de chart tonen
            datasets: [
                {
                    label: 'data', //Hoofdlabel
                    backgroundColor: gradient,
                    borderColor: kleur,
                    data: converted_data,
                    fill: 'start',
                },
            ],
        },
        options: {
            responsive: true,
            title: {
                display: false,
                text: 'Sensor grafiek',
            },
            elements: { point: { radius: 0 } },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: false,
            },
            legend: {
                display: false,
            },
            scales: {
                xAxes: [
                    {
                        display: false,
                        scaleLabel: {
                            display: false,
                        },
                    },
                ],
                yAxes: [
                    {
                        display: false,
                        scaleLabel: {
                            display: false,
                        },
                        ticks: {
                            beginAtZero: true,
                        },
                    },
                ],
            },
        },
    };
    myChart = new Chart(ctx, config);
};
//Grote grafiek voor op historiek pagina
const drawBigChart = function (labels, converted_data, sensor, kleur, beschrijving) {
    let ctx = document.querySelector('#myChart').getContext('2d');
    var gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, kleur.replace(')', ', 1)').replace('rgb', 'rgba'));
    gradient.addColorStop(1, kleur.replace(')', ', 0)').replace('rgb', 'rgba'));
    let config = {
        type: 'line', //Type chart
        data: {
            labels: labels, //Labels op de chart tonen
            datasets: [
                {
                    label: beschrijving, //Hoofdlabel
                    backgroundColor: gradient,
                    borderColor: kleur,
                    data: converted_data,
                    fill: 'start',
                },
            ],
        },
        options: {
            responsive: true,
            title: {
                display: false,
                text: 'Sensor grafiek',
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: false,
            },
            legend: {
                display: true,
            },
            scales: {
                xAxes: [
                    {
                        display: true,
                        scaleLabel: {
                            display: true,
                        },
                    },
                ],
                yAxes: [
                    {
                        display: true,
                        scaleLabel: {
                            display: true,
                        },
                        ticks: {
                            beginAtZero: true,
                        },
                    },
                ],
            },
        },
    };
    if (bigChart) {
        bigChart.destroy();
    }
    bigChart = new Chart(ctx, config);
};
//Progressbar tekenen
const drawProgress = function (score) {
    let progressbar = document.querySelector('.c-progressbar');
    let config = {
        strokeWidth: 6,
        color: '#FFEA82',
        trailColor: '#eee',
        trailWidth: 1,
        easing: 'easeInOut',
        duration: 1400,
        svgStyle: null,
        text: {
            value: '',
            alignToBottom: true,
        },
        from: { color: '#ED6A5A' },
        to: { color: '#32CD32' },
        step: (state, bar) => {
            bar.path.setAttribute('stroke', state.color);
            var value = Math.round(bar.value() * 100);
            bar.setText(value);
            bar.text.style.color = state.color;
        },
    };
    if (bar) {
        bar.destroy();
    }
    bar = new ProgressBar.SemiCircle(progressbar, config);
    bar.text.style.fontFamily = '"Raleway", Helvetica, sans-serif';
    bar.text.style.fontSize = '4rem';
    let animate = score / 100;
    bar.animate(animate);
};
// Data ophalen get__
const getSensorData = function (sensor) {
    handleData(`http://${lanIP}/api/v1/chart/${sensor}`, showChart);
};
const getSensorDataByDate = function (tijd, sensor) {
    handleData(`http://${lanIP}/api/v1/chart/${tijd}/${sensor}`, showChart);
};
const getSensorDataByDatePicker = function (tijd, sensor) {
    handleData(`http://${lanIP}/api/v1/chart/picker/${tijd}/${sensor}`, showChart);
};
const getSensorDataByWeekPicker = function (tijd, sensor) {
    handleData(`http://${lanIP}/api/v1/chart/weekpicker/${tijd}/${sensor}`, showChart);
};
// Luisteren naar listen__
const listenToSocketIndex = function () {
    //Socket connect
    socket.on('connected', function () {
        console.log('verbonden met socket zwebserver');
    });
    //Laatste metingen ophalen en tonen
    socket.on('B2F_latest_measurements', function (jsonObject) {
        let html = '';
        console.log('Dit zijn de metingen');
        console.log(jsonObject);
        for (const object of jsonObject['measurements']) {
            const naam = object['naam'];
            let waarde = object['waarde'];
            const meeteenheid = object['meeteenheid'];
            const recent = object['recent'];
            const beschrijving = object['beschrijving'];
            const code = object['codeSens'];
            if (recent == 0) {
                waarde = 0;
            }
            getSensorDataByDate('day', code);
            html += `<div class="o-layout__item  u-1-of-4-bp3 c-chart-card u-max-width-xs u-mb-lg js-chart-card" data-sens="${code}">
            <div class="js-sensor-title ">${beschrijving}</div>
            <div class="js-sensor-waarde c-chart-card-waarde">${waarde} ${meeteenheid}</div>
            <canvas id="${code}" class='c-chartCanvas' width="200" height="50"></canvas>
            </div>`;
        }
        let score = jsonObject['score'];
        if (Number.isInteger(score) == false) {
            score = jsonObject['score']['score'];
            let recent = jsonObject['score']['recent'];
            if (recent == 0) {
                score = 0;
            }
        }
        drawProgress(score);
        html_sensor.innerHTML = html;
        listenToCards();
    });
    socket.on('B2F_tips', function (jsonObject) {
        let html = '';
        for (const object of jsonObject['tips']) {
            const tip = object['Tip'];
            html += `<p>${tip}</p>`;
        }
        html_tip.innerHTML = html;
        showTips();
    });
    socket.on('B2F_dataStart', function () {
        console.log('DataStart');
        html_data_ophalen.style.opacity = 1;
    });
    socket.on('B2F_dataOphalen_klaar', function () {
        html_data_ophalen.style.opacity = 0;
    });
};
const listenToSocketSettings = function () {
    socket.on('B2F_acuator_data', function (jsonObject) {
        // console.log('hier');
        console.log(jsonObject);
        //VOOR FAN
        let value = jsonObject['acuator'][0]['waarde'];
        let recent = jsonObject['acuator'][0]['waarde'];
        if (recent == 0) {
            value = 0;
        }
        console.log(value);
        document.querySelector('.js-fan-btn').value = value;
        if (value == 0) {
            html_slider.classList.remove('c-slider-on');
        } else if (value == 100) {
            html_slider.classList.add('c-slider-on');
        }
        //VOOR RGB
        let valueRGB = jsonObject['acuator'][1]['waarde'];
        let recentRGB = jsonObject['acuator'][1]['waarde'];
        if (recentRGB == 0) {
            valueRGB = 0;
        }
        console.log(valueRGB);

        if (valueRGB == 6) {
            document.querySelector('.c-slider-rgb').classList.remove('c-slider-on-rgb');
            document.querySelector('.js-rgb-btn').value = 'OFF';
        } else {
            document.querySelector('.c-slider-rgb').classList.add('c-slider-on-rgb');
            document.querySelector('.js-rgb-btn').value = 'ON';
        }
    });
};
const listenToTime = function (sensor) {
    const btns = document.querySelectorAll('.js-tijdOptie');
    for (let btn of btns) {
        btns[0].classList.add('c-btn-active');
        btn.addEventListener('click', function () {
            for (btn of btns) {
                btn.classList.remove('c-btn-active');
            }
            console.log('click');
            const tijd = this.getAttribute('data-tijd');
            this.classList.add('c-btn-active');
            if (tijd == 'totaal') {
                getSensorData(sensor);
            } else if (tijd == 'hour') {
                console.log(tijd, sensor);
                getSensorDataByDate(tijd, sensor);
            } else if (tijd == 'day') {
                html_datepicker = flatpickr('.flatpickr', {
                    disableMobile: 'true',
                    maxDate: 'today',
                    onChange: function (selectedDates) {
                        console.log(selectedDates[0]);
                        const year = selectedDates[0].getFullYear();
                        const day = selectedDates[0].getDate();
                        const month = selectedDates[0].getMonth();
                        const datum = `${year}-${month + 1}-${day}`;
                        console.log(sensor, datum);
                        getSensorDataByDatePicker(datum, sensor);
                    },
                });
                html_datepicker.open();
            } else if (tijd == 'week') {
                html_datepicker = flatpickr('.flatpickr', {
                    plugins: [new weekSelect({})],
                    disableMobile: 'true',
                    mode: 'range',
                    maxDate: 'today',
                    onChange: function () {
                        const weekNumber = this.selectedDates[0]
                            ? this.config.getWeek(this.selectedDates[0])
                            : null;
                        console.log(weekNumber);
                        getSensorDataByWeekPicker(weekNumber, sensor);
                    },
                });
                html_datepicker.open();
            }
        });
    }
};
const listenToUI = function () {
    const buttonFan = document.querySelector('.js-fan-btn');
    const buttonRGB = document.querySelector('.js-rgb-btn');
    buttonFan.addEventListener('click', function () {
        console.log('FAN');
        const acuator = this.getAttribute('data-acuator');
        html_slider.classList.toggle('c-slider-on');
        let value = this.value;
        if (value == 0) {
            this.value = 100;
        } else if (value == 100) {
            this.value = 0;
        }
        console.log(value);
        socket.emit('F2B_switch_fan', { value: this.value, acuator: acuator });
    });
    buttonRGB.addEventListener('click', function () {
        const acuator = this.getAttribute('data-acuator-RGB');
        console.log(acuator);
        let value = this.value;
        if (value == 'OFF') {
            this.value = 'ON';
        } else if (value == 'ON') {
            this.value = 'OFF';
        }
        document.querySelector('.c-slider-rgb').classList.toggle('c-slider-on-rgb');
        socket.emit('F2B_switch_rgb', { value: this.value, acuator: acuator });
    });
    html_power.addEventListener('click', function () {
        alertify
            .confirm(
                'Jammer dat je weg gaat :(',
                'Ben je zeker dat je het systeem wilt afsluiten?',
                function () {
                    socket.emit('F2B_power_off');
                },
                function () {
                    alertify.error('Actie geannuleerd');
                }
            )
            .set('labels', { ok: 'Zeker!', cancel: 'Nee toch niet!' });
    });
};
const listenToCards = function () {
    const cards = document.querySelectorAll('.js-chart-card');
    for (const card of cards) {
        card.addEventListener('click', function () {
            console.log('click');
            const sensor = this.getAttribute('data-sens');
            window.location = `/historiek.html?sensor=${sensor}`;
        });
    }
};
const listenToMenu = function () {
    html_menu_btn.addEventListener('click', function () {
        let value = this.getAttribute('data-toggle');
        if (value == 0) {
            html_menu.classList.add('c-header__nav-visible');
            this.setAttribute('data-toggle', 100);
            html_menu_icon.innerHTML = 'close';
        } else if (value == 100) {
            html_menu.classList.remove('c-header__nav-visible');
            this.setAttribute('data-toggle', 0);
            html_menu_icon.innerHTML = 'menu';
        }
    });
};
const init = function () {
    console.info('DOM geladen');
    html_sensor = document.querySelector('.js-sensor');
    html_menu_btn = document.querySelector('.js-hamburger');
    html_menu = document.querySelector('.c-header__nav');
    html_menu_icon = document.querySelector('.js-menu-icon');
    listenToMenu();
    if (document.querySelector('.js-index')) {
        html_tip = document.querySelector('.js-tip');
        html_data_ophalen = document.querySelector('.js-dataLoading');
        listenToSocketIndex();
    } else if (document.querySelector('.js-historiek')) {
        html_historie_cards = document.querySelector('.js-historie-cards');
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const sensor = urlParams.get('sensor');
        getSensorData(sensor);
        listenToTime(sensor);
    } else if (document.querySelector('.js-settings')) {
        html_slider = document.querySelector('.c-slider');
        html_power = document.querySelector('.js-power-btn');
        listenToSocketSettings();
        listenToUI();
    }
};

document.addEventListener('DOMContentLoaded', init);
