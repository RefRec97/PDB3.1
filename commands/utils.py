import interactions
import logging
from utils.authorisation import Authorization
from utils.update import Update
from utils.notify import Notify
from utils.db import DB
import config

class Bot(interactions.Extension):
    def __init__(self, client, args):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._client: interactions.Client = client
        self._auth:Authorization = args[0]
        self._update:Update = args[1]
        self._notify:Notify = args[2]
        self._db:DB = args[3]

    @interactions.extension_command(
        name="shutdown",
        description="Schaltet den Bot aus",
        scope=config.devDiscordId
    )
    async def shutdown(self, ctx: interactions.CommandContext):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        self._update.stop()
        await ctx.send("Schlafenszeit zZz")
        await self._notify.notify(Notify.CHANNEL, "Ich bin Offline (planmäßig)")
        await self._client._stop()

    @interactions.extension_command(
        name="link",
        description="Verlinken von Discord mit Pr0game",
        options = [
            interactions.Option(
                name="playername",
                description="Pr0game Username",
                type=interactions.OptionType.STRING,
                required=True
            ),
        ],
    )
    async def link(self, ctx: interactions.CommandContext, playername:str):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        playerData = self._db.getPlayerDataByName(playername)
        if not playerData:
            await ctx.send(f"Spieler nicht gefunden: {playername}", ephemeral=True)
            return

        try:
            self._db.setLink(playerData[1], str(ctx.user.id), ctx.user.username)
        except:
            await ctx.send(f"Fehler aufgetreten")
            return

        await ctx.send("Verlinkung Gespeichert")

    @interactions.extension_command(
        name="update",
        description="Startet Aktualisierung der stats",
        scope=config.devDiscordId
    )
    @interactions.autodefer(delay=60)
    async def update(self, ctx: interactions.CommandContext):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        await ctx.send("Starte Update")
        await self._update.force()
        await ctx.message.edit("Update Complete")
    
    @interactions.extension_command(
        name="status",
        description="Status des Bots"
    )
    async def status(self, ctx: interactions.CommandContext):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        
        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        await ctx.send("Online auf {} Server".format(len(self._client.guilds)))
    
    @interactions.extension_command(
        name="features",
        description="Ungeordnete Liste der geplanten Updates"
    )
    async def features(self, ctx: interactions.CommandContext):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)
        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        featureLIst = """
        Geplante Features (ungeordnet):
            - Inacitve erweitern mit optinalen Parameter
                - min/max Inactive Datenpunkte
            - Der letzten X tage. /stats [username] [optional Zeitfesnster]
            - Prozentuales Punktewachstum eines oder mehrere Spieler (vergleichbar)
                - chart mit Trendlinine
            - Playerhistory. Zusätzlich speichern Wenn sich name oder Allianz ändert
              (aktuell wird überschrieben)
            - Notify
                - Warnung bei Phalax +1 scannbar
            - Mond Map
            - Allianz Plazierung pro update ausrechnen und speichern
            - DB statistik (anzahl planeten,statseinträge,...)
                (weil ich daten Geil finde!)"""

        await ctx.send(featureLIst)
    
def setup(client, args):
    Bot(client, args)
    
