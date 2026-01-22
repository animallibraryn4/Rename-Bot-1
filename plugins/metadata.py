from helper.database import dbcol, get_metadata, setmeta, get_title, set_title, get_author, set_author, get_artist, set_artist, get_audio, set_audio, get_subtitle, set_subtitle, get_video, set_video
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import Txt

# At the top of metadata.py, define excluded commands
EXCLUDED_COMMANDS = [
    "start", "help", "metadata", "verify", "get_token", 
    "autorename", "setmedia", "info", "set_caption", 
    "del_caption", "see_caption", "view_caption", 
    "restart", "tutorial", "stats", "status", 
    "broadcast", "donate", "bought", "sequence", 
    "sf", "fileseq", "ls", "plan", "smart_thumb", 
    "mode", "caption", "meta", "file_names", 
    "thumbnail", "metadatax", "source", "premiumx", 
    "plans", "about", "home"
]

async def clear_metadata_state(user_id):
    """Editing mode clear"""
    dbcol.update_one(
        {"_id": int(user_id)},
        {"$unset": {"editing_metadata_field": "", "editing_message_id": ""}}
    )

async def get_metadata_summary(user_id):
    """Generate a summary of all metadata settings"""
    current = get_metadata(user_id)
    title = get_title(user_id)
    author = get_author(user_id)
    artist = get_artist(user_id)
    video = get_video(user_id)
    audio = get_audio(user_id)
    subtitle = get_subtitle(user_id)
    
    summary = f"""
  **Title:** `{title if title else 'Not Set'}`
  **Author:** `{author if author else 'Not Set'}`
  **Artist:** `{artist if artist else 'Not Set'}`
  **Audio:** `{audio if audio else 'Not Set'}`
  **Subtitle:** `{subtitle if subtitle else 'Not Set'}`
  **Video:** `{video if video else 'Not Set'}`
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

@Client.on_message(filters.command("metadata"))
async def metadata_main(client, message):
    user_id = message.from_user.id
    current_status = get_metadata(user_id)
    
    summary = await get_metadata_summary(user_id)
    
    text = f"""
**Metadata Settings**

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
    current = get_metadata(user_id)
    
    # Handle toggle commands - NO NOTIFICATIONS
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
        # Don't edit if we're already on the set metadata menu
        if "Set Metadata Values" in query.message.text:
            return

        summary = await get_metadata_summary(user_id)
        
        text = f"""
**Your Metadata Is Currently: {current}**

ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀᴋᴇ ᴄʜᴀɴɢᴇꜱ
"""
        keyboard = get_set_metadata_keyboard()
        await query.message.edit_text(text=text, reply_markup=keyboard)
        return
    
    # Handle edit field selection
    elif data.startswith("edit_"):
        field = data.split("_")[1]
        await show_edit_field_prompt(query, user_id, field)
        return
    
    # Handle cancel edit operation - DELETE WITH ANIMATION
    elif data.startswith("cancel_edit_"):
        field = data.split("_")[2]
        # Clear any editing state
        await clear_metadata_state(user_id)
        # Delete message with animation
        await query.message.delete()
        return
    
    # Handle View All button
    elif data == "view_all":
        summary = await get_metadata_summary(user_id)
        
        text = f"""
**📋 Current Metadata Overview**

**Current status:** `{current}`
{summary}
"""
        
        keyboard = get_view_all_keyboard()
        await query.message.edit_text(text=text, reply_markup=keyboard)
        return
    
    # Handle back to home
    elif data == "metadata_home":
        await show_main_panel(query, user_id)
        return
    
    # Handle meta info/help
    elif data == "meta_info":
        if hasattr(Txt, 'META_TXT') and Txt.META_TXT in query.message.text:
            return
        meta_text = """
**ℹ️ Metadata Information**

**Title** - Displayed as the main name of the media file
**Author** - The creator/author of the content
**Artist** - The artist/performer name
**Audio** - Audio track information
**Subtitle** - Subtitle track information
**Video** - Video track information

These metadata fields will be embedded into your media files when metadata is enabled.
"""
        await query.message.edit_text(
            text=meta_text,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔙 Back", callback_data="set_metadata_menu"),
                    InlineKeyboardButton("Close", callback_data="close_meta")
                ]
            ])
        )
        return
    
    # Handle close - DELETE WITH ANIMATION
    elif data == "close_meta":
        await query.message.delete()
        return

