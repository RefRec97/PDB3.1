import interactions
import logging
from utils.authorisation import Authorization
from utils.db import DB
from utils.notify import Notify

class ManageNotify(interactions.Extension):
    def __init__(self, client, args):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._client: interactions.Client = client
        self._auth:Authorization = args[0]
        self._db:DB = args[1]


    @interactions.extension_command(
        name="add_update_channel",
        description="Fügt den aktuellen Channel zum Nachrichtenverteiler hinzu"
    )
    async def add_notify_channel(self, ctx: interactions.CommandContext):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        existing = self._db.getNotify(str(ctx.channel.id),Notify.CHANNEL)
        if existing and existing[1] == Notify.CHANNEL:
            await ctx.send(f"{ctx.channel.mention} bereits registriert", ephemeral=True)
            return
        
        self._db.setNotify(str(ctx.channel.id),Notify.CHANNEL)

        await ctx.send(f"{ctx.channel.mention} hinzugefügt")
    
    @interactions.extension_command(
        name="notify",
        description="Fügt dich zum Nachrichtenvertieler hinzu",
        options =[
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="type",
                description="Kategorie",
                required=True,
                choices=[
                    interactions.Choice(name="Sensor Phalanx reichweite", value=Notify.SENSOR_PHALANX)
                ]
            ),
            interactions.Option(
                name="username",
                description="Pr0game Username",
                type=interactions.OptionType.STRING,
                required=True
            )
        ]
    )
    async def add_notify(self, ctx: interactions.CommandContext, type:str, username:str=None):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        existing = self._db.getNotify(str(ctx.user.id),type)
        if existing and existing[0][1] == type:
            await ctx.send(f"{ctx.user.mention} Bereits registriert", ephemeral=True)
            return
        
        if type == Notify.SENSOR_PHALANX:
            playerData = self._db.getPlayerDataByName(username)
            if not playerData:
                await ctx.send(f"Spieler nicht gefunden: {username}", ephemeral=True)
                return
        
        self._db.setNotify(str(ctx.user.id), type, str(ctx.guild.id), playerData[1])

        await ctx.send(f"Im Verteiler aufgenommen {ctx.user.mention}")
    
    @interactions.extension_command(
        name="del_notify",
        description="Löscht dich vom Nachrichtenvertieler",
        options =[
            interactions.Option(
                type=interactions.OptionType.STRING,
                name="type",
                description="Kategorie",
                required=True,
                choices=[
                    interactions.Choice(name="Expo cap increase", value=Notify.EXPO_SIZE),
                    interactions.Choice(name="Sensor Phalanx reichweite", value=Notify.SENSOR_PHALANX)
                ]
            ),
            interactions.Option(
                name="username",
                description="Pr0game Username",
                type=interactions.OptionType.STRING,
                required=True
            )
        ]
    )
    async def del_notify(self, ctx: interactions.CommandContext, type:str, username:str=None):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        existing = self._db.getNotify(str(ctx.user.id),type)
        if existing and existing[0][1] == type:
            self._db.delNotify(str(ctx.user.id),type)
            await ctx.send(f"Gelöscht", ephemeral=True)
            return


        await ctx.send(f"Nicht gefunden", ephemeral=True)

def setup(client, args):
    ManageNotify(client, args)
    