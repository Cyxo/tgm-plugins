import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Select

COG_NAME = "RoleManager"
GUILD_ID = 311149232402726912
STAFF_CHANNEL_ID = 781551409433673748 #please change with the intended channel  lole

class RoleManager(commands.GroupCog, name=COG_NAME, group_name="role"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="Get information about requirements of the vanity roles.")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(title="── · · ✦  STAFF ROLES  ❀ ‧ ₊ ˚", description="", color=discord.Color.yellow())
        embed.set_thumbnail(url="https://catjam-united.s-ul.eu/oCSgKMpe")
        embed.add_field(name="OG〖Pulled on Release〗", value="Requirement: Get Trigger on her first release banner (1.6)", inline=False)
        embed.add_field(name="Stygian Guide〖M0 Trigger〗", value="Requirement: Having Trigger in your account", inline=False)
        embed.add_field(name="Spectral Gaze〖Weapon Haver〗", value="Requirement: Having Trigger's W-Engine in your account" , inline=False)
        embed.add_field(name="Sharpened Senses〖M1+ Trigger〗", value="Requirement: Having atleast 1 of Trigger's Mindscapes" , inline=False)
        embed.add_field(name="Condemned Soul〖M6 Trigger〗", value="Requirement: Having all 6 of Trigger's Mindscapes" , inline=False)
        embed.add_field(name="Vengeful Specter〖O5 Weapon〗", value="Requirement: Having Overclocked 4 times Trigger's W-Engine" , inline=False)
        embed.add_field(name="<@&1354886772886339593>", value="Requirement: Having Maxed all of Trigger's Skill (not counting mindscape levels)" , inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="role_request", description="Submit a request for a vanity role.")
    @app_commands.describe(role="Choose one of the available roles.")
    @app_commands.choices(
        role=[
            app_commands.Choice(name="OG〖Pulled on Release〗", value="1354884832315969719"), #Roles's ids should be already changed, so no need to change them again
            app_commands.Choice(name="Stygian Guide〖M0 Trigger〗", value="1354885013153255525"),
            app_commands.Choice(name="Spectral Gaze〖Weapon Haver〗", value="1354885535528910908"),
            app_commands.Choice(name="Sharpened Senses〖M1+ Trigger〗", value="1354885769642119340"),
            app_commands.Choice(name="Condemned Soul〖M6 Trigger〗", value="1354886255762210876"),
            app_commands.Choice(name="Vengeful Specter〖O5 Weapon〗", value="1354886598810013716"),
            app_commands.Choice(name="Locked In〖Maxed skills〗", value="1354886772886339593"),
        ]
    )
    async def role_request(self, interaction: discord.Interaction, role: app_commands.Choice[str], image: discord.Attachment, image2: discord.Attachment = None, image3: discord.Attachment = None):

        #-----------------------------------------------------------
        # Stuff
        #-----------------------------------------------------------


        guild = self.bot.get_guild(GUILD_ID) # Get the discord server
        author = interaction.user  # Get the user who requested the role
        staff_channel = guild.get_channel(STAFF_CHANNEL_ID)  # Get the staff channel


        #-----------------------------------------------------------
        # Verifications
        #-----------------------------------------------------------

        # Collect all attachments into a list
        attachments = [image, image2, image3]
        attachments = [att for att in attachments if att is not None]  # Remove None values

        # Validate that all attachments are images
        for attachment in attachments:
            if not attachment.content_type or not attachment.content_type.startswith("image/"):
                await interaction.response.send_message(
                    f"Invalid attachment: {attachment.filename} is not an image.", ephemeral=True
                )
                return
        if guild.get_role(int(role.value)) in author.roles:
            await interaction.response.send_message(
                f"You already have the role **{role.name}**.", ephemeral=True
            )
            return

        #-----------------------------------------------------------
        # User response
        #-----------------------------------------------------------
        submission_embed = discord.Embed(
            title=f"Submission by {author.name}",
            color=discord.Color.blue(),
        )
        submission_embed.add_field(name="Role", value=role.name, inline=False)
        submission_embed.set_footer(text=f"User ID: {author.id}")
        try:
            await author.send(embed=submission_embed)
            for attachment in attachments:
                await author.send(content=attachment.url)
        except discord.Forbidden:
            await interaction.response.send_message(
                "I cannot send you a DM. Please check your privacy settings.", ephemeral=True
            )
            return
        #-----------------------------------------------------------
        # Hard part
        #-----------------------------------------------------------
        staff_view = StaffView(author, role)  # Create an instance of StaffView

        # Create the main embed for the request
        main_embed = discord.Embed(
            title="New Role Request",
            description=f"**User:** {author.mention}\n**Requested Role:** {role.name}",
            color=discord.Color.blue(),
        )
        main_embed.set_author(name=author.name, icon_url=author.avatar.url if author.avatar else None)

        # Send the main embed with the view to the staff channel
        await staff_channel.send(embed=main_embed)
        # Send the images to the staff channel and attach the view to the last one
        for i, attachment in enumerate(attachments):
            embed = discord.Embed(title=f"Image {i + 1}", color=discord.Color.blue())
            embed.set_image(url=attachment.url)
            embed.set_footer(text=f"User ID: {author.id}")
            embed.set_author(name=author.name, icon_url=author.avatar.url if author.avatar else None)
            if i == len(attachments) - 1:  # If it's the last image, add the view
                await staff_channel.send(embed=embed, view=staff_view)
            else:
                await staff_channel.send(embed=embed)

        # Acknowledge the interaction
        await interaction.response.send_message(
            f"Your request for the role **{role.name}** has been submitted. Please wait for a response from the staff.",
            ephemeral=True
        )

