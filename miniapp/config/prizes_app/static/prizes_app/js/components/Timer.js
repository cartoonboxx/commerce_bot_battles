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
        this.bindEvent();
    }

    bindEvent() {
        setInterval(() => {
            const currentTime = this.collectTimeToString()
            const calcedTime = this.calcTime(currentTime);
            this.setTimeAsElement(calcedTime);
        }, 1000)
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

        // Вычитаем одну секунду
        if (seconds > 0) {
            seconds--;
        } else {
            // Если секунды равны 0, уменьшаем минуты
            if (minutes > 0) {
                minutes--;
                seconds = 59; // Устанавливаем секунды на 59
            } else {
                // Если минуты тоже равны 0, уменьшаем часы
                if (hours > 0) {
                    hours--;
                    minutes = 59; // Устанавливаем минуты на 59
                    seconds = 59; // Устанавливаем секунды на 59
                } else {
                    console.log('Отправляем запрос'); // Если время закончилось
                    return '00:00:00'; // Возвращаем 00:00:00, если время закончилось
                }
            }
        }

        // Форматируем время с ведущими нулями
        const formattedHours = String(hours).padStart(2, '0');
        const formattedMinutes = String(minutes).padStart(2, '0');
        const formattedSeconds = String(seconds).padStart(2, '0');

        return `${formattedHours}:${formattedMinutes}:${formattedSeconds}`;
    }

}

new Timer();