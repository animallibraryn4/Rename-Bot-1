from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from helper.database import *
from script import *
import re

# At the top of metadata.py, define excluded commands for input handler
EXCLUDED_COMMANDS = [
    "start", "help", "metadata", "verify", "get_token", 
    "autorename", "setmedia", "info", "set_caption", 
    "del_caption", "see_caption", "view_caption", 
    "restart", "tutorial", "stats", "status", 
    "broadcast", "donate", "bought", "sequence", 
    "sf", "fileseq", "ls", "plan", "smart_thumb", 
    "mode", "caption", "meta", "file_names", 
    "thumbnail", "metadatax", "source", "premiumx", 
    "plans", "about", "home", "myplan", "ping", 
    "viewthumb", "delthumb", "users", "allids", 
    "upgrade", "warn", "addpremium", "ceasepower", 
    "resetpower"
]

async def get_metadata_summary(chat_id):
    """Generate a summary of all metadata settings"""
    user_data = find(chat_id)
    if user_data and len(user_data) >= 10:
        metadata = user_data[2]
        title = user_data[4]
        author = user_data[5]
        artist = user_data[6]
        audio = user_data[7]
        subtitle = user_data[8]
        video = user_data[9]
    else:
        metadata = "Off"
        title = get_title(chat_id)
        author = get_author(chat_id)
        artist = get_artist(chat_id)
        audio = get_audio(chat_id)
        subtitle = get_subtitle(chat_id)
        video = get_video(chat_id)
    
    summary = f"""
📋 **Metadata Status:** `{metadata}`
────────────────────
📝 **Title:** `{title if title else 'Not Set'}`
👤 **Author:** `{author if author else 'Not Set'}`
🎨 **Artist:** `{artist if artist else 'Not Set'}`
🎵 **Audio:** `{audio if audio else 'Not Set'}`
📜 **Subtitle:** `{subtitle if subtitle else 'Not Set'}`
🎬 **Video:** `{video if video else 'Not Set'}`
"""
    return summary

