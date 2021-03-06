# Chat Module for Friendly-Telegram UserBot.
# Copyright (C) 2020 @Fl1yd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ======================================================================

import logging
from .. import loader, utils
from os import remove
from telethon import functions
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.errors.rpcerrorlist import MessageTooLongError
from telethon.errors import (UserIdInvalidError, UserNotMutualContactError, UserPrivacyRestrictedError, BotGroupsBlockedError, ChannelPrivateError, YouBlockedUserError,
                             UserBlockedError, ChatAdminRequiredError, UserKickedError, InputUserDeactivatedError, ChatWriteForbiddenError, UserAlreadyParticipantError)
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (ChannelParticipantsAdmins, PeerChat, ChannelParticipantsBots)
from userbot import bot
logger = logging.getLogger(__name__)


def register(cb):
    cb(ChatMod())

class ChatMod(loader.Module):
    """Чат модуль"""
    strings = {'name': 'ChatModule'}

    def __init__(self):
        self.config = loader.ModuleConfig("Зашифровать", False, lambda m: ("Кодировать символы Юникода", m))

    def _handle_string(self, string):
        if self.config["Зашифровать"]:
            return utils.escape_html(ascii(string))
        return utils.escape_html(string)

    async def client_ready(self, client, db):
        self.client = client


    async def useridcmd(self, usrid):
        """Команда .userid <@ или реплай> показывает ID выбранного пользователя."""
        if usrid.is_reply:
            full = await self.client(GetFullUserRequest((await usrid.get_reply_message()).from_id))
        else:
            args = utils.get_args(usrid)
            try:
                full = await self.client(GetFullUserRequest(args[0]))
            except:
                full = await self.client(GetFullUserRequest(usrid.from_id))
        logger.debug(full)
        message = ("<b>Имя:</b> <code>{}</code>\n".format(self._handle_string(full.user.first_name)))
        message += ("<b>ID:</b> <code>{}</code>".format(utils.escape_html(full.user.id)))
        await utils.answer(usrid, message)


    async def chatidcmd(self, chtid):
        """Команда .chatid показывает ID чата."""
        await chtid.edit("<b>Чат ID: </b><code>" + str(chtid.chat_id) + "</code>")


    async def invitecmd(self, event):
        """Используйте .invite <@ или реплай>, чтобы добавить пользователя в чат."""
        if event.fwd_from:
            return
        to_add_users = utils.get_args_raw(event)
        reply = await event.get_reply_message()
        if not to_add_users and not reply:
            await event.edit("<b>Нет аргументов.</b>")
        elif reply:
            to_add_users = str(reply.from_id)
        if to_add_users:
            if not event.is_group and not event.is_channel:
                return await event.edit("<b>Это не чат!</b>")
            else:
                if not event.is_channel and event.is_group:
                    # https://tl.telethon.dev/methods/messages/add_chat_user.html
                    for user_id in to_add_users.split(" "):
                        try:
                            userID = int(user_id)
                        except:
                            userID = user_id

                        try:
                            await event.client(functions.messages.AddChatUserRequest(chat_id=event.chat_id,
                                                                                     user_id=userID,
                                                                                     fwd_limit=1000000))
                        except ValueError:
                            await event.reply("<b>Неверный @ или ID.</b>")
                            return
                        except UserIdInvalidError:
                            await event.reply("<b>Неверный @ или ID.</b>")
                            return
                        except UserPrivacyRestrictedError:
                            await event.reply("<b>Настойки приватности пользователя не позволяют пригласить его.</b>")
                            return
                        except UserNotMutualContactError:
                            await event.reply("<b>Настойки приватности пользователя не позволяют пригласить его.</b>")
                            return
                        except ChatAdminRequiredError:
                            await event.reply("<b>У меня нет прав.</b>")
                            return
                        except ChatWriteForbiddenError:
                            await event.reply("<b>У меня нет прав.</b>")
                            return
                        except ChannelPrivateError:
                            await event.reply("<b>У меня нет прав.</b>")
                            return
                        except UserKickedError:
                            await event.reply("<b>Пользователь кикнут из чата, обратитесь к администраторам.</b>")
                            return
                        except BotGroupsBlockedError:
                            await event.reply("<b>Бот заблокирован в чате, обратитесь к администраторам.</b>")
                            return
                        except UserBlockedError:
                            await event.reply("<b>Пользователь заблокирован в чате, обратитесь к администраторам.</b>")
                            return
                        except InputUserDeactivatedError:
                            await event.reply("<b>Аккаунт пользователя удалён.</b>")
                            return
                        except UserAlreadyParticipantError:
                            await event.reply("<b>Пользователь уже в группе.</b>")
                            return
                        except YouBlockedUserError:
                            await event.reply("<b>Вы заблокировали этого пользователя.</b>")
                            return
                    await event.edit("<b>Пользователь приглашён успешно!</b>")
                else:
                    # https://tl.telethon.dev/methods/channels/invite_to_channel.html
                    for user_id in to_add_users.split(" "):
                        try:
                            userID = int(user_id)
                        except:
                            userID = user_id

                        try:
                            await event.client(functions.channels.InviteToChannelRequest(channel=event.chat_id,
                                                                                         users=[userID]))
                        except ValueError:
                            await event.reply("<b>Неверный @ или ID.</b>")
                            return
                        except UserIdInvalidError:
                            await event.reply("<b>Неверный @ или ID.</b>")
                            return
                        except UserPrivacyRestrictedError:
                            await event.reply("<b>Настойки приватности пользователя не позволяют пригласить его.</b>")
                            return
                        except UserNotMutualContactError:
                            await event.reply("<b>Настойки приватности пользователя не позволяют пригласить его.</b>")
                            return
                        except ChatAdminRequiredError:
                            await event.reply("<b>У меня нет прав.</b>")
                            return
                        except ChatWriteForbiddenError:
                            await event.reply("<b>У меня нет прав.</b>")
                            return
                        except ChannelPrivateError:
                            await event.reply("<b>У меня нет прав.</b>")
                            return
                        except UserKickedError:
                            await event.reply("<b>Пользователь кикнут из чата, обратитесь к администраторам.</b>")
                            return
                        except BotGroupsBlockedError:
                            await event.reply("<b>Бот заблокирован в чате, обратитесь к администраторам.</b>")
                            return
                        except UserBlockedError:
                            await event.reply("<b>Пользователь заблокирован в чате, обратитесь к администраторам.</b>")
                            return
                        except InputUserDeactivatedError:
                            await event.reply("<b>Аккаунт пользователя удалён.</b>")
                            return
                        except UserAlreadyParticipantError:
                            await event.reply("<b>Пользователь уже в группе.</b>")
                            return
                        except YouBlockedUserError:
                            await event.reply("<b>Вы заблокировали этого пользователя.</b>")
                            return
                        await event.edit("<b>Пользователь приглашён успешно!</b>")


    async def kickmecmd(self, leave):
        """Используйте команду .kickme <причина>; ничего, чтобы кикнуть себя из чата."""
        reason = utils.get_args_raw(leave)
        try:
            if reason:
                await leave.edit(f"<b>До связи.\nПричина: {reason}.</b>")
            else:
                await leave.edit("<b>До связи.</b>")
            await leave.client(LeaveChannelRequest(leave.chat_id))
        except:
            await leave.edit("<b>Это не чат!</b>")
            return


    async def userscmd(self, message):
        """Команда .users <имя> выводит список всех пользователей в чате."""
        if message.chat:
            try:
                await message.edit("<b>Считаем...</b>")
                info = await message.client.get_entity(message.chat_id)
                title = info.title if info.title else "this chat"
                users = await message.client.get_participants(message.chat_id)
                mentions = f'<b>Пользователей в "{title}": {len(users)}</b> \n'
                if not utils.get_args_raw(message):
                    users = await bot.get_participants(message.chat_id)
                    for user in users:
                        if not user.deleted:
                            mentions += f"\n• <a href =\"tg://user?id={user.id}\">{user.first_name}</a> <b>|</b> <code>{user.id}</code>"
                        else:
                            mentions += f"\n• Удалённый аккаунт <b>|</b> <code>{user.id}</code>"
                else:
                    searchq = utils.get_args_raw(message)
                    users = await message.client.get_participants(message.chat_id, search=f"{searchq}")
                    mentions = f'<b>В чате "{title}" найдено {len(users)} пользователей с именем {searchq}:</b> \n'
                    for user in users:
                        if not user.deleted:
                            mentions += f"\n• <a href =\"tg://user?id={user.id}\">{user.first_name}</a> <b>|</b> <code>{user.id}</code>"
                        else:
                            mentions += f"\n• Удалённый аккаунт <b>|</b> <code>{user.id}</code>"
            except ChatAdminRequiredError as err:
                info = await message.client.get_entity(message.chat_id)
                title = info.title if info.title else "this chat"
                users = await message.client.get_participants(message.chat_id)
                mentions = f'<b>Пользователей в "{title}": {len(users)}</b> \n'
                mentions += " " + str(err) + "\n"
        else:
            await message.edit("<b>Это не чат!</b>")
            return
        try:
            await message.edit(mentions)
        except MessageTooLongError:
            await message.edit("<b>Черт, слишком большой чат. Загружаю список пользователей в файл...</b>")
            file = open("userslist.md", "w+")
            file.write(mentions)
            file.close()
            await message.client.send_file(message.chat_id,
                                           "userslist.md",
                                           caption="<b>Пользователей в {}:</b>".format(title),
                                           reply_to=message.id)
            remove("userslist.md")
            await message.delete()


    async def adminscmd(self, message):
        """Команда .admins показывает список всех админов в чате."""
        if message.chat:
            await message.edit("<b>Считаем...</b>")
            info = await message.client.get_entity(message.chat_id)
            title = info.title if info.title else "this chat"
            admins = await message.client.get_participants(message.chat_id, filter=ChannelParticipantsAdmins)
            mentions = f'<b>Админов в "{title}": {len(admins)}</b> \n'
            for user in await message.client.get_participants(message.chat_id, filter=ChannelParticipantsAdmins):
                if not user.deleted:
                    link = f"• <a href=\"tg://user?id={user.id}\">{user.first_name}</a>"
                    userid = f"<code>{user.id}</code>"
                    mentions += f"\n{link} <b>|</b> {userid}"
                else:
                    mentions += f"\n• Удалённый аккаунт <b>|</b> <code>{user.id}</code>"
            try:
                await message.edit(mentions, parse_mode="html")
            except MessageTooLongError:
                await message.edit("Черт, слишком много админов здесь. Загружаю список админов в файл...")
                file = open("adminlist.md", "w+")
                file.write(mentions)
                file.close()
                await message.client.send_file(message.chat_id,
                                               "adminlist.md",
                                               caption="<b>Админов в {}:<b>".format(title),
                                               reply_to=message.id)
                remove("adminlist.md")
                await message.delete()
        else:
            await message.edit("<b>Я слышал, что только чаты могут иметь админов...</b>")


    async def botscmd(self, message):
        """Команда .bots показывает список всех ботов в чате."""
        if message.chat:
            await message.edit("<b>Считаем...</b>")
            info = await message.client.get_entity(message.chat_id)
            title = info.title if info.title else "this chat"
            bots = await message.client.get_participants(message.to_id, filter=ChannelParticipantsBots)
            mentions = f'<b>Ботов в "{title}": {len(bots)}</b>\n'
            try:
                if isinstance(message.to_id, PeerChat):
                    await message.edit("<b>Я слышал, что только чаты могут иметь ботов...</b>")
                    return
                else:
                    async for user in message.client.iter_participants(message.chat_id, filter=ChannelParticipantsBots):
                        if not user.deleted:
                            link = f"• <a href=\"tg://user?id={user.id}\">{user.first_name}</a>"
                            userid = f"<code>{user.id}</code>"
                            mentions += f"\n{link} <b>|</b> {userid}"
                        else:
                            mentions += f"\n• Удалённый бот <b>|</b> <code>{user.id}</code>"
            except ChatAdminRequiredError as err:
                mentions += " " + str(err) + "\n"
            try:
                await message.edit(mentions, parse_mode="html")
            except MessageTooLongError:
                await message.edit(
                    "Черт, слишком много ботов здесь. Загружаю список ботов в файл...")
                file = open("botlist.md", "w+")
                file.write(mentions)
                file.close()
                await message.client.send_file(message.chat_id,
                                               "botlist.md",
                                               caption="<b>Ботов в {}:</b>".format(title),
                                               reply_to=message.id)
                remove("botlist.md")
                await message.delete()
        else:
            await message.edit("<b>Я слышал, что только чаты могут иметь ботов...</b>")
