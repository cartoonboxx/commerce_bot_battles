'use strict'

export const updateDataWinners = () => {
    let mainElement = document.querySelector('main');
    mainElement.innerHTML = `
        <h4><span class="winner-count"></span> победителей</h4>
        <p class="text-info">Бот автоматически определил 10 победителей среди 15 000 участников.
         Каждый получил по 100 Telegram Stars.</p>
        <div class="container winners">
         
        </div>
        <p class="tg-info"></p>
        <a href="{{ url_button }}" class="invite_users">Пригласить друзей</a>
    `

    const prizeId = window.location.href.split('/')[4]

    fetch(`api/collect_winners?prize_id=${prizeId}`, {
        method: 'GET',
    })
    .then(res => res.json())
    .then(winners => {
        console.log(winners)

        document.querySelector('.winner-count').textContent = winners.length

        const containerElement = document.querySelector('.container')
        winners.forEach((winner) => {
            const { photo, name, chance, invites } = winner
            containerElement.innerHTML += `
                <div class="user">
                    <div class="user__img">
                        <img src="${photo}" alt="">
                    </div>
                    <div class="user__info">
                        <h3>${ name }</h3>
                        <p><img src="/static/prizes_app/images/chance.png" alt="">${Number(chance).toFixed(2)}% шанс
                        <img src="/static/prizes_app/images/user-ico.png">${invites}
                        </p>
                    </div>
                    <div class="user__invites">
                        <p>+${document.querySelector('.header__upper__stars')
                                        .querySelector('h1').textContent / winners.length}
                        <img src="/static/prizes_app/images/ministar.png"></p>
                    </div>
                </div>
            `
        })
    })


    fetch(`api/data?prize_id=${prizeId}`, {
        method: 'GET',
    })
    .then(res => {
        if (!res.ok) {
            console.error('Ошибка при запросе к API:', res.status, res.statusText);
            throw new Error('Ошибка сети или сервера');
        }

        return res.json()
    })
    .then(data => {
        const { prize_info, users } = data
        document.querySelector('.header__text').innerHTML = `Раздача Telegram Stars<br>Встречайте победителей!`
        console.log('help')
        document.querySelector('.text-info').textContent = `
        Бот автоматически определил ${prize_info.count_winners} победителей среди ${users.length} участников.
         Каждый получил по ${prize_info.tg_stars / prize_info.count_winners} Telegram Stars.
        `
        document.querySelector('.header__paragraph').textContent = `Розыгрыш завершился в ${prize_info.endTime}`
        document.querySelector('.invite_users').remove()


    })
    .catch(error => {
        console.error('Произошла ошибка:', error);
    });

}

