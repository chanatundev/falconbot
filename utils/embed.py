import discord

from utils import localization as l

def list_to_embed(
        items: list[str], 
        title: str = None, 
        description: str = "", 
        color: discord.Color = discord.Color.red(),
        server: discord.Guild = None,
) -> discord.Embed:
    if title is None:
        if server is not None:
            title = server.name
        else:
            title = "List"
    embed = discord.Embed(title=title, description=description, color=color)
    embed.description += "\n".join(items)
    return embed

class EmbedPages(discord.ui.View):
    def __init__(self, 
        items, 
        author: discord.Member,
        items_per_page: int = 10, 
        **kwargs # to pass to list_to_embed (title, description, color, server)
    ):
        super().__init__(timeout=600)
        self.items = items
        self.items_per_page = items_per_page
        self.kwargs = kwargs
        self.pages = (len(self.items)-1) // self.items_per_page + 1
        self.page = 0
        self.author = author

    def get_embed(self):
        if len(self.items) == 0:
            return list_to_embed([], description=l.get("embed.nothing"), **self.kwargs)
        page_items = self.items[self.page*self.items_per_page:self.page*self.items_per_page+self.items_per_page]
        embed = list_to_embed(page_items,**self.kwargs)
        embed.set_footer(text=f"page {self.page + 1}/{self.pages}")
        return embed

    @discord.ui.button(label="<-")
    async def left(self, interaction, button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(l.get("embed.no_perms"), ephemeral=True)
            return
        if self.page > 0:
            self.page -= 1
        else:
            await interaction.response.send_message(l.get("embed.on_first_page"), ephemeral=True)
        await interaction.response.edit_message(
            embed=self.get_embed(),
            view=self
        )

    @discord.ui.button(label="->")
    async def right(self, interaction, button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(l.get("embed.no_perms"), ephemeral=True)
            return
        if self.page < self.pages-1:
            self.page += 1
        else:
            await interaction.response.send_message(l.get("embed.on_last_page"), ephemeral=True)
        await interaction.response.edit_message(
            embed=self.get_embed(),
            view=self
        )
    
    class GoToModal(discord.ui.Modal, title=l.get("embed.go_to_modal.title")):
        page = discord.ui.TextInput(label=l.get("embed.go_to_modal.label"), placeholder=l.get("embed.go_to_modal.placeholder"), required=True)

        def __init__(self, parent, **kwargs):
            super().__init__(**kwargs)
            self.parent = parent

        async def on_submit(self, interaction: discord.Interaction):
            if interaction.user.id != self.parent.author.id:
                await interaction.response.send_message(l.get("embed.no_perms"), ephemeral=True)
                return
            try:
                page_num = int(self.page.value)
                if 1 <= page_num <= self.parent.pages:
                    self.parent.page = page_num - 1
                    await interaction.response.edit_message(
                        embed=self.parent.get_embed(),
                        view=self.parent
                    )
                else:
                    await interaction.response.send_message(l.get("embed.go_to_modal.error", max_page=self.parent.pages), ephemeral=True)
            except ValueError:
                await interaction.response.send_message(l.get("embed.go_to_modal.nan"), ephemeral=True)

    @discord.ui.button(label="go to...")
    async def go_to(self, interaction, button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(l.get("embed.no_perms"), ephemeral=True)
            return
        await interaction.response.send_modal(self.GoToModal(self))

class SearchableEmbedPages(EmbedPages):
    def __init__(self, 
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.query = None
        self.original_items = self.items
        self.original_pages = self.pages
    
    def search(self, query):
        self.query = query
        self.items = [item for item in self.original_items if query.lower() in item.lower()]
        self.pages = (len(self.items)-1) // self.items_per_page + 1
        self.page = 0
    
    class SearchModal(discord.ui.Modal, title=l.get("embed.search_modal.title")):
        query = discord.ui.TextInput(label=l.get("embed.search_modal.label"), placeholder=l.get("embed.search_modal.placeholder"), required=True)

        def __init__(self, parent, **kwargs):
            super().__init__(**kwargs)
            self.parent = parent

        async def on_submit(self, interaction: discord.Interaction):
            if interaction.user.id != self.parent.author.id:
                await interaction.response.send_message(l.get("embed.no_perms"), ephemeral=True)
                return
            self.parent.search(self.query.value)
            await interaction.response.edit_message(
                embed=self.parent.get_embed(),
                view=self.parent
            )
    
    @discord.ui.button(label="search")
    async def search_button(self, interaction, button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(l.get("embed.no_perms"), ephemeral=True)
            return
        await interaction.response.send_modal(self.SearchModal(self))

    @discord.ui.button(label="clear search")
    async def clear_search(self, interaction, button):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(l.get("embed.no_perms"), ephemeral=True)
            return
        self.query = None
        self.items = self.original_items
        self.pages = self.original_pages
        self.page = 0
        await interaction.response.edit_message(
            embed=self.get_embed(),
            view=self
        )
    