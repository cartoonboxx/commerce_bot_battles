let tg = window.Telegram.WebApp;

localStorage.setItem('tg', JSON.stringify(tg.initDataUnsafe))

const { id: userId, first_name: name, photo_url: photo } = tg.initDataUnsafe.user;

fetch(`api/adduser?user_id=${userId}&name=${name}&photo=${photo}`, {
    method: 'GET',
})
.then(res => res.json())
.then(json => {
    console.log(json);
})


