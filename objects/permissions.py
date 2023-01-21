import discord
from discord import app_commands
import json


class Permissions:
    file = './data/moderators.json'

    @staticmethod
    def get_admin_ids():
        with open(Permissions.file, 'r') as f:
            data = json.load(f)
        return data['admins']

    @staticmethod
    def get_mod_ids():
        with open(Permissions.file, 'r') as f:
            data = json.load(f)
        return data['mods']

    @staticmethod
    def check_if_bot_admin(interaction: discord.Interaction):
        return interaction.user.id in Permissions.get_admin_ids()

    @staticmethod
    def check_if_bot_mod(interaction: discord.Interaction):
        return interaction.user.id in Permissions.get_mod_ids() or interaction.user.id in Permissions.get_admin_ids()

class PermissionDecorators:
    is_bot_admin = app_commands.check(Permissions.check_if_bot_admin)
    is_bot_mod = app_commands.check(Permissions.check_if_bot_mod)