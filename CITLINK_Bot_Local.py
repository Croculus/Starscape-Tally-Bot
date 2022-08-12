import json, Kill_Calculator, nextcord, datetime, pytz, psycopg2
from nextcord.ext import commands, tasks
from nextcord.ui import View, Button

#NOTE this program requires a SQL database to work functionally, I used postgres

with open("Ships.json") as json_file:
    ships = json.load(json_file)

token = '' #put the token of your discord bot here

reset_time = [datetime.time(0, 0, 0, 0, tzinfo=pytz.UTC)] #default to 12 AM UTC
ID_dict = {}
kills = []
pending = []

host = ''
db = ''
user=''
password = ''


async def fetch_pending(string):
    async def msgToEmbed(id):

            async def verified(interaction):
                kills.append(interaction.message.content)
                button1.disabled = True
                button2.disabled = True

                conn = None
                try:
                    conn = psycopg2.connect(host=host, database=db, user=user, password=password)
                    cur = conn.cursor()
                    cmd = "DELETE FROM pending WHERE message_id = {}".format(interaction.message.embeds[0].footer.text) #its been grabbing the message id of the button, we have to get the message id in the link url
                    cur.execute(cmd)
                    conn.commit()
                    cur.close()
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                    await interaction.response.edit_message(content="Error connecting to database", view=view)
                except:
                    await interaction.response.edit_message(content="Something went wrong", view=view)

                else: 
                    await interaction.response.edit_message(content = 'Verified by '+ interaction.user.name, view=view)
                finally:
                    if conn is not None:
                        conn.close()
                
            
            async def reject(interaction):
                button1.disabled = True
                button2.disabled = True 

                conn = None
                try:
                    conn = psycopg2.connect(host=host, database=db, user=user, password=password)
                    cur = conn.cursor()
                    cmd = "DELETE FROM pending WHERE message_id = {}".format(interaction.message.embeds[0].footer.text) #its been grabbing the message id of the button, we have to get the message id in the link url
                    cur.execute(cmd)
                    conn.commit()
                    cur.close()
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                    await interaction.response.edit_message(content="Error connecting to database", view=view)
                except:
                    await interaction.response.edit_message(content="Something went wrong", view=view)

                else: 
                    await interaction.response.edit_message(content = 'Rejected by '+ interaction.user.name, view=view)
                finally:
                    if conn is not None:
                        conn.close()

            msg = await kill_channel.fetch_message(id)
            embedVar = nextcord.Embed(title = "Verify this message", description = msg.content, url = msg.jump_url)
            embedVar.set_author(name = msg.author.name, icon_url = msg.author.avatar.url)
            embedVar.set_footer(text=str(msg.id)) # have to do this so the DB can find the correct row to delete
            button1.callback = verified
            button2.callback = reject
            await ver_channel.send(embed=embedVar, view=view)

    async def pending():
        #trying to create pending embeds on launch

        conn = None
        try:
            conn = psycopg2.connect(host=host, database=db, user=user, password=password)
            cur = conn.cursor()
            cur.execute("SELECT message_id FROM pending")
            row = cur.fetchone()
            
            if row is not None:
                msg = "**{}**".format(string)
                await ver_channel.send(msg)
            while row is not None:
                try:
                    await msgToEmbed(row[0])
                except:
                    await ver_channel.send("Error fetching kills from database")
                row = cur.fetchone()#fetch message id, create embed from message info
            cur.close()
            
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
    await pending()
    
async def update(json, ctx, string):
    conn = None
    try:
        conn = psycopg2.connect(host=host, database=db, user=user, password=password)
        cur = conn.cursor()
        cmd = """UPDATE config 
        SET faction_map = '{}'""".format(json)
        cur.execute(cmd)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        if ctx is not None:
            await ctx.send(content="Error connecting to database")
        print(error)
    except:
        if ctx is not None:
            await ctx.send(content="Something went wrong")
    finally:
        if ctx is not None:
            await ctx.send(content=string)
        if conn is not None:
            conn.close()