async def show_edit_field_prompt(query, user_id, field):
    """Show edit prompt for a specific field"""
    field_display = field.capitalize()
    
    # Get current value
    field_methods = {
        "title": get_title,
        "author": get_author,
        "artist": get_artist,
        "audio": get_audio,
        "subtitle": get_subtitle,
        "video": get_video
    }
    
    if field in field_methods:
        current_value = field_methods[field](user_id)
    else:
        current_value = "Not set"
    
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
"""
    
    keyboard = get_edit_field_keyboard(field)
    
    # Store which field we're editing and the message ID
    dbcol.update_one(
        {"_id": int(user_id)},
        {"$set": {
            "editing_metadata_field": field,
            "editing_message_id": query.message.id
        }}
    )
    
    await query.message.edit_text(text=text, reply_markup=keyboard)

async def show_main_panel(query, user_id):
    """Show the main metadata panel"""
    current_status = get_metadata(user_id)
    summary = await get_metadata_summary(user_id)

    text = f"""
**Metadata Settings**

ᴛʜɪꜱ ʟᴇᴛꜱ ʏᴏᴜ ᴄʜᴀɴɢᴇ ᴛʜᴇ ɴᴀᴍᴇꜱ ᴀɴᴅ ᴅᴇᴛᴀɪʟꜱ ꜱʜᴏᴡɴ ᴏɴ ʏᴏᴜʀ ᴍᴇᴅɪᴀ ꜰɪʟᴇꜱ.

ʏᴏᴜ ᴄᴀɴ ᴇᴅɪᴛ ᴛʜɪɴɢꜱ ʟɪᴋᴇ ᴛɪᴛʟᴇ, ᴀᴜᴅɪᴏ ɴᴀᴍᴇ, ꜱᴜʙᴛɪᴛʟᴇ ɴᴀᴍᴇ, ᴀɴᴅ ᴀᴜᴛʜᴏʀ ꜱᴏ ʏᴏᴜʀ ꜰɪʟᴇꜱ ʟᴏᴏᴋ ᴄʟᴇᴀɴ ᴀɴᴅ ᴇᴀꜱʏ ᴛᴏ ʀᴇᴀᴅ.
"""
    
    keyboard = get_main_menu_keyboard(current_status)
    
    # Check if we're already showing this content to avoid MESSAGE_NOT_MODIFIED
    current_text = query.message.text
    if "Metadata Settings" in current_text:
        # Content is the same, don't edit
        return
    
    await query.message.edit_text(text=text, reply_markup=keyboard)

async def show_set_metadata_menu(query, user_id):
    """Show the set metadata menu"""
    current = get_metadata(user_id)
  
    text = f"""
**Your Metadata Is Currently: {current}**

ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀᴋᴇ ᴄʜᴀɴɢᴇꜱ
"""
    keyboard = get_set_metadata_keyboard()
    
    # Check if we're already showing this content
    if "Set Metadata Values" in query.message.text:
        return
    
    await query.message.edit_text(text=text, reply_markup=keyboard)

@Client.on_message(filters.private & ~filters.command(EXCLUDED_COMMANDS))
async def handle_metadata_value_input(client, message):
    """Handle text input for metadata fields - SILENT UPDATE"""
    user_id = message.from_user.id
    
    # Check if user is in metadata editing mode
    user_data = dbcol.find_one({"_id": int(user_id)})
    if not user_data or "editing_metadata_field" not in user_data or "editing_message_id" not in user_data:
        return

    # FIX: Check if message.text exists before stripping
    if not message.text:
        try:
            # Optionally alert the user or just delete the non-text message
            await message.delete()
        except:
            pass
        return
        
    field = user_data["editing_metadata_field"]
    edit_message_id = user_data["editing_message_id"]
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
        await clear_metadata_state(user_id)
        
        # SILENT UPDATE: Edit the original prompt message with new current value
        field_display = field.capitalize()
        
        # Get updated current value
        get_methods = {
            "title": get_title,
            "author": get_author,
            "artist": get_artist,
            "audio": get_audio,
            "subtitle": get_subtitle,
            "video": get_video
        }
        
        if field in get_methods:
            current_value = get_methods[field](user_id)
        else:
            current_value = "Not set"
        
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
        updated_text = f"""
**✏️ Send Me The New {field_display} Value:**

**Current {field_display}:** `{current_value}`

**Example:** `{example}`
"""
        
        keyboard = get_edit_field_keyboard(field)
        
        try:
            # Edit the original message using stored message ID
            await client.edit_message_text(
                chat_id=user_id,
                message_id=edit_message_id,
                text=updated_text,
                reply_markup=keyboard
            )
        except Exception as e:
            # If message not found or other error, just continue
            print(f"Error editing message: {e}")
        
        # Delete the user's input message
        try:
            await message.delete()
        except:
            pass