#-----------------------------------------------------------
# How does one do views
#-----------------------------------------------------------


class StaffView(View):
    def __init__(self, author: discord.Member, role: app_commands.Choice[str]):
        self.author = author
        self.role = role
        self.selection_reasons = None  # Initialize selection reasons
        super().__init__(timeout=None)  # No timeout for the view

    async def disable_all_components(self, interaction: discord.Interaction):
        """Disable all components in the view."""
        for item in self.children:  # Iterate through all components in the view
            item.disabled = True
        await interaction.response.edit_message(view=self)  # Update the message with the disabled view

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Add the role to the user
            role_to_assign = interaction.guild.get_role(int(self.role.value))
            if role_to_assign:
                await self.author.add_roles(role_to_assign)
                # Notify the user
                try:
                    await self.author.send(f"You have been given the role: **{self.role.name}**.")
                except discord.Forbidden:
                    await interaction.response.send_message("Could not send a DM to the user.", ephemeral=True)
            else:
                await interaction.response.send_message("The role could not be found. Please contact an administrator.", ephemeral=True)

            # Respond to the interaction
            await interaction.response.send_message("Role assigned successfully!", ephemeral=False)

            # Stop the view
            self.stop()
        except Exception as e:
            print(f"Error while assigning role: {e}")

    @discord.ui.select(
        placeholder="Select a reason for rejection.",
        options=[
            discord.SelectOption(label="No proof attachment.", value="No proof attachment."),
            discord.SelectOption(label="Attached pictures are proof for a different role.", value="Attached pictures are proof for a different role."),
            discord.SelectOption(label="UID is not visible.", value="UID is not visible."),
            discord.SelectOption(label="Discord username is not in HSR bio.", value="Discord username is not in HSR bio."),
            discord.SelectOption(label="Didn't meet role requirements.", value="Didn't meet role requirements."),
            discord.SelectOption(label="Other. Please open a modmail for further information.", value="Other. Please open a modmail for further information."),
            discord.SelectOption(label="Poopyhead", value="Poopyhead")
        ],
        min_values=1,
        max_values=3
    )
    async def select_rejection_reason(self, interaction: discord.Interaction,select: discord.ui.Select):
        self.selection_reasons = select.values  # Store the selected reasons
        await interaction.response.send_message(
            f"You selected the following reason(s) for rejection: {', '.join(select.values)}",
            ephemeral=True
        )

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Notify the user about the rejection
            if self.selection_reasons:
                try:
                    embed = discord.Embed(
                        title="Role Request Rejected",
                        description=f"Your request for the role **{self.role.name}** has been rejected.",
                        color=discord.Color.red()
                    )
                    for reason in self.selection_reasons:
                        embed.add_field(name="Reason", value=reason, inline=False)
                    await self.author.send(embed=embed)
                except discord.Forbidden:
                    await interaction.response.send_message("Could not send a DM to the user.", ephemeral=True)
            else:
                try:
                    await self.author.send("Your role request has been rejected. No specific reason was provided.")
                except discord.Forbidden:
                    await interaction.response.send_message("Could not send a DM to the user.", ephemeral=True)

            # Respond to the interaction
            await interaction.response.send_message("Role request rejected.", ephemeral=False)

            # Stop the view
            self.stop()
        except Exception as e:
            print(f"Error while rejecting role request: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleManager(bot))
    await bot.tree.sync()