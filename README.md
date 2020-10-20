# DiscordBotPanelExample

An example of a web panel for a discord bot

## Running in container

If you don't have a discord application. Create it at [Discord Developers](https://discord.com/developers/applications). Make sure to add ``http://127.0.0.1:8000/discord`` to OAuth2 redirects

Go to the projects directory and create ``.env`` file with the following content

```txt
CLIENT_ID=<your client id>
CLIENT_SECRET=<your client secret>
BOT_TOKEN=<your bot token>
```

then run ``docker-compose up``

Invite bot to your server and open ``http://127.0.0.1:8000`` in web browser
