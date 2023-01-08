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
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        existing = self._db.getNotify(str(ctx.channel.id),Notify.CHANNEL)
        if existing and existing[1] == Notify.CHANNEL:
            await ctx.send(f"{ctx.channel.mention} bereits registriert")
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
                    interactions.Choice(name="Expo cap increase", value=Notify.EXPO_SIZE),
                    interactions.Choice(name="Sensor Phalanx reichweite", value=Notify.SENSOR_PHALANX)
                ]
            ),
        ]
    )
    async def add_notify(self, ctx: interactions.CommandContext, type:str):
        self._logger.debug("Command called: %s from %s",ctx.command.name, ctx.user.username)

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        existing = self._db.getNotify(str(ctx.user.id),type)
        if existing and existing[0][1] == type:
            await ctx.send(f"{ctx.user.mention} Bereits registriert", ephemeral=True)
            return
        
        self._db.setNotify(str(ctx.user.id), type, str(ctx.guild.id))

        await ctx.send(f"Im Verteiler aufgenommen {ctx.user.mention}")
    
def setup(client, args):
    ManageNotify(client, args)
    