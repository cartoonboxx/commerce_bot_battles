class UserCollector {
    messages = {
        isNull: "Вы пока не приглашали участников",
        isCollected: `Вы пригласили N участников`
    }

    constructor() {
        this.bindEvents();
    }

    bindEvents() {
        setInterval(() => {
            this.collectAllUsers()
        }, 1000)
    }

    collectAllUsers() {
       // fetch("prizes_app/api/users", {
       //     method: "POST",
       //     body: {
       //
       //     }
       // })
       //     .then(res => res.json())
       // .then(users => {
       //     console.log(users)
       // })
    }

}

new UserCollector();