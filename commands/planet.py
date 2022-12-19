import interactions
from utils.authorisation import Authorization
from utils.db import DB

class Planet(interactions.Extension):
    def __init__(self, client, args):
        self._client: interactions.Client = client
        self._auth:Authorization = args[0]
        self._db:DB = args[1]
    
    
    @interactions.extension_command(
        name="planet",
        description="Speichert ein Planet",
        options = [
            interactions.Option(
                name="username",
                description="Pr0game Username",
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.Option(
                name="galaxy",
                description="Galaxy",
                type=interactions.OptionType.INTEGER,
                required=True
            ),
            interactions.Option(
                name="system",
                description="System",
                type=interactions.OptionType.INTEGER,
                required=True
            ),
            interactions.Option(
                name="position",
                description="Position",
                type=interactions.OptionType.INTEGER,
                required=True
            ),
        ],
    )
    async def planet(self, ctx: interactions.CommandContext, username:str, galaxy:int, system:int, position: int):
        if not self._auth.check(ctx.user.id, ctx.command.name):
            await ctx.send(embeds=self._auth.NOT_AUTHORIZED_EMBED, ephemeral=True)
            return

        #get userId
        userId = self._db.getuserId(username)[1]

        #save planet
        self._db.updatePlanet(userId, galaxy, system, position)

        planetEmbed = interactions.Embed(
            title="Gespeichert",
            description= f"{galaxy}:{system}:{position}",
        )

        await ctx.send(embeds=planetEmbed)

    
    


def setup(client, args):
    Planet(client, args)