def botconfig():
    conn = None
    try:
        
        conn = psycopg2.connect(host=host, database=db, user=user, password=password)
        cur = conn.cursor()
        cur.execute("SELECT faction_map FROM config ")
        row = cur.fetchone()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            return row

def makeidentifier(string):
     string = string.replace(' ', '_') #changes keyname to be identifier
     string = string.replace('-', '_')
     return string
# get discord ID for specified channels 
kill_channel_id = 0  #this channel is where the bot will collect kill data
ver_channel_id = 0 #this channel is where the bot will post verification messages
publish_channel_id = 0 # this is the channel where the tally will be published
mod_role_id= 0 # the role of the mods/ tally managers
ping_role_id = 0 #the role to ping when the tally is  published
guild_id = 0 #the id of the server

class MyCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    
    @commands.Cog.listener()    
    async def on_ready(self):
        self.compile.start()
        print('Logged on as {0}!'.format(self.bot.user))

        global kill_channel, ver_channel, publish_channel, ping_role, factions
        guild = self.bot.get_guild(guild_id)
        kill_channel = self.bot.get_channel(kill_channel_id)
        ver_channel = self.bot.get_channel(ver_channel_id)
        publish_channel = self.bot.get_channel(publish_channel_id)
        ping_role = guild.get_role(ping_role_id)
        factions = botconfig()[0]

        global view, button1, button2 
        view = View()
        button1 = Button(label= 'Verified', style= nextcord.ButtonStyle.green)
        button2 = Button(label= 'Rejected', style= nextcord.ButtonStyle.red)
        view.add_item(button1)
        view.add_item(button2)
    
        await fetch_pending("Pending Kills from last reset")


    @commands.Cog.listener()
    async def on_message(self, message):

        async def verified(interaction):
            kills.append(message.content)
            button1.disabled = True
            button2.disabled = True

            conn = None
            try:
                conn = psycopg2.connect(host=host, database=db, user=user, password=password)
                cur = conn.cursor()
                cmd = "DELETE FROM pending WHERE message_id = {}".format(interaction.message.embeds[0].footer.text) #its been grabbing the message id of the button, we have to get the message id in the link url
                cur.execute(cmd)
                conn.commit()
                cur.close()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                await interaction.response.edit_message(content="Error connecting to database", view=view)
            except:
                await interaction.response.edit_message(content="Something went wrong", view=view)
                
            else: 
                await interaction.response.edit_message(content = 'Verified by '+ interaction.user.name, view=view)
        
        async def reject(interaction):
            button1.disabled = True
            button2.disabled = True 
            conn = None
            try:
                conn = psycopg2.connect(host=host, database=db, user=user, password=password)
                cur = conn.cursor()
                cur.execute("DELETE FROM pending WHERE message_id = "+str(interaction.message.id))
                conn.commit()
                cur.close()
            except (Exception, psycopg2.DatabaseError):
                await interaction.response.edit_message("Error connecting to database")
            except:
                await interaction.response.edit_message("Something went wrong")

            else: 
                await interaction.response.edit_message(content = 'Rejected by '+ interaction.user.name, view=view)


        def isformat(message):
            parts = message.split(' to ')
            vict = parts[0].split()
            try:
                if vict[1] in ships: #checks if message can be run through parser:
                    Kill_Calculator.can_run(message)
            except:
                return False
            else:
                return True
        
        if message.author == self.bot.user or message.channel != kill_channel:
            return
        
         #after button pressed edit message to see who verified/rejected it
        
        
        
        

        if " to " in message.content and isformat(message.content):

            embedVar = nextcord.Embed(title = "Verify this message", description = message.content, url = message.jump_url)
            embedVar.set_author(name = message.author.name, icon_url = message.author.avatar.url)
            embedVar.set_footer(text=str(message.id))
            button1.callback = verified
            button2.callback = reject
            await ver_channel.send(embed=embedVar, view=view)
            
            
            conn = None
            cmd = """INSERT INTO pending(message_id, message, author)
            VALUES({},'{}','{}')""".format(message.id, message.content, message.author)
            try:
                conn = psycopg2.connect(host=host, database=db, user=user, password=password)
                cur = conn.cursor()
                cur.execute(cmd)
                conn.commit()
                cur.close()
            except (Exception, psycopg2.DatabaseError) as error:
                await ver_channel.send(content="Error connecting to database")
                print(error)
            except:
                await ver_channel.send(content="Something went wrong")
            finally:
                if conn is not None:
                    conn = None
  
        else:
            await message.delete()

            
        

    @commands.command()
    @commands.has_role(mod_role_id)
    async def newday(self, ctx):
        global kills
        date = datetime.datetime.now()
        header = "**Kill Tally " + date.strftime("%m/%d/%y** \n \n")
        export = Kill_Calculator.calculate(kills, factions)
        await kill_channel.send("**NEW DAY**")
        await publish_channel.send(content = header+export)
        await publish_channel.send(content = ping_role.mention)    
        kills = []
    
    @commands.command()
    @commands.has_role(mod_role_id)
    async def addgroup(self, ctx: commands.context, name, identifiers):
        identifiers = identifiers.split(',')
        factions[name]= identifiers
        data = json.dumps(factions)
        msg = 'Sucessfully added group {}'.format(name)
        await update(data, ctx, msg) 
        
    @commands.command()
    @commands.has_role(mod_role_id)
    async def removegroup(self, ctx: commands.context, group):
        del factions[group]
        data = json.dumps(factions)
        msg = 'Sucessfully removed group {}'.format(group)
        await update(data, ctx, msg)
    
    @commands.command()
    @commands.has_role(mod_role_id)
    async def addfaction(self, ctx: commands.context, group, faction):
        groups = factions.keys()
        if group not in groups:
            await ctx.send("That group does not exist!")
            return
        factions[group].append(faction)
        string = "Successfully added {0} to {1}".format(faction, group)
        data = json.dumps(factions)
        await update(data, ctx, string)
    
    @commands.command()
    @commands.has_role(mod_role_id)
    async def removefaction(self, ctx: commands.context, faction, group):
        factions2 = [x for xs in factions.values() for x in xs]

        if faction not in factions2:
            await ctx.send("That faction does not exist!")
            return
        factions[group].remove(faction)
        string = "Successfully removed {0} from {1}".format(faction, group)
        data = json.dumps(factions)
        await update(data, ctx, string)

    @commands.command()
    @commands.has_role(mod_role_id)
    async def display(self, ctx: commands.context, group ='all'):
        example = "{0}: {1}"
        if group == 'all':
            desc = ''
            example = "{0}: {1}\n"
            for i in factions.items():
                desc+= example.format(i[0], i[1])
            embedVar = nextcord.Embed(title="All groups", description=desc)
            await ctx.send(embed=embedVar)
        elif group not in factions:
            await ctx.send("That group does not exist!")
        else:
            desc = example.format(group, factions[group])
            embedVar = nextcord.Embed(title=group, description=desc)
            await ctx.send(embed=embedVar)
        
    @tasks.loop(time=reset_time)
    async def compile(self):
        global kills
        date = datetime.datetime.now()

        kill_channel = self.bot.get_channel(kill_channel_id)
        publish_channel = self.bot.get_channel(publish_channel_id)
        header = "**Kill Tally " + date.strftime("%m/%d/%y** \n \n")
        export = Kill_Calculator.calculate(kills, factions)
        await kill_channel.send("**NEW DAY**")
        await publish_channel.send(content = header+export)
        await publish_channel.send(content = ping_role.mention)
        kills = []
    data = json.dumps(factions)
    update(data, None, None)

client = commands.Bot(command_prefix='?')
client.add_cog(MyCog(client))

client.run(token)