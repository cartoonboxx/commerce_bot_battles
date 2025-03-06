import {updateDataWinners} from "../utils.js";

class Timer {
    selectors = {
        hours: '[data-js-hours]',
        minutes: '[data-js-minutes]',
        seconds: '[data-js-seconds]',
    }

    blockSelector = 'header__timer-block'

    constructor() {
        this.hoursElement = document.querySelector(this.selectors.hours);
        this.minutesElement = document.querySelector(this.selectors.minutes);
        this.secondsElement = document.querySelector(this.selectors.seconds);
        this.timerInterval = null;
        this.bindEvent();
    }

    bindEvent() {
        this.timerInterval = setInterval(() => {
            const currentTime = this.collectTimeToString()
            const calcedTime = this.calcTime(currentTime);
            this.setTimeAsElement(calcedTime);
        }, 1000)
        if (!this.hoursElement) {
            clearInterval(this.timerInterval)
        }
    }

    collectTimeToString() {
        let result = '';

        result += this.hoursElement.firstElementChild.textContent;
        result += this.hoursElement.lastElementChild.textContent;
        result += ':';
        result += this.minutesElement.firstElementChild.textContent;
        result += this.minutesElement.lastElementChild.textContent;
        result += ':';
        result += this.secondsElement.firstElementChild.textContent;
        result += this.secondsElement.lastElementChild.textContent;

        return result
    }

    setTimeAsElement(time) {
        time = time.replaceAll(':', '')
        time = time.split('')
        const isEndTimer = time.map(item => Number(item)).reduce((prev, curr) => {
            return curr > 0 ? curr + prev : prev;
        }, 0)

        if (!isEndTimer && document.querySelector('.container').classList.contains('winners')) {
            this.stopInterval()
            return
        }

        this.hoursElement.firstElementChild.textContent = time[0]
        this.hoursElement.lastElementChild.textContent = time[1]

        this.minutesElement.firstElementChild.textContent = time[2]
        this.minutesElement.lastElementChild.textContent = time[3]

        this.secondsElement.firstElementChild.textContent = time[4]
        this.secondsElement.lastElementChild.textContent = time[5]
    }

    calcTime(time) {
        const timeSplit = time.split(':');
        let hours = parseInt(timeSplit[0], 10);
        let minutes = parseInt(timeSplit[1], 10);
        let seconds = parseInt(timeSplit[2], 10);

        if (seconds > 0) {
            seconds--;
        } else {
            if (minutes > 0) {
                minutes--;
                seconds = 59;
            } else {

                if (hours > 0) {
                    hours--;
                    minutes = 59;
                    seconds = 59;
                } else {
                    const url = window.location.href.toString().split('/')

                    const prizeId = url[4]
                    fetch(`api/finish_prize?prize_id=${prizeId}`)
                        .then(res => {
                            return res.json()
                        })
                    .then(data => {
                        console.log(data)
                        updateDataWinners();
                    })

                    this.stopInterval()
                    console.log('Here')
                    updateDataWinners()

                    return '00:00:00';
                }
            }
        }

        const formattedHours = String(hours).padStart(2, '0');
        const formattedMinutes = String(minutes).padStart(2, '0');
        const formattedSeconds = String(seconds).padStart(2, '0');

        return `${formattedHours}:${formattedMinutes}:${formattedSeconds}`;
    }

    stopInterval() {
        document.querySelector('[data-js-time]').remove()
        clearInterval(this.timerInterval)
    }
}

new Timer()