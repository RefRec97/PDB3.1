import interactions
import logging
from utils.authorisation import Authorization
from utils.db import DB

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
        
        if self._db.getNotifyChannel(str(ctx.channel.id)):
            await ctx.send(f"{ctx.channel.mention} bereits registriert")
            return
        
        self._db.setNotifyChannel(str(ctx.channel.id))

        await ctx.send(f"{ctx.channel.mention} hinzugefügt")
    
def setup(client, args):
    ManageNotify(client, args)
    