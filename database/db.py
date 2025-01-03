from datetime import datetime
import aiosqlite

name_db = 'photobattle.db'


async def db_start():
    async with aiosqlite.connect(name_db) as db:
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER,
                channel_id INTEGER,
                title TEXT,
                admin_chat INTEGER DEFAULT 0,
                channel_link TEXT DEFAULT '-',
                post_link TEXT DEFAULT '-',
                status INTEGER DEFAULT 0
            )''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS battles_statistic (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER,
                all_battles INTEGER DEFAULT 0,
                count_end INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER,
                count INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER,
                first_name TEXT,
                username TEXT,
                wins INTEGER DEFAULT 0,
                today_voices INTEGER DEFAULT 0,
                all_voices INTEGER DEFAULT 0
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS battle_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER,
                battle_id INTEGER,
                photo TEXT,
                votes INTEGER DEFAULT 0,
                status INTEGER DEFAULT 0,
                number_post INTEGER DEFAULT 0,
                notification INTEGER DEFAULT 0,
                post_id INTEGER DEFAULT 0,
                last_like TEXT DEFAULT '2024-10-20 01:18:32'
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS battle_voices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                battle_id INTEGER,
                tg_id INTEGER
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS battle_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                battle_id INTEGER,
                tg_id INTEGER
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS battle_winners (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                battle_id INTEGER,
                tg_id INTEGER
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS blocked (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                count INTEGER DEFAULT 0)''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS battles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                tg_id INTEGER,
                title TEXT DEFAULT '-',
                post_link TEXT DEFAULT '-',
                channel_link TEXT DEFAULT '-',
                prize TEXT DEFAULT '-',
                post TEXT DEFAULT '-',
                start TEXT DEFAULT '-',
                end TEXT DEFAULT '-',
                participants INTEGER DEFAULT 0,
                min_golos INTEGER DEFAULT 0,
                min_participants_round INTEGER DEFAULT 0,
                round_users INTEGER DEFAULT 0,
                status INTEGER DEFAULT 0,
                end_round TEXT DEFAULT '-',
                count_in_post INTEGER DEFAULT 0,
                post_id INTEGER DEFAULT 0,
                error_battle INTEGER DEFAULT 0,
                error_post INTEGER DEFAULT 0,
                post_text TEXT DEFAULT '-',
                photo_send INTEGER DEFAULT 1,
                current_round INTEGER DEFAULT 0,
                type_battle INTEGER DEFAULT 2)''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS posts_correcting (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                battle_id INTEGER,
                post_id INTEGER)''')
        await db.commit()


async def check_all_battle_photos_where_battle_id(id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE battle_id = ?', (id,))
        rows = await cursor.fetchall()
        # Преобразование списка кортежей в одномерный список
        return rows

async def check_battles_where_status_1_return_battle_info():
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battles WHERE status = 1')
        rows = await cursor.fetchall()
        # Преобразование списка кортежей в одномерный список
        return rows

async def update_last_like(tg_id, last_like, battle_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battle_photos SET last_like = ? WHERE tg_id = ? AND battle_id = ?', (last_like, tg_id, battle_id))
        await db.commit()

async def check_all_battles_photo_where_id(id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE battle_id = ?', (id,))
        rows = await cursor.fetchall()
        # Преобразование списка кортежей в одномерный список
        return rows

async def check_all_battles_where_status_3_return_id():
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT id FROM battles WHERE status = 3')
        rows = await cursor.fetchall()
        # Преобразование списка кортежей в одномерный список
        ids = [row[0] for row in rows]
        return ids

async def check_all_battles_where_all_ran_return_id():
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT id FROM battles WHERE (status > 2) AND title <> "-"')
        rows = await cursor.fetchall()
        # Преобразование списка кортежей в одномерный список
        ids = [row[0] for row in rows]
        return ids

async def update_battlepost_text(post_text, id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET post_text = ? WHERE id = ?', (post_text, id))
        await db.commit()
    
async def update_error_post(error_number, id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET error_post = ? WHERE id = ?', (error_number, id))
        await db.commit()

async def update_error_number(error_number, id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET error_battle = ? WHERE id = ?', (error_number, id))
        await db.commit()
async def update_channel_link_where_id(channel_link, id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE channels SET channel_link = ? WHERE id = ?', (channel_link, id))
        await db.commit()

async def update_channels_post_link_where_id(post_link, id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE channels SET post_link = ? WHERE id = ?', (post_link, id))
        await db.commit()



async def update_post_id(post_id, id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET post_id = ? WHERE id = ?', (post_id, id))
        await db.commit()

async def update_photo_send_battle(photo_send, id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET photo_send = ? WHERE id = ?', (photo_send, id))
        await db.commit()

async def update_blocked_count(count):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE blocked SET count = ? WHERE id = ?', (count, 1))
        await db.commit()

async def check_len_users():
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM users')
        result = await cursor.fetchone()
        return result[0]
async def check_blocked_count_where_id_1():
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT count FROM blocked WHERE id = ?', (1,))
        result = await cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

async def update_admin_count_minus_1(tg_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE admins SET count = count - 1 WHERE tg_id = ?', (tg_id, ))
        await db.commit()

async def check_admins_count(tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT count FROM admins WHERE tg_id = ?', (tg_id,))
        result = await cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

async def delete_all_battle_voices_where_battle_id(battle_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('DELETE FROM battle_voices WHERE battle_id = ?', (battle_id,))
        await db.commit()

async def add_battles_statistic(tg_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('INSERT INTO battles_statistic (tg_id) VALUES (?)', (tg_id,))
        await db.commit()

async def get_all_users_tg_id():
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT tg_id FROM users')
        return await cursor.fetchall()

async def add_battle_photos_votes_where_tg_id(tg_id, votes):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battle_photos SET votes = votes + ? WHERE tg_id = ?', (votes, tg_id, ))
        await db.commit()

async def add_admins_count(tg, count):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE admins SET count = ? WHERE tg_id = ?', (count, tg,))
        await db.commit()

async def delete_admin(tg_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('DELETE FROM admins WHERE tg_id = ?', (tg_id, ))
        await db.commit()

async def add_admin(tg_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('INSERT INTO admins (tg_id) VALUES (?)', (tg_id,))
        await db.commit()

async def check_all_admins():
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM admins')
        return await cursor.fetchall()

async def check_admin_exist_return_bool(tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM admins WHERE tg_id = ?', (tg_id,))
        if await cursor.fetchone():
            return True
        else:
            return False

async def update_end_battle_statistic(tg_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles_statistic SET count_end = count_end + 1 WHERE tg_id = ?', (tg_id, ))
        await db.commit()

async def update_battle_statistic_plus_1(tg_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles_statistic SET all_battles = all_battles + 1 WHERE tg_id = ?', (tg_id,))
        await db.commit()

async def check_battles_where_tg_id_return_count(tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM battles WHERE tg_id = ?', (tg_id,))
        return await cursor.fetchone()

async def check_battle_statistic_by_tg_id(tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battles_statistic WHERE tg_id = ?', (tg_id, ))
        return await cursor.fetchone()

async def check_count_battle_winners_where_tg_id(tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM battle_winners WHERE tg_id = ?', (tg_id,))
        return await cursor.fetchone()

async def check_battle_winner_exist_return_bool(battle_id, tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_winners WHERE battle_id = ? AND tg_id = ?', (battle_id, tg_id))
        if await cursor.fetchone():
            return True
        else:
            return False

async def add_new_battle_winner(battle_id, tg_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('INSERT INTO battle_winners (battle_id, tg_id) VALUES (?, ?)', (battle_id, tg_id))
        await db.commit()


async def check_battle_block_battle_id_tg_id_exist_return_bool(battle_id, tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_blocks WHERE battle_id = ? AND tg_id = ?', (battle_id, tg_id))
        if await cursor.fetchone():
            return True
        else:
            return False

async def add_new_user_to_battle_blocks(battle_id,tg_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('INSERT INTO battle_blocks (battle_id,tg_id) VALUES (?, ?)', (battle_id,tg_id))
        await db.commit()

async def check_info_users_by_tg_id(tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM users WHERE tg_id = ?', (tg_id,))
        return await cursor.fetchone()

async def update_users_today_voices_and_all_voices(tg_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE users SET today_voices = today_voices + 1, all_voices = all_voices + 1 WHERE tg_id = ?', (tg_id, ))
        await db.commit()


async def check_battle_voices_tg_id_exist_return_bool(tg_id, battle_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_voices WHERE tg_id = ? AND battle_id = ?', (tg_id, battle_id))
        if await cursor.fetchone():
            return True
        else:
            return False


async def add_one_voice_to_battle_photos_by_id(id: int):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battle_photos SET votes = votes + 1 WHERE id = ?', (id,))
        await db.commit()


async def add_new_battle_voices(battle_id, tg_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('INSERT INTO battle_voices (battle_id, tg_id) VALUES (?, ?)', (battle_id, tg_id))
        await db.commit()


async def add_user_if_not_exist(tg_id, first_name, username):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM users WHERE tg_id = ?', (tg_id,))
        user = await cursor.fetchone()
        if not user:
            await db.execute('INSERT INTO users (tg_id, first_name, username) VALUES (?, ?, ?)', (tg_id, first_name, username))
            await db.commit()

async def delete_battle_by_id(id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('DELETE FROM battles WHERE id = ?', (id,))
        await db.commit()

async def check_battle_photos_where_id1(id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE id = ?', (id,))
        return await cursor.fetchone()
async def check_battle_photos_where_id(id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE battle_id = ?', (id,))
        return await cursor.fetchone()

async def check_users_from_battle(id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE battle_id = ?', (id,))
        return await cursor.fetchall()

async def update_photo_approved_time(id):
    current_time = datetime.now().strftime("%H:%M")  # Форматируем текущее время как часы:минуты
    async with aiosqlite.connect(name_db) as db:
        await db.execute(
            'UPDATE battle_photos SET photo_approved_time = ? WHERE battle_id = ?',
            (current_time, id)
        )
        await db.commit()
        
async def update_battles_descr_round_users_min_golos_end_round_by_id(id):
    descr = '-'
    round_users = 0
    min_golos = 0
    end_round = '-'
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET post = ?, round_users = ?, min_golos = ?, end_round = ? WHERE id = ?', (descr, round_users, min_golos, end_round, id))
        await db.commit()

async def update_battle_photos_votes_and_number_post(id, votes, number_post):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battle_photos SET votes = ?, number_post = ? WHERE id = ?', (votes, number_post, id))
        await db.commit()



async def delete_user_from_battle_photos(id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('DELETE FROM battle_photos WHERE id = ?', (id, ))
        await db.commit()

async def check_battle_photo_info_by_id(id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE id = ?', (id,))
        return await cursor.fetchone()

async def check_battle_photos_by_battle_id_and_number_post(battle_id, number_post):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE battle_id = ? AND number_post = ?', (battle_id, number_post))
        return await cursor.fetchall()


async def update_number_post_in_battle_photos_by_id(id,number_post):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battle_photos SET number_post = ? WHERE id = ?', (number_post, id))
        await db.commit()


async def update_count_in_posts(battle_id,count_in_post):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET count_in_post = ? WHERE id = ?', (count_in_post, battle_id))
        await db.commit()

async def increment_count_in_posts(battle_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET count_in_post = count_in_post + 1 WHERE id = ?', (battle_id,))
        await db.commit()

async def check_all_battle_photos_where_status_1_and_battle_id(battle_id):
    async with aiosqlite.connect(name_db) as db:
        # cursor = await db.execute('SELECT * FROM battle_photos WHERE status = 1 AND battle_id = ? AND number_post <> 0', (battle_id, ))
        cursor = await db.execute('SELECT * FROM battle_photos WHERE (status = 1 AND battle_id = ? AND number_post <> 0)', (battle_id, ))
        return await cursor.fetchall()

async def before_check_all_battle_photos_where_status_1_and_battle_id(battle_id):
    async with aiosqlite.connect(name_db) as db:
        # cursor = await db.execute('SELECT * FROM battle_photos WHERE status = 1 AND battle_id = ? AND number_post <> 0', (battle_id, ))
        cursor = await db.execute('SELECT * FROM battle_photos WHERE (status = 1 AND battle_id = ?)', (battle_id, ))
        return await cursor.fetchall()

async def check_all_battle_photos_where_number_post_0_and_battle_id(battle_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE (number_post = 0 AND battle_id = ? AND status = 1)', (battle_id, ))
        return await cursor.fetchall()


async def check_all_battle_photos_where_status_1_and_battle_id_bigger_than(battle_id, start_id):
    async with aiosqlite.connect(name_db) as db:
        # Добавляем условие на id и сортировку
        cursor = await db.execute('''
            SELECT * FROM battle_photos 
            WHERE status = 1 AND battle_id = ? AND id >= ?
            ORDER BY id ASC
        ''', (battle_id, start_id))
        return await cursor.fetchall()

async def update_min_golos_battle(battle_id, min_golos):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET min_golos = ? WHERE id = ?', (min_golos, battle_id))
        await db.commit()



async def update_end_round_battle(battle_id,end_round):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET end_round = ? WHERE id = ?', (end_round, battle_id))
        await db.commit()

async def update_round_users_battle(battle_id, round_users):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET round_users = ? WHERE id = ?', (round_users, battle_id))
        await db.commit()

async def check_count_battle_photos_where_battle_id_and_status_1(battle_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT COUNT(*) FROM battle_photos WHERE battle_id = ? AND status = 1', (battle_id,))
        return (await cursor.fetchone())[0]

async def battle_photos_status_by_id(id, status):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battle_photos SET status = ? WHERE id = ?', (status, id))
        await db.commit()

async def check_battle_where_battle_id_and_tg_id_exist_and_status_1_return_bool(battle_id,tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE battle_id = ? AND tg_id = ?', (battle_id, tg_id))
        return bool(await cursor.fetchone())
async def check_battle_where_battle_id_and_tg_id_exist_and_status_0_return_bool(battle_id,tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE battle_id = ? AND tg_id = ? AND status = 0', (battle_id, tg_id))
        return bool(await cursor.fetchone())

async def add_battle_photo(tg_id, battle_id, photo):
    async with aiosqlite.connect(name_db) as db:
        async with db.execute('INSERT INTO battle_photos (tg_id, battle_id, photo) VALUES (?, ?, ?)', (tg_id, battle_id, photo)) as cursor:
            await db.commit()
            return cursor.lastrowid


async def check_all_battles_where_status_1():
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battles WHERE status = 1  ORDER BY id DESC')
        return await cursor.fetchall()

async def check_battles_where_status_1_and_tg_id(tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute("""
            SELECT * FROM battles 
            WHERE tg_id = ? AND (status = 0 OR status = 1 OR status = 2 OR status = 3 OR status = 4) 
            ORDER BY id DESC
        """, (tg_id,))
        return await cursor.fetchall()


async def update_participants_battle(battle_id, participants):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET participants = ? WHERE id = ?', (participants, battle_id))
        await db.commit()

async def update_battle_end(battle_id,end):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET end = ? WHERE id = ?', (end, battle_id))
        await db.commit()

async def update_battle_start(battle_id, start):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET start = ? WHERE id = ?', (start, battle_id))
        await db.commit()

async def update_battle_description(battle_id,description):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET post = ? WHERE id = ?', (description, battle_id))
        await db.commit()

async def update_battle_prize(battle_id, prize):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET prize = ? WHERE id = ?', (prize, battle_id))
        await db.commit()

async def update_battle_post_link_by_battle_id(battle_id,link):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET post_link = ? WHERE id = ?', (link, battle_id))
        await db.commit()

async def update_status_battle(battle_id,status):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET status = ? WHERE id = ?', (status, battle_id))
        await db.commit()

async def update_battle_channel_link_by_battle_id(battle_id, link):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET channel_link = ? WHERE id = ?', (link, battle_id))
        await db.commit()

async def update_battle_name_by_battle_id(battle_id,name):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET title = ? WHERE id = ?', (name, battle_id))
        await db.commit()

async def update_link_by_battle_id(battle_id,battle_link):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET channel_link = ? WHERE id = ?', (battle_link, battle_id))
        await db.commit()

async def check_battle_info(battle_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battles WHERE id = ?', (battle_id,))
        rows = await cursor.fetchone()
        await cursor.close()
        return rows



async def create_new_battle_return_id(channel_id, tg_id):
    async with aiosqlite.connect(name_db) as db:
        async with db.execute('INSERT INTO battles (channel_id, tg_id) VALUES (?, ?)', (channel_id, tg_id)) as cursor:
            await db.commit()
            return cursor.lastrowid



async def uopdate_admin_chat_by_chat_id(chat_id, admin_chat):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE channels SET admin_chat = ? WHERE id = ?', (admin_chat, chat_id))
        await db.commit()

async def delete_channel_by_id(id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('DELETE FROM channels WHERE id = ?', (id,))
        await db.commit()
        
async def check_all_channels():
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM channels')
        rows = await cursor.fetchall()
        return rows
    
async def check_all_battles():
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battles WHERE status = 1')
        return await cursor.fetchall()
    
async def check_channel_info_by_id(id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM channels WHERE id = ?', (id, ))
        rows = await cursor.fetchone()
        await cursor.close()
        return rows

async def check_channel_info_by_link(url):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM channels WHERE channel_link = ?', (url, ))
        rows = await cursor.fetchone()
        await cursor.close()
        return rows
    
async def check_channel_duplicate(channel_id):  # Исправлено название функции для ясности
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM channels WHERE id = ?', (channel_id,))  # Используем channel_id
        row = await cursor.fetchone()  # Исправлено на `row`, так как возвращается одна строка
        await cursor.close()
        return row
    
async def add_new_cahnnel_by_chan_id(tg_id, channel_id, title):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute(f"SELECT channel_id FROM channels WHERE channel_id={channel_id}")
        row = await cursor.fetchone()
        await cursor.close()
        if row is not None:

            return False
        else:
            await db.execute('INSERT INTO channels (tg_id, channel_id, title) VALUES (?, ?, ?)', (tg_id, channel_id, title))
            await db.commit()
            return True

async def checkk_all_channels_where_tg_id(tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM channels WHERE tg_id = ?', (tg_id,))
        rows = await cursor.fetchall()
        await cursor.close()
        return rows

async def all_photo_by_battle(battle_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE (battle_id = ? and status = 1 AND number_post <> 0)', (battle_id, ))
        return await cursor.fetchall()

async def update_id_post(message_id_post, battle_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('INSERT INTO posts_correcting (post_id, battle_id) VALUES (?, ?)', (message_id_post, battle_id))
        await db.commit()

async def get_all_posts_by_battle(battle_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM posts_correcting WHERE battle_id = ?', (battle_id, ))
        return await cursor.fetchall()

async def updatePostFieldBattles(post, battle_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET post = ? WHERE id = ?', (post, battle_id))
        await db.commit()

async def update_number_round(current_round, battle_id):
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET current_round = ? WHERE id = ?', (current_round, battle_id))
        await db.commit()

async def get_photos_where_status_1(battle_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE (battle_id = ? AND status = 1)', (battle_id, ))
        return await cursor.fetchall()

async def check_battle_where_battle_id_and_tg_id_exist_and_status_1(battle_id, tg_id):
    async with aiosqlite.connect(name_db) as db:
        cursor = await db.execute('SELECT * FROM battle_photos WHERE battle_id = ? AND tg_id = ? AND status = 1', (battle_id, tg_id))
        return await cursor.fetchone()

async def update_type_battle(battle_id, type_battle) -> None:
    ''' Обновляет значение типа батла в таблице по айди '''
    async with aiosqlite.connect(name_db) as db:
        await db.execute('UPDATE battles SET type_battle = ? WHERE id = ?', (type_battle, battle_id))
        await db.commit()
