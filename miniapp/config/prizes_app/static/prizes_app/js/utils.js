export const updateDataWinners = () => {
    let mainElement = document.querySelector('main');
    mainElement.innerHTML = `
        <h4><span class="winner-count"></span> победителей</h4>
        <p>Бот автоматически определил 10 победителей среди 15 000 участников.
         Каждый получил по 100 Telegram Stars.</p>
        <div class="container">
         
        </div>
        <p class="tg-info"></p>
        <a href="{{ url_button }}" class="invite_users">Пригласить друзей</a>
    `

    const containerElement = document.querySelector('.container');

    fetch("api/users", {
        method: "POST",
        body: {
            user_id: 35647463
        }
    })
        .then(res => res.json())
        .then(users => {
            users.forEach(user => {
                console.log(user)
                const { photo, name } = user.fields

                const userElement = `
                <div class="user">
                    <div class="user__img">
                        <img src="${photo}" alt="">
                    </div>
                    <div class="user__info">
                        <h3>change ${name}</h3>
                        <p><img src="/static/prizes_app/images/chance.png" alt=""> шанс</p>
                    </div>
                    <div class="user__invites">
                        <p> <img src="/static/prizes_app/images/user-ico.png"></p>
                    </div>
                </div>
            `
                containerElement.innerHTML += userElement
            })
        })

}

