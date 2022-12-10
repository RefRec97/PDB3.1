import interactions
from utils.authorisation import Authorization
from utils.db import DB

class Stats(interactions.Extension):
    def __init__(self, client, args):
        self._client: interactions.Client = client
        self._auth:Authorization = args[0]
        self._db:DB = args[1]
    
    @interactions.extension_command(
        name="stats",
        description="Stats des Spielers",
        options = [
            interactions.Option(
                name="username",
                description="Pr0game Username",
                type=interactions.OptionType.STRING,
                required=False
            ),
        ],
    )
    async def stats(self, ctx: interactions.CommandContext, username:str = None):
        if not self._auth.check(ctx.user.id, ctx.command.name):
            return

        if not username:
            username = ctx.user.username
        
        try:
            statsEmbed,statsComponent = self._getStatsContent(username)
        except:
            await ctx.send(f"{username} nicht gefunden")
            return

        await ctx.send(embeds=statsEmbed, components=statsComponent)

    @interactions.extension_command(
        name="alliance",
        description="Stats einer Alliance",
        options = [
            interactions.Option(
                name="alliancename",
                description="Alliance Name",
                type=interactions.OptionType.STRING,
                required=True
            ),
        ],
    )
    async def alliance(self, ctx: interactions.CommandContext, alliancename:str):
        if not self._auth.check(ctx.user.id, ctx.command.name):
            return
        
        try:
            allianceEmbed, allianzComponents = self._getAllianzContent(alliancename)
        except:
            await ctx.send(f"{alliancename} nicht gefunden")
            return

        await ctx.send(embeds=allianceEmbed, components=allianzComponents)

    #Button: Allianz
    @interactions.extension_component("btnShowAllianz")
    async def button_response(self, ctx:interactions.ComponentContext):        
        if not self._auth.check(ctx.user.id, "alliance"):
            return
        
        allianzName = ctx.message.embeds[0].description

        try:
            allianceEmbed, allianzComponents = self._getAllianzContent(allianzName)
        except:
            await ctx.send(f"{allianzName} nicht gefunden")
            return
        
        await ctx.send(embeds=allianceEmbed, components = allianzComponents)

    #Select: Player
    @interactions.extension_component("SoPlayerSelect")
    async def selectionResponse(self, ctx:interactions.ComponentContext, userNames:list):        
        if not self._auth.check(ctx.user.id, "stats"): #button command = stats command
            return
        
        try:
            statsEmbed,statsComponent = self._getStatsContent(userNames[0])
        except:
            await ctx.send(f"{userNames[0]} nicht gefunden")
            return
        
        await ctx.send(embeds=statsEmbed, components= statsComponent)

    def _getStatsContent(self, playerName:str):
        data = self._db.getUserData(playerName)

        if not data:
            return False

        statsEmbed = interactions.Embed(
            title=f"{data[0]}",
            description= f"{data[1]}",
            fields= [
                interactions.EmbedField(
                    inline=False,
                    name="Gesamt",
                    value=f"`{data[4]:4} - {self._formatNumber(data[5])}`"
                ),
                interactions.EmbedField(
                    inline=False,
                    name="Gebäude",
                    value=f"`{data[8]:4} - {self._formatNumber(data[9])}`"
                ),
                interactions.EmbedField(
                    inline=False,
                    name="Forschung",
                    value=f"`{data[6]:4} - {self._formatNumber(data[7])}`"
                ),
                interactions.EmbedField(
                    inline=False,
                    name="Flotte",
                    value=f"`{data[12]:4} - {self._formatNumber(data[13])}`"
                ),
                interactions.EmbedField(
                    inline=False,
                    name="Verteidigung",
                    value=f"`{data[10]:4} - {self._formatNumber(data[11])}`"
                )
            ],
            timestamp=data[22]
        )

        statsBtn =  interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="Allianz",
            custom_id="btnShowAllianz")

        return (statsEmbed, statsBtn)

    def _formatNumber(self, number):
        return f"{number:,}".replace(",",".")
    
    def _getAllianzContent(self, allianzName:str):
        
        data = self._db.getAllianzData(allianzName)

        if not data:
            return

        #Create Main content
        #Create max 5 Embed fields (if Possible)
        ebedFields = []
        for player in data[:5]:
            ebedFields.append(interactions.EmbedField(
                inline=False,
                name=player[1],
                value=f"`{player[2]} - {self._formatNumber(player[3])}`"))

        allianceEmbed = interactions.Embed(
            title=f"{allianzName}",
            description= f"Anzahl Mitglieder: {len(data)}\nTop Spieler:",
            fields=ebedFields)

        selectOptions = []
        for player in data[:25]: #max SelectionOptions possible (=25)
            selectOptions.append(interactions.SelectOption(
                label=str(player[1]),
                value=player[1]))
        
        allianceComponent = interactions.SelectMenu(
            custom_id="SoPlayerSelect",
            options = selectOptions)

        return (allianceEmbed,allianceComponent)


def setup(client, args):
    Stats(client, args)