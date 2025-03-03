class UserCollector {

    containerElement = document.querySelector('.container')

    spanElement = document.querySelector('.main').querySelector('.invited')

    onlineElement = document.querySelector('.main').querySelector('.online-right-now')

    constructor() {
        this.bindEvents();
    }

    bindEvents() {
        setInterval(() => {
            this.collectAllUsers()
        }, 1000)
    }

    collectAllUsers() {
       fetch("api/users/", {
           method: "POST",
           body: {
               user_id: 35647463
           }
       })
           .then(res => res.json())
       .then(users => {
           this.containerElement.innerHTML = ''
           this.participants = users.map(user => {
               return {
                   id: user.fields.user_id,
                   invites: this.calcInvites(user, users)
               }
           })
           users.forEach(user => {
               this.updateUserList(user, users)
               this.updateInviteString(user, users)

           })
       })
    }

    updateUserList(user, users) {
        const { name, photo, user_id } = user.fields
        const chance = this.calculateChances(this.participants).find((item, index, array) => {
            if (user_id === item.id) {
                return item.chance
            }
        })
        const userObject = `
            <div class="user">
                <div class="user__img">
                    <img src="${photo}" alt="">
                </div>
                <div class="user__info">
                    <h3>${name}</h3>
                    <p><img src="/static/prizes_app/images/chance.png" alt="">${chance.chance.toFixed(2)}% шанс</p>
                </div>
                <div class="user__invites">
                    <p>${this.calcInvites(user, users)} <img src="/static/prizes_app/images/user-ico.png"></p>
                </div>
            </div>
        `
        this.containerElement.innerHTML += userObject

        // const winner = new Set()
        // while (winner.size < 2) {
        //     winner.add(this.pickWinner(this.participants).id)
        // }
        //
        // console.log(winner)
        // console.log('Победитель', this.pickWinner(this.participants))
    }

    pickWinner(participants, baseWeight = 1, coefficient = 1) {
        const totalWeight = participants.reduce(
            (sum, participant) => sum + (baseWeight + participant.invites * coefficient),
            0
        );

        let random = Math.random() * totalWeight;
        let remaining = random;

        for (const participant of participants) {
            const weight = baseWeight + participant.invites * coefficient;
            if (remaining <= weight) {
                return participant;
            }
            remaining -= weight;
        }

        return participants[participants.length - 1];
    }

    calculateChances(participants, baseWeight = 1, coefficient = 1) {
        const totalWeight = participants.reduce(
            (sum, participant) => sum + (baseWeight + participant.invites * coefficient),
            0
        );

        return participants.map(participant => ({
            ...participant,
            weight: baseWeight + participant.invites * coefficient,
            chance: ((baseWeight + participant.invites * coefficient) / totalWeight) * 100,
        }));
    }

    calcInvites(user, users) {
        const { user_id } = user.fields
        let count = 0;
        users.forEach((curUser) => {
            if (user_id == curUser.fields.invited_from) {
                count++
            }
        })

        return count;
    }

    updateInviteString(user, users) {
        let count = this.calcInvites(user, users);

        let tg = JSON.parse(localStorage.getItem('tg'))
        console.log(tg)

        if (user.fields.user_id == tg.user.id) {
            if (count > 0) {
                this.spanElement.textContent = `Вы пригласили ${count} участников`;
            }
            else {
                this.spanElement.textContent = "Вы пока не приглашали участников";
            }
        }

        this.onlineElement.textContent = users.length
    }

}

new UserCollector();