'use strict'

class UserEvent {
    tg = window.Telegram.WebApp;

    constructor() {
        localStorage.setItem('tg', JSON.stringify(this.tg.initDataUnsafe))

        this.prize_id = parseInt(window.location.href.split('/')[4])
        if (this.tg) {
            const { id: userId, first_name: name, photo_url: photo } = this.tg.initDataUnsafe.user;
            this.userId = userId;
            this.name = name
            this.photo = photo
            this.addUser()
            this.bindEvents()
            this.updateLink()
        }
    }

    bindEvents() {
        window.addEventListener('focus', function(event) {
            this.addUser();
        });

        window.addEventListener('focusout', function(event) {
            this.removeUser();
        });

        window.addEventListener('load', (event) => {
            this.addUser();
        });

        document.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'hidden') {
                this.removeUser();
            }
        });

        window.addEventListener('beforeunload', function() {
            this.removeUser();
        });
    }

    addUser() {
        fetch(`api/adduser?user_id=${this.userId}&name=${this.name}&photo=${this.photo}&prize_id=${this.prize_id}`)
        .then(res => res.json())
        .then(json => {
            console.log(json);
        })
    }

    removeUser() {
        fetch(`api/removeuser?user_id=${this.userId}&prize_id=${this.prize_id}`)
            .then(res => res.json())
            .then(json => {
                console.log(json)
            })
    }

    updateLink() {
        const base_url = 'https://t.me/share/url'
        const share_url = `https://t.me/vndfkjnkjdfgbknvds_bot?start=prizeApp_${this.prize_id}_from_${this.userId}`
        const text = "Привет, "
        const { encoded_text, encoded_url } = this.encodeTextAndUrl(text, share_url);
        const full_url = `${base_url}?url=${encoded_url}&text=${encoded_text}`

        document.querySelector('.invite_users').setAttribute('href', `${full_url}`);
    }

    encodeTextAndUrl(text, share_url) {
        // Проверяем, что text и share_url существуют
        if (text === undefined || text === null) {
            console.warn("Text is undefined or null. Returning empty string for encoded_text.");
            var encoded_text = "";
        } else {
            var encoded_text = encodeURIComponent(text);
        }

        if (share_url === undefined || share_url === null) {
            console.warn("share_url is undefined or null. Returning empty string for encoded_url.");
            var encoded_url = "";
        } else {
            var encoded_url = encodeURIComponent(share_url);
        }


        return { encoded_text, encoded_url };
    }
}

new UserEvent();
