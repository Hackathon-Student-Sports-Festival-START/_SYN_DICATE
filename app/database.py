# База данных
import asyncpg


class Database:
    def __init__(self, db_name, db_user, db_user_pass, db_host='localhost', db_port=5432):
        self.db_name = db_name
        self.db_user = db_user
        self.db_user_pass = db_user_pass
        self.db_host = db_host
        self.db_port = db_port
        self.conn = None






    async def connect(self):
        self.conn = await asyncpg.connect(
            database=self.db_name,
            user=self.db_user,
            password=self.db_user_pass,
            host=self.db_host,
            port=self.db_port
        )
    async def create_tables(self):
        await self.conn.execute("""CREATE TABLE IF NOT EXISTS users(
                                 id SERIAL PRIMARY KEY,
                                 email TEXT UNIQUE NOT NULL,
                                 password TEXT NOT NULL,
                                 phone TEXT  DEFAULT NULL,
                                 name TEXT  DEFAULT NULL,
                                 last_name TEXT DEFAULT NULL,
                                 university TEXT DEFAULT NULL);""")


    async def disconnect(self):
        if self.conn:
            await self.conn.close()

    async def add_new_user(self, email, password, first_name, last_name, university, phone):
        await self.conn.execute("""
            INSERT INTO users (email, password, phone, name, last_name, university)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, email, password, phone, first_name, last_name, university)

    async def get_user_by_email(self, email):
        user = await self.conn.fetchrow("""
            SELECT email, password, name, last_name, university, phone
            FROM users WHERE email = $1
        """, email)
        return user

    async def update_user_profile(self, current_email, name=None, last_name=None, university=None, email=None,
                                  phone=None):
        await self.conn.execute("""
            UPDATE users
            SET name = COALESCE($1, name),
                last_name = COALESCE($2, last_name),
                university = COALESCE($3, university),
                email = COALESCE($4, email),
                phone = COALESCE($5, phone)
            WHERE email = $6
        """, name, last_name, university, email, phone, current_email)