def get_main_menu_keyboard(current_status):
    """Generate main menu keyboard"""
    buttons = [
        [
            InlineKeyboardButton(
                f"{'✅' if current_status == 'On' else '○'} Enable", 
                callback_data='on_metadata'
            ),
            InlineKeyboardButton(
                f"{'✅' if current_status == 'Off' else '○'} Disable", 
                callback_data='off_metadata'
            )
        ],
        [
            InlineKeyboardButton("🧑🏻‍💻 Set Metadata", callback_data="set_metadata_menu")
        ],
        [
            InlineKeyboardButton("Close", callback_data="close_meta")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_set_metadata_keyboard():
    """Keyboard for setting metadata values"""
    buttons = [
        [
            InlineKeyboardButton("Title", callback_data="edit_title"),
            InlineKeyboardButton("Author", callback_data="edit_author")
        ],
        [
            InlineKeyboardButton("Artist", callback_data="edit_artist"),
            InlineKeyboardButton("Audio", callback_data="edit_audio")
        ],
        [
            InlineKeyboardButton("Subtitle", callback_data="edit_subtitle"),
            InlineKeyboardButton("Video", callback_data="edit_video")
        ],
        [
            InlineKeyboardButton("View All", callback_data="view_all"),
            InlineKeyboardButton("Help", callback_data="meta_info")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="metadata_home")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_view_all_keyboard():
    """Keyboard for View All Overview page"""
    buttons = [
        [
            InlineKeyboardButton("Close", callback_data="close_meta"),
            InlineKeyboardButton("🔙 Back", callback_data="set_metadata_menu")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_edit_field_keyboard(field):
    """Keyboard for editing a specific field"""
    buttons = [
        [
            InlineKeyboardButton("Cancel", callback_data=f"cancel_edit_{field}"),
            InlineKeyboardButton("🔙 Back", callback_data="set_metadata_menu")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

@Client.on_message(filters.private & filters.command("metadata"))
async def metadata_main(client, message):
    user_id = message.from_user.id
    user_data = find(user_id)
    
    if user_data and len(user_data) >= 3:
        current_status = user_data[2]
    else:
        current_status = "Off"
    
    summary = await get_metadata_summary(user_id)
    
    text = f"""
**⚙️ Metadata Settings Panel**

ᴛʜɪꜱ ʟᴇᴛꜱ ʏᴏᴜ ᴄʜᴀɴɢᴇ ᴛʜᴇ ɴᴀᴍᴇꜱ ᴀɴᴅ ᴅᴇᴛᴀɪʟꜱ ꜱʜᴏᴡɴ ᴏɴ ʏᴏᴜʀ ᴍᴇᴅɪᴀ ꜰɪʟᴇꜱ.

ʏᴏᴜ ᴄᴀɴ ᴇᴅɪᴛ ᴛʜɪɴɢꜱ ʟɪᴋᴇ ᴛɪᴛʟᴇ, ᴀᴜᴅɪᴏ ɴᴀᴍᴇ, ꜱᴜʙᴛɪᴛʟᴇ ɴᴀᴍᴇ, ᴀɴᴅ ᴀᴜᴛʜᴏʀ ꜱᴏ ʏᴏᴜʀ ꜰɪʟᴇꜱ ʟᴏᴏᴋ ᴄʟᴇᴀɴ ᴀɴᴅ ᴇᴀꜱʏ ᴛᴏ ʀᴇᴀᴅ.
"""
    
    keyboard = get_main_menu_keyboard(current_status)
    
    await message.reply_text(
        text=text, 
        reply_markup=keyboard, 
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex(r"^(on_metadata|off_metadata|set_metadata_menu|edit_|cancel_edit_|view_all|metadata_home|meta_info|close_meta|clear_)"))
async def metadata_callback_handler(client, query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data
    
    user_data = find(user_id)
    if user_data and len(user_data) >= 3:
        current = user_data[2]
    else:
        current = "Off"
    
    # Handle toggle commands
    if data == "on_metadata":
        setmeta(user_id, "On")
        await show_main_panel(query, user_id)
        return
    
    elif data == "off_metadata":
        setmeta(user_id, "Off")
        await show_main_panel(query, user_id)
        return
    
    # Handle "Set Metadata" menu
    elif data == "set_metadata_menu":
        summary = await get_metadata_summary(user_id)
        
        text = f"""
**⚙️ Set Metadata Values**

**Current Status:** `{current}`

ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀᴋᴇ ᴄʜᴀɴɢᴇꜱ ᴛᴏ ʏᴏᴜʀ ꜰɪʟᴇ ᴍᴇᴛᴀᴅᴀᴛᴀ
"""
        keyboard = get_set_metadata_keyboard()
        await query.message.edit_text(text=text, reply_markup=keyboard)
        return
    
    # Handle edit field selection
    elif data.startswith("edit_"):
        field = data.split("_")[1]
        await show_edit_field_prompt(query, user_id, field)
        return
    
    # Handle cancel edit operation
    elif data.startswith("cancel_edit_"):
        field = data.split("_")[2]
        # Clear any editing state
        clear_editing_state(user_id)
        # Delete message
        await query.message.delete()
        return
    
    # Handle View All button
    elif data == "view_all":
        summary = await get_metadata_summary(user_id)
        
        text = f"""
**📋 Current Metadata Overview**

{summary}

────────────────────
ℹ️ *Use the buttons below to navigate*
"""
        
        keyboard = get_view_all_keyboard()
        await query.message.edit_text(text=text, reply_markup=keyboard, disable_web_page_preview=True)
        return
    
    # Handle clearing field
    elif data.startswith("clear_"):
        field = data.split("_")[1]
        field_display = field.capitalize()
        
        # Reset to default value
        default_values = {
            "title": "Encoded by @TechifyBots",
            "author": "@TechifyBots",
            "artist": "@TechifyBots",
            "audio": "By @TechifyBots",
            "subtitle": "By @TechifyBots",
            "video": "Encoded By @TechifyBots"
        }
        
        if field in default_values:
            method_name = f"set_{field}"
            method = globals().get(method_name)
            if method:
                method(user_id, default_values[field])
                await show_set_metadata_menu(query, user_id)
        return
    
    # Handle back to home
    elif data == "metadata_home":
        await show_main_panel(query, user_id)
        return
    
    # Handle meta info/help
    elif data == "meta_info":
        help_text = """
**📚 Metadata Help Guide**

Metadata is additional information embedded in your media files. This includes:

**• Title** - Main name of the file
**• Author** - Creator/uploader name  
**• Artist** - Performer/artist name
**• Audio** - Audio track title
**• Subtitle** - Subtitle track title
**• Video** - Video track title

**How it works:**
1. Enable metadata to apply changes
2. Set individual values using buttons
3. Send files - metadata will be added automatically
4. Works with videos, audio, and documents

**Note:** Metadata is applied using FFmpeg without re-encoding.
"""
        
        await query.message.edit_text(
            text=help_text,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔙 Back", callback_data="set_metadata_menu"),
                    InlineKeyboardButton("Close", callback_data="close_meta")
                ]
            ])
        )
        return
    
    # Handle close
    elif data == "close_meta":
        clear_editing_state(user_id)
        await query.message.delete()
        return

async def show_edit_field_prompt(query, user_id, field):
    """Show edit prompt for a specific field"""
    field_display = field.capitalize()
    
    # Get current value
    get_method_name = f"get_{field}"
    get_method = globals().get(get_method_name)
    current_value = get_method(user_id) if get_method else "Not set"
    
    # Get example value
    examples = {
        "title": "Encoded By TechifyBots",
        "author": "TechifyBots",
        "artist": "TechifyBots",
        "audio": "TechifyBots",
        "subtitle": "TechifyBots",
        "video": "Encoded By TechifyBots"
    }
    example = examples.get(field, "Your custom value")
    
    text = f"""
**✏️ Send Me The New {field_display} Value:**

**Current {field_display}:** `{current_value}`

**Example:** `{example}`

────────────────────
⚠️ *Send your new value in the next message*
"""
    
    keyboard = get_edit_field_keyboard(field)
    
    # Store which field we're editing and the message ID
    set_editing_state(user_id, field, query.message.id)
    
    await query.message.edit_text(text=text, reply_markup=keyboard)

async def show_main_panel(query, user_id):
    """Show the main metadata panel"""
    user_data = find(user_id)
    if user_data and len(user_data) >= 3:
        current_status = user_data[2]
    else:
        current_status = "Off"

    text = f"""
**⚙️ Metadata Settings Panel**

ᴛʜɪꜱ ʟᴇᴛꜱ ʏᴏᴜ ᴄʜᴀɴɢᴇ ᴛʜᴇ ɴᴀᴍᴇꜱ ᴀɴᴅ ᴅᴇᴛᴀɪʟꜱ ꜱʜᴏᴡɴ ᴏɴ ʏᴏᴜʀ ᴍᴇᴅɪᴀ ꜰɪʟᴇꜱ.

ʏᴏᴜ ᴄᴀɴ ᴇᴅɪᴛ ᴛʜɪɴɢꜱ ʟɪᴋᴇ ᴛɪᴛʟᴇ, ᴀᴜᴅɪᴏ ɴᴀᴍᴇ, ꜱᴜʙᴛɪᴛʟᴇ ɴᴀᴍᴇ, ᴀɴᴅ ᴀᴜᴛʜᴏʀ ꜱᴏ ʏᴏᴜʀ ꜰɪʟᴇꜱ ʟᴏᴏᴋ ᴄʟᴇᴀɴ ᴀɴᴅ ᴇᴀꜱʏ ᴛᴏ ʀᴇᴀᴅ.
"""
    
    keyboard = get_main_menu_keyboard(current_status)
    
    await query.message.edit_text(text=text, reply_markup=keyboard)

async def show_set_metadata_menu(query, user_id):
    """Show the set metadata menu"""
    user_data = find(user_id)
    if user_data and len(user_data) >= 3:
        current = user_data[2]
    else:
        current = "Off"
    
    text = f"""
**⚙️ Set Metadata Values**

**Current Status:** `{current}`

ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀᴋᴇ ᴄʜᴀɴɢᴇꜱ ᴛᴏ ʏᴏᴜʀ ꜰɪʟᴇ ᴍᴇᴛᴀᴅᴀᴛᴀ
"""
    keyboard = get_set_metadata_keyboard()
    
    await query.message.edit_text(text=text, reply_markup=keyboard)

@Client.on_message(filters.private & ~filters.command(EXCLUDED_COMMANDS))
async def handle_metadata_value_input(client, message):
    """Handle text input for metadata fields"""
    user_id = message.from_user.id
    
    # Check if user is in metadata editing mode
    field, edit_message_id = get_editing_state(user_id)
    if not field or not edit_message_id:
        return
    
    # Check if message.text exists
    if not message.text:
        try:
            await message.delete()
        except:
            pass
        return
        
    new_value = message.text.strip()
    
    # Update the specific field
    field_methods = {
        "title": set_title,
        "author": set_author,
        "artist": set_artist,
        "audio": set_audio,
        "subtitle": set_subtitle,
        "video": set_video
    }
    
    if field in field_methods:
        field_methods[field](user_id, new_value)
        
        # Clear editing flag
        clear_editing_state(user_id)
        
        # Get updated current value
        get_method_name = f"get_{field}"
        get_method = globals().get(get_method_name)
        current_value = get_method(user_id) if get_method else "Not set"
        
        # Get example value
        examples = {
            "title": "Encoded By TechifyBots",
            "author": "TechifyBots",
            "artist": "TechifyBots",
            "audio": "TechifyBots",
            "subtitle": "TechifyBots",
            "video": "Encoded By TechifyBots"
        }
        example = examples.get(field, "Your custom value")
        
        # Update the original edit prompt message
        field_display = field.capitalize()
        updated_text = f"""
**✅ {field_display} Updated Successfully!**

**Current {field_display}:** `{current_value}`

**Example:** `{example}`

────────────────────
*You can edit another field or go back*
"""
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✏️ Edit Again", callback_data=f"edit_{field}"),
                InlineKeyboardButton("🔙 Back", callback_data="set_metadata_menu")
            ]
        ])
        
        try:
            # Edit the original message
            await client.edit_message_text(
                chat_id=user_id,
                message_id=int(edit_message_id),
                text=updated_text,
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Error editing message: {e}")
        
        # Delete the user's input message
        try:
            await message.delete()
        except:
            pass
