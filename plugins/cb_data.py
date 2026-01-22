from helper.progress import progress_for_pyrogram
from pyrogram import Client, filters
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, ForceReply)
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.database import *
import os, random, time, asyncio, humanize
from PIL import Image
from datetime import timedelta
from helper.ffmpeg import take_screen_shot, fix_thumb, add_metadata, add_metadata_advanced
from helper.progress import humanbytes
from helper.set import escape_invalid_curly_brackets
from config import *

app = Client("JishuBotz", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)





@Client.on_callback_query(filters.regex('cancel'))
async def cancel(bot, update):
    try:
        await update.message.delete()
        await update.message.reply_to_message.delete()
        await update.message.continue_propagation()
    except:
        await update.message.delete()
        await update.message.continue_propagation()
        return



@Client.on_callback_query(filters.regex('rename'))
async def rename(bot, update):
    date_fa = str(update.message.date)
    pattern = '%Y-%m-%d %H:%M:%S'
    date = int(time.mktime(time.strptime(date_fa, pattern)))
    chat_id = update.message.chat.id
    id = update.message.reply_to_message_id
    await update.message.delete()
    await update.message.reply_text(f"__Please Enter The New Filename...__\n\n**Note :** Extension Not Required", reply_to_message_id=id,
                                    reply_markup=ForceReply(True))
    dateupdate(chat_id, date)



