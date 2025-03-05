'use strict'

let tg = window.Telegram.WebApp;

localStorage.setItem('tg', JSON.stringify(tg.initDataUnsafe))

const { id: userId, first_name: name, photo_url: photo } = tg.initDataUnsafe.user;

fetch(`api/adduser?user_id=${userId}&name=${name}&photo=${photo}`)
    .then(res => res.json())
    .then(json => {
        console.log(json);
    })

window.addEventListener('focus', function(event) {
    fetch(`api/adduser?user_id=${userId}&name=${name}&photo=${photo}`)
    .then(res => res.json())
    .then(json => {
        console.log(json);
    })
});

window.addEventListener('focusout', function(event) {
    fetch(`api/removeuser?user_id=${userId}`)
        .then(res => res.json())
        .then(json => {
            console.log(json)
        })
});

window.addEventListener('load', (event) => {
    fetch(`api/adduser?user_id=${userId}&name=${name}&photo=${photo}`)
        .then(res => res.json())
        .then(json => {
            console.log(json);
    })
})

document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'hidden') {
        fetch(`api/removeuser?user_id=${userId}`)
            .then(res => res.json())
            .then(json => {
                console.log(json)
            })
    }
});

window.addEventListener('beforeunload', function() {
    fetch(`api/removeuser?user_id=${userId}`)
        .then(res => res.json())
        .then(json => {
            console.log(json)
        })

});
