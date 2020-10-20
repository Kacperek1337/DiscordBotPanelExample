import os

import discord
import psycopg2

TOKEN = os.getenv('BOT_TOKEN')


class Bot(discord.Client):

    conn = psycopg2.connect("""
                            host=127.0.0.1
                            port=5432
                            dbname=bot_panel
                            user=postgres
                            password=password
                            """)
    query = """
    SELECT message
    FROM settings
    WHERE user_id=%s
    """

    async def on_message(self, message):
        if message.author == self.user:
            return

        with self.conn.cursor() as cursor:
            cursor.execute(
                self.query,
                (
                    message.author.id,
                )
            )
            result = cursor.fetchone()
            if message.content == '!msg':
                if not result:
                    result = ['Default message. Change it in the panel']
                await message.channel.send(*result)

    async def on_ready(self):
        print(self.user, 'connected to discord!')

    def __init__(self, *args, **kwargs):
        self.cursor = self.conn.cursor()
        super().__init__(*args, **kwargs)


if __name__ == '__main__':
    Bot().run(TOKEN)