@Client.on_callback_query(filters.regex("doc"))
async def doc(bot, update):
    try:
        # Creating Directory for Metadata
        if not os.path.isdir("Metadata"):
            os.mkdir("Metadata")

        # Try to get the original message in multiple ways
        message = None
        
        # Method 1: Check if callback has data stored
        if hasattr(update, 'data') and update.data:
            # Try to extract message ID from callback data
            pass
        
        # Method 2: Check reply_to_message
        if update.message and update.message.reply_to_message:
            message = update.message.reply_to_message
        # Method 3: Check if message itself contains media
        elif update.message and (update.message.document or update.message.video or update.message.audio):
            message = update.message
        else:
            # Try to get from database or cache
            # You might need to store the message when /metadata is called
            await update.message.edit("❌ Please reply to a file with /metadata command first, then select a format.")
            return

        if not message:
            await update.message.edit("❌ Error: No file found. Please use /metadata command on a file first.")
            return

        # Get filename from message or ForceReply
        new_name = update.message.text if update.message.text else ""
        
        if not new_name or ":-" not in new_name:
            # If no filename provided, use original filename
            if message.document:
                new_filename = message.document.file_name
            elif message.video:
                new_filename = message.video.file_name
            elif message.audio:
                new_filename = message.audio.file_name
            else:
                new_filename = "file"
        else:
            try:
                new_filename = new_name.split(":-")[1].strip()
            except IndexError:
                new_filename = new_name.strip()

        used_ = find_one(update.from_user.id)
        used = used_["used_limit"]
        date = used_["date"]
        
        file_path = f"downloads/{new_filename}"
        file = message.document or message.video or message.audio
        
        if not file:
            await update.message.edit("❌ Error: No file found in the message.")
            return
            
        ms = await update.message.edit("🚀 Try To Download...  ⚡")
        used_limit(update.from_user.id, file.file_size)
        c_time = time.time()
        total_used = used + int(file.file_size)
        used_limit(update.from_user.id, total_used)
        
        try:
            path = await bot.download_media(message=file, progress=progress_for_pyrogram, progress_args=("🚀 Try To Downloading...  ⚡",  ms, c_time))
        except Exception as e:
            neg_used = used - int(file.file_size)
            used_limit(update.from_user.id, neg_used)
            await ms.edit(f"❌ Download Error: {str(e)}")
            return
        
        # METADATA ADDING CODE - UPDATED
        user_data = find(int(message.chat.id))
        if user_data and len(user_data) >= 3:
            _bool_metadata = user_data[2]  # "On" or "Off"
        else:
            _bool_metadata = "Off"
        
        if _bool_metadata == "On":
            metadata_path = f"Metadata/{new_filename}"
            # Use advanced metadata function
            await add_metadata_advanced(path, metadata_path, int(message.chat.id), ms)
        else:
            await ms.edit("🚀 Processing without metadata...  ⚡")

        splitpath = path.split("/downloads/")
        dow_file_name = splitpath[1]
        old_file_name = f"downloads/{dow_file_name}"
        os.rename(old_file_name, file_path)
        user_id = int(update.message.chat.id)
        data = find(user_id)
        try:
            c_caption = data[1]
        except:
            pass
        thumb = data[0]
        if c_caption:
            doc_list = ["filename", "filesize"]
            new_tex = escape_invalid_curly_brackets(c_caption, doc_list)
            caption = new_tex.format(
                filename=new_filename, filesize=humanbytes(file.file_size))
        else:
            caption = f"**{new_filename}**"
        if thumb:
            ph_path = await bot.download_media(thumb)
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img.resize((320, 320))
            img.save(ph_path, "JPEG")
            c_time = time.time()

        else:
            ph_path = None

        value = 2090000000
        if value < file.file_size:
            await ms.edit("🚀 Try To Upload...  ⚡")
            try:
                output_path = metadata_path if (_bool_metadata == "On" and os.path.exists(metadata_path)) else file_path
                filw = await app.send_document(LOG_CHANNEL, document=output_path, thumb=ph_path, caption=caption, progress=progress_for_pyrogram, progress_args=("🚀 Try To Uploading...  ⚡",  ms, c_time))
                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                
                # Cleanup
                try:
                    os.remove(file_path)
                    if _bool_metadata == "On" and os.path.exists(metadata_path):
                        os.remove(metadata_path)
                    if ph_path and os.path.exists(ph_path):
                        os.remove(ph_path)
                except:
                    pass
                
            except Exception as e:
                neg_used = used - int(file.file_size)
                used_limit(update.from_user.id, neg_used)
                await ms.edit(f"❌ Upload Error: {str(e)}")
                # Cleanup on error
                try:
                    os.remove(file_path)
                    if _bool_metadata == "On" and os.path.exists(metadata_path):
                        os.remove(metadata_path)
                    if ph_path and os.path.exists(ph_path):
                        os.remove(ph_path)
                except:
                    pass
                return
        else:
            await ms.edit("🚀 Try To Upload...  ⚡")
            c_time = time.time()
            try:
                output_path = metadata_path if (_bool_metadata == "On" and os.path.exists(metadata_path)) else file_path
                await bot.send_document(update.from_user.id, document=output_path, thumb=ph_path, caption=caption, progress=progress_for_pyrogram, progress_args=("🚀 Try To Uploading...  ⚡",  ms, c_time))
                await ms.delete()
                
                # Cleanup
                try:
                    os.remove(file_path)
                    if _bool_metadata == "On" and os.path.exists(metadata_path):
                        os.remove(metadata_path)
                    if ph_path and os.path.exists(ph_path):
                        os.remove(ph_path)
                except:
                    pass
                
            except Exception as e:
                neg_used = used - int(file.file_size)
                used_limit(update.from_user.id, neg_used)
                await ms.edit(f"❌ Upload Error: {str(e)}")
                # Cleanup on error
                try:
                    os.remove(file_path)
                    if _bool_metadata == "On" and os.path.exists(metadata_path):
                        os.remove(metadata_path)
                except:
                    pass
                return
    except Exception as e:
        await update.message.edit(f"❌ Unexpected Error: {str(e)}")
        return


@Client.on_callback_query(filters.regex("vid"))
async def vid(bot, update):
    try:
        # Creating Directory for Metadata
        if not os.path.isdir("Metadata"):
            os.mkdir("Metadata")

        # Try to get the original message
        message = None
        
        if update.message and update.message.reply_to_message:
            message = update.message.reply_to_message
        elif update.message and (update.message.document or update.message.video or update.message.audio):
            message = update.message
        else:
            await update.message.edit("❌ Please reply to a file with /metadata command first, then select a format.")
            return

        if not message:
            await update.message.edit("❌ Error: No file found. Please use /metadata command on a file first.")
            return

        new_name = update.message.text if update.message.text else ""
        
        if not new_name or ":-" not in new_name:
            if message.document:
                new_filename = message.document.file_name
            elif message.video:
                new_filename = message.video.file_name
            elif message.audio:
                new_filename = message.audio.file_name
            else:
                new_filename = "file"
        else:
            try:
                new_filename = new_name.split(":-")[1].strip()
            except IndexError:
                new_filename = new_name.strip()

        used_ = find_one(update.from_user.id)
        used = used_["used_limit"]
        date = used_["date"]
        
        file_path = f"downloads/{new_filename}"
        file = message.document or message.video or message.audio
        
        if not file:
            await update.message.edit("❌ Error: No file found in the message.")
            return
            
        ms = await update.message.edit("🚀 Try To Download...  ⚡")
        used_limit(update.from_user.id, file.file_size)
        c_time = time.time()
        total_used = used + int(file.file_size)
        used_limit(update.from_user.id, total_used)
        
        try:
            path = await bot.download_media(message=file, progress=progress_for_pyrogram, progress_args=("🚀 Try To Downloading...  ⚡",  ms, c_time))
        except Exception as e:
            neg_used = used - int(file.file_size)
            used_limit(update.from_user.id, neg_used)
            await ms.edit(f"❌ Download Error: {str(e)}")
            return
        
        # METADATA ADDING CODE - UPDATED
        user_data = find(int(message.chat.id))
        if user_data and len(user_data) >= 3:
            _bool_metadata = user_data[2]  # "On" or "Off"
        else:
            _bool_metadata = "Off"

        if _bool_metadata == "On":
            metadata_path = f"Metadata/{new_filename}"
            # Use advanced metadata function
            await add_metadata_advanced(path, metadata_path, int(message.chat.id), ms)
        else:
            await ms.edit("🚀 Processing without metadata...  ⚡")

        splitpath = path.split("/downloads/")
        dow_file_name = splitpath[1]
        old_file_name = f"downloads/{dow_file_name}"
        os.rename(old_file_name, file_path)
        user_id = int(update.message.chat.id)
        data = find(user_id)
        try:
            c_caption = data[1]
        except:
            pass
        thumb = data[0]

        duration = 0
        metadata = extractMetadata(createParser(file_path))
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        if c_caption:
            vid_list = ["filename", "filesize", "duration"]
            new_tex = escape_invalid_curly_brackets(c_caption, vid_list)
            caption = new_tex.format(filename=new_filename, filesize=humanbytes(
                file.file_size), duration=timedelta(seconds=duration))
        else:
            caption = f"**{new_filename}**"
        if thumb:
            ph_path = await bot.download_media(thumb)
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img.resize((320, 320))
            img.save(ph_path, "JPEG")
            c_time = time.time()

        else:
            try:
                ph_path_ = await take_screen_shot(file_path, os.path.dirname(os.path.abspath(file_path)), random.randint(0, duration - 1))
                width, height, ph_path = await fix_thumb(ph_path_)
            except Exception as e:
                ph_path = None
                print(e)

        value = 2090000000
        if value < file.file_size:
            await ms.edit("🚀 Try To Upload...  ⚡")
            try:
                output_path = metadata_path if (_bool_metadata == "On" and os.path.exists(metadata_path)) else file_path
                filw = await app.send_video(LOG_CHANNEL, video=output_path, thumb=ph_path, duration=duration, caption=caption, progress=progress_for_pyrogram, progress_args=("🚀 Try To Uploading...  ⚡",  ms, c_time))
                from_chat = filw.chat.id
                mg_id = filw.id
                time.sleep(2)
                await bot.copy_message(update.from_user.id, from_chat, mg_id)
                await ms.delete()
                
                # Cleanup
                try:
                    os.remove(file_path)
                    if _bool_metadata == "On" and os.path.exists(metadata_path):
                        os.remove(metadata_path)
                    if ph_path and os.path.exists(ph_path):
                        os.remove(ph_path)
                except:
                    pass
                    
            except Exception as e:
                neg_used = used - int(file.file_size)
                used_limit(update.from_user.id, neg_used)
                await ms.edit(f"❌ Upload Error: {str(e)}")
                # Cleanup on error
                try:
                    os.remove(file_path)
                    if _bool_metadata == "On" and os.path.exists(metadata_path):
                        os.remove(metadata_path)
                    if ph_path and os.path.exists(ph_path):
                        os.remove(ph_path)
                except:
                    pass
                return
        else:
            await ms.edit("🚀 Try To Upload...  ⚡")
            c_time = time.time()
            try:
                output_path = metadata_path if (_bool_metadata == "On" and os.path.exists(metadata_path)) else file_path
                await bot.send_video(update.from_user.id, video=output_path, thumb=ph_path, duration=duration, caption=caption, progress=progress_for_pyrogram, progress_args=("🚀 Try To Uploading...  ⚡",  ms, c_time))
                await ms.delete()
                
                # Cleanup
                try:
                    os.remove(file_path)
                    if _bool_metadata == "On" and os.path.exists(metadata_path):
                        os.remove(metadata_path)
                    if ph_path and os.path.exists(ph_path):
                        os.remove(ph_path)
                except:
                    pass
                
            except Exception as e:
                neg_used = used - int(file.file_size)
                used_limit(update.from_user.id, neg_used)
                await ms.edit(f"❌ Upload Error: {str(e)}")
                # Cleanup on error
                try:
                    os.remove(file_path)
                    if _bool_metadata == "On" and os.path.exists(metadata_path):
                        os.remove(metadata_path)
                except:
                    pass
                return
    except Exception as e:
        await update.message.edit(f"❌ Unexpected Error: {str(e)}")
        return


@Client.on_callback_query(filters.regex("aud"))
async def aud(bot, update):
    try:
        # Creating Directory for Metadata
        if not os.path.isdir("Metadata"):
            os.mkdir("Metadata")

        # Try to get the original message
        message = None
        
        if update.message and update.message.reply_to_message:
            message = update.message.reply_to_message
        elif update.message and (update.message.document or update.message.video or update.message.audio):
            message = update.message
        else:
            await update.message.edit("❌ Please reply to a file with /metadata command first, then select a format.")
            return

        if not message:
            await update.message.edit("❌ Error: No file found. Please use /metadata command on a file first.")
            return

        new_name = update.message.text if update.message.text else ""
        
        if not new_name or ":-" not in new_name:
            if message.document:
                new_filename = message.document.file_name
            elif message.video:
                new_filename = message.video.file_name
            elif message.audio:
                new_filename = message.audio.file_name
            else:
                new_filename = "file"
        else:
            try:
                new_filename = new_name.split(":-")[1].strip()
            except IndexError:
                new_filename = new_name.strip()

        used_ = find_one(update.from_user.id)
        used = used_["used_limit"]
        
        file_path = f"downloads/{new_filename}"
        file = message.document or message.video or message.audio
        
        if not file:
            await update.message.edit("❌ Error: No file found in the message.")
            return
            
        total_used = used + int(file.file_size)
        used_limit(update.from_user.id, total_used)
        ms = await update.message.edit("🚀 Try To Download...  ⚡")
        c_time = time.time()
        
        try:
            path = await bot.download_media(message=file, progress=progress_for_pyrogram, progress_args=("🚀 Try To Downloading...  ⚡",  ms, c_time))
        except Exception as e:
            neg_used = used - int(file.file_size)
            used_limit(update.from_user.id, neg_used)
            await ms.edit(f"❌ Download Error: {str(e)}")
            return
        
        # METADATA ADDING CODE - UPDATED
        user_data = find(int(message.chat.id))
        if user_data and len(user_data) >= 3:
            _bool_metadata = user_data[2]  # "On" or "Off"
        else:
            _bool_metadata = "Off"

        if _bool_metadata == "On":
            metadata_path = f"Metadata/{new_filename}"
            # Use advanced metadata function
            await add_metadata_advanced(path, metadata_path, int(message.chat.id), ms)
        else:
            await ms.edit("🚀 Processing without metadata...  ⚡")
            
        splitpath = path.split("/downloads/")
        dow_file_name = splitpath[1]
        old_file_name = f"downloads/{dow_file_name}"
        os.rename(old_file_name, file_path)
        duration = 0
        metadata = extractMetadata(createParser(file_path))
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        user_id = int(update.message.chat.id)
        data = find(user_id)
        c_caption = data[1]
        thumb = data[0]
        if c_caption:
            aud_list = ["filename", "filesize", "duration"]
            new_tex = escape_invalid_curly_brackets(c_caption, aud_list)
            caption = new_tex.format(filename=new_filename, filesize=humanbytes(
                file.file_size), duration=timedelta(seconds=duration))
        else:
            caption = f"**{new_filename}**"

        if thumb:
            ph_path = await bot.download_media(thumb)
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img.resize((320, 320))
            img.save(ph_path, "JPEG")
            await ms.edit("🚀 Try To Upload...  ⚡")
            c_time = time.time()
            try:
                output_path = metadata_path if (_bool_metadata == "On" and os.path.exists(metadata_path)) else file_path
                await bot.send_audio(update.message.chat.id, audio=output_path, caption=caption, thumb=ph_path, duration=duration, progress=progress_for_pyrogram, progress_args=("🚀 Try To Uploading...  ⚡",  ms, c_time))
                await ms.delete()
                
                # Cleanup
                try:
                    os.remove(file_path)
                    if _bool_metadata == "On" and os.path.exists(metadata_path):
                        os.remove(metadata_path)
                    os.remove(ph_path)
                except:
                    pass
                
            except Exception as e:
                neg_used = used - int(file.file_size)
                used_limit(update.from_user.id, neg_used)
                await ms.edit(f"❌ Upload Error: {str(e)}")
                # Cleanup on error
                try:
                    os.remove(file_path)
                    if _bool_metadata == "On" and os.path.exists(metadata_path):
                        os.remove(metadata_path)
                    os.remove(ph_path)
                except:
                    pass
                return
        else:
            await ms.edit("🚀 Try To Upload...  ⚡")
            c_time = time.time()
            try:
                output_path = metadata_path if (_bool_metadata == "On" and os.path.exists(metadata_path)) else file_path
                await bot.send_audio(update.message.chat.id, audio=output_path, caption=caption, duration=duration, progress=progress_for_pyrogram, progress_args=("🚀 Try To Uploading...  ⚡",  ms, c_time))
                await ms.delete()
                
                # Cleanup
                try:
                    os.remove(file_path)
                    if _bool_metadata == "On" and os.path.exists(metadata_path):
                        os.remove(metadata_path)
                except:
                    pass
                
            except Exception as e:
                await ms.edit(f"❌ Upload Error: {str(e)}")
                neg_used = used - int(file.file_size)
                used_limit(update.from_user.id, neg_used)
                # Cleanup on error
                try:
                    os.remove(file_path)
                    if _bool_metadata == "On" and os.path.exists(metadata_path):
                        os.remove(metadata_path)
                except:
                    pass
                return
    except Exception as e:
        await update.message.edit(f"❌ Unexpected Error: {str(e)}")
        return
