from database import db

'''
1 - 10 голосов = 6 рублей = 0.07 usdt = 6 звезд
11 - 20 голосов = 8 рублей = 0.09 usdt = 7 звезд
21 - 30 голосов = 9 рублей = 0.10 usdt = 8 звезд
31 - 40 голосов = 10 рублей = 0.11 usdt = 9 звезд
41 - 50 голосов = 11 рублей = 0.12 usdt = 10 звезд
51 - 60 голосов = 12 рублей = 0.13 usdt = 11 звезд
61 - 70 голосов = 13 рублей = 0.14 usdt = 12 звезд
71 - 80 голосов = 14 рублей = 0.15 usdt = 13 звезд
81 - 90 голосов = 15 рублей = 0.16 usdt = 14 звезд
91 - 100 голосов = 16 рублей = 0.17 usdt = 15 звезд
101 - 110 голосов = 17 рублей = 0.18 usdt = 16 звезд
111 - 120 голосов = 18 рублей = 0.19 usdt = 17 звезд
121 - 130 голосов = 19 рублей = 0.20 usdt = 18 звезд
131 - и выше голосов = 20 рублей = 0.21 usdt = 19 звезд
'''

currency_converter = {
    0: {
        "ruble": 0,
        "crypto": 0,
        "stars": 0
    },
    1: {
        "ruble": 6,
        "crypto": 0.07,
        "stars": 6
    },
    2: {
        "ruble": 8,
        "crypto": 0.09,
        "stars": 7
    },
    3: {
        "ruble": 9,
        "crypto": 0.1,
        "stars": 8
    },
    4: {
        "ruble": 10,
        "crypto": 0.11,
        "stars": 9
    },
    5: {
        "ruble": 11,
        "crypto": 0.12,
        "stars": 10
    },
    6: {
        "ruble": 12,
        "crypto": 0.13,
        "stars": 11
    },
    7: {
        "ruble": 13,
        "crypto": 0.14,
        "stars": 12
    },
    8: {
        "ruble": 14,
        "crypto": 0.15,
        "stars": 13
    },
    9: {
        "ruble": 15,
        "crypto": 0.16,
        "stars": 14
    },
    10: {
        "ruble": 16,
        "crypto": 0.17,
        "stars": 15
    },
    11: {
        "ruble": 17,
        "crypto": 0.18,
        "stars": 16
    },
    12: {
        "ruble": 18,
        "crypto": 0.19,
        "stars": 17
    },
    13: {
        "ruble": 19,
        "crypto": 0.2,
        "stars": 18
    },
    14: {
        "ruble": 20,
        "crypto": 0.21,
        "stars": 19
    }
}

async def money_calc(user_id, battle_id, votes: int, currency: str):
    ''' currecy = "ruble" | "stars" | "crypto" '''

    await db.update_donations(user_id, battle_id)
    user_info = await db.get_user_from_donations(user_id, battle_id)
    votes_bought = user_info[3]

    calced_sum = 0


    for i in range(votes_bought, votes_bought + votes + 1):
        calced_sum += calc(i, currency)

    return calced_sum

def calc(vote, currency):
    ''' currecy = "ruble" | "stars" | "crypto" '''
    if vote in range(1, 11):
        return currency_converter[1][currency]
    elif vote in range(11, 21):
        return currency_converter[2][currency]
    elif vote in range(21, 31):
        return currency_converter[3][currency]
    elif vote in range(31, 41):
        return currency_converter[4][currency]
    elif vote in range(41, 51):
        return currency_converter[5][currency]
    elif vote in range(51, 61):
        return currency_converter[6][currency]
    elif vote in range(61, 71):
        return currency_converter[7][currency]
    elif vote in range(71, 81):
        return currency_converter[8][currency]
    elif vote in range(81, 91):
        return currency_converter[9][currency]
    elif vote in range(91, 101):
        return currency_converter[10][currency]
    elif vote in range(101, 111):
        return currency_converter[11][currency]
    elif vote in range(111, 121):
        return currency_converter[12][currency]
    elif vote in range(121, 131):
        return currency_converter[13][currency]
    elif vote > 131:
        return currency_converter[14][currency]
    else:
        return currency_converter[0][currency]