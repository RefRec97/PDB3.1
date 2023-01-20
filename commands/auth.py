import interactions
import logging
from utils.authorisation import Authorization
import config

class Auth(interactions.Extension):
    def __init__(self, client, args):
        self._logger = logging.getLogger(__name__)
        self._logger.debug("Initialization")

        self._client: interactions.Client = client
        self._auth:Authorization = args

        #init Owner
        self._auth.add(config.ownerId, self._auth.OWNER)
        
    
    #Authorization Admin
    @interactions.extension_command(
        name="admin",
        description="Authorisiert einen Nutzer als Admin",
        options = [
            interactions.Option(
                name="user",
                description="Discord Nutzer",
                type=interactions.OptionType.USER,
                required=True
            ),
        ],
        scope=config.devDiscordId
    )
    async def admin(self, ctx: interactions.CommandContext, user:interactions.User):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Target: %s", str(user.username))

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        self._auth.add(user.id, self._auth.ADMIN)
        await ctx.send("Admin authorisiert: " + user.mention)


    #Authorization with command
    @interactions.extension_command(
        name="auth",
        description="Authorisiert einen Nutzer für den Bot",
        options = [
            interactions.Option(
                name="user",
                description="Discord Nutzer",
                type=interactions.OptionType.USER,
                required=True
            ),
        ],
        scope=config.devDiscordId
    )
    async def auth(self, ctx: interactions.CommandContext, user:interactions.User):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Target: %s", str(user.username))

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return
        
        self._auth.add(user.id, self._auth.USER)
        await ctx.send("User authorisiert: " + user.mention)

    #Authorization with context menue
    @interactions.extension_command(
        type=interactions.ApplicationCommandType.USER,
        name="Auth",
        description="Authorisiert diesen Nutzer für den Bot"
    )
    async def authContext(self, ctx: interactions.CommandContext):
        self._logger.info(f"{ctx.user.username}, {ctx.command.name}")
        self._logger.debug("Target: %s", str(ctx.target.user.username))

        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        self._auth.add(ctx.target.user.id, self._auth.USER)
        await ctx.send("User authorisiert: " + ctx.target.user.mention)
        
    

def setup(client, args):
    Auth(client, args)