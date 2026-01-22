from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from helper.database import *
import script as Txt

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

def clear_metadata_state(user_id):
    """Clear editing state"""
    dbcol.update_one(
        {"_id": int(user_id)},
        {"$unset": {"editing_metadata_field": "", "editing_message_id": "", "editing_profile": ""}}
    )

def get_metadata_summary(user_id, profile_num=None):
    """Generate a summary of metadata settings for a specific profile"""
    if profile_num is None:
        profile_num = get_current_profile(user_id)
    
    current = "On" if get_metadata(user_id) else "Off"
    
    # Use profile-specific getters
    title = get_metadata_field_with_profile(user_id, "title", profile_num)
    author = get_metadata_field_with_profile(user_id, "author", profile_num)
    artist = get_metadata_field_with_profile(user_id, "artist", profile_num)
    video = get_metadata_field_with_profile(user_id, "video", profile_num)
    audio = get_metadata_field_with_profile(user_id, "audio", profile_num)
    subtitle = get_metadata_field_with_profile(user_id, "subtitle", profile_num)
    
    summary = f"""
**Current Profile: Profile {profile_num}** {'✅' if profile_num == get_current_profile(user_id) else ''}

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

def get_set_metadata_keyboard(current_profile):
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
            InlineKeyboardButton(f"🔄 Switch {2 if current_profile == 1 else 1}", callback_data=f"toggle_profile"),
            InlineKeyboardButton("🔙 Back", callback_data="metadata_home")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_view_all_keyboard(current_profile):
    """Keyboard for View All Overview page"""
    buttons = [
        [
            InlineKeyboardButton(f"🔄 Switch {2 if current_profile == 1 else 1}", callback_data=f"toggle_profile_from_view")
        ],
        [
            InlineKeyboardButton("Close", callback_data="close_meta"),
            InlineKeyboardButton("🔙 Back", callback_data="set_metadata_menu")
        ]
    ]
    return InlineKeyboardMarkup(buttons)

def get_edit_field_keyboard(field, current_profile):
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
    current_status = "On" if get_metadata(user_id) else "Off"
    current_profile = get_current_profile(user_id)
    
    text = f"""
**Metadata Settings**

ᴛʜɪꜱ ʟᴇᴛꜱ ʏᴏᴜ ᴄʜᴀɴɢᴇ ᴛʜᴇ ɴᴀᴍᴇꜱ ᴀɴᴅ ᴅᴇᴛᴀɪʟꜱ ꜱʜᴏᴡɴ ᴏɴ ʏᴏᴜʀ ᴍᴇᴅɪᴀ ꜰɪʟᴇꜱ.

ʏᴏᴜ ᴄᴀɴ ꜱᴀᴠᴇ ᴛᴡᴏ ᴅɪꜰꜰᴇʀᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ ᴘʀᴏꜰɪʟᴇꜱ ᴀɴᴅ ꜱᴡɪᴛᴄʜ ʙᴇᴛᴡᴇᴇɴ ᴛʜᴇᴍ ᴇᴀꜱɪʟʏ.

**Current Profile:** Profile {current_profile} {'✅' if current_profile == 1 else ''}
"""
    
    keyboard = get_main_menu_keyboard(current_status)
    
    await message.reply_text(
        text=text, 
        reply_markup=keyboard, 
        disable_web_page_preview=True
    )

@Client.on_callback_query(filters.regex(r'.*'))
async def metadata_callback_handler(client, query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data
    current = "On" if get_metadata(user_id) else "Off"
    current_profile = get_current_profile(user_id)
    
    # Handle toggle profile from View All page
    if data == "toggle_profile_from_view":
        new_profile = 2 if current_profile == 1 else 1
        set_current_profile(user_id, new_profile)
        await show_all_profiles_overview(query, user_id)
        return
    
    # Handle regular toggle profile
    elif data == "toggle_profile":
        new_profile = 2 if current_profile == 1 else 1
        set_current_profile(user_id, new_profile)
        current_profile = new_profile
        await show_set_metadata_menu(query, user_id)
        return
    
    # Handle toggle commands
    elif data == "on_metadata":
        set_metadata(user_id, True)
        await show_main_panel(query, user_id)
        return
    
    elif data == "off_metadata":
        set_metadata(user_id, False)
        await show_main_panel(query, user_id)
        return
    
    # Handle "Set Metadata" menu
    elif data == "set_metadata_menu":
        await show_set_metadata_menu(query, user_id)
        return
    
    # Handle edit field selection
    elif data.startswith("edit_"):
        field = data.split("_")[1]
        await show_edit_field_prompt(query, user_id, field)
        return
    
    # Handle cancel edit operation
    elif data.startswith("cancel_edit_"):
        field = data.split("_")[2]
        clear_metadata_state(user_id)
        await query.message.delete()
        return
    
    # Handle View All button
    elif data == "view_all":
        await show_all_profiles_overview(query, user_id)
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
            current_profile = get_current_profile(user_id)
            set_metadata_field_with_profile(user_id, field, default_values[field], current_profile)
            await show_set_metadata_menu(query, user_id)
        return
    
    # Handle back to home
    elif data == "metadata_home":
        await show_main_panel(query, user_id)
        return
    
    # Handle meta info/help
    elif data == "meta_info":
        if hasattr(Txt, 'META_TXT'):
            await query.message.edit_text(
                text=Txt.META_TXT,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("Close", callback_data="close_meta"),
                        InlineKeyboardButton("🔙 Back", callback_data="set_metadata_menu")
                    ]
                ])
            )
        return
    
    # Handle close
    elif data == "close_meta":
        await query.message.delete()
        return

async def show_edit_field_prompt(query, user_id, field):
    """Show edit prompt for a specific field"""
    current_profile = get_current_profile(user_id)
    field_display = field.capitalize()
    
    # Get current value with profile support
    current_value = get_metadata_field_with_profile(user_id, field, current_profile)
    if not current_value:
        # Fallback to default
        method_name = f"get_{field}"
        method = globals().get(method_name)
        if method:
            current_value = method(user_id)
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
**✏️ Send Me The New {field_display} Value**

**Current Profile:** Profile {current_profile}
**Current {field_display}:** `{current_value}`

**Example:** `{example}`
"""
    
    keyboard = get_edit_field_keyboard(field, current_profile)
    
    # Store which field we're editing and the message ID
    dbcol.update_one(
        {"_id": int(user_id)},
        {"$set": {
            "editing_metadata_field": field,
            "editing_message_id": query.message.id,
            "editing_profile": current_profile
        }}
    )
    
    await query.message.edit_text(text=text, reply_markup=keyboard)

async def show_main_panel(query, user_id):
    """Show the main metadata panel"""
    current_status = "On" if get_metadata(user_id) else "Off"
    current_profile = get_current_profile(user_id)

    text = f"""
**Metadata Settings**

ᴛʜɪꜱ ʟᴇᴛꜱ ʏᴏᴜ ᴄʜᴀɴɢᴇ ᴛʜᴇ ɴᴀᴍᴇꜱ ᴀɴᴅ ᴅᴇᴛᴀɪʟꜱ ꜱʜᴏᴡɴ ᴏɴ ʏᴏᴜʀ ᴍᴇᴅɪᴀ ꜰɪʟᴇꜱ.

ʏᴏᴜ ᴄᴀɴ ꜱᴀᴠᴇ ᴛᴡᴏ ᴅɪꜰꜰᴇʀᴇɴᴛ ᴍᴇᴛᴀᴅᴀᴛᴀ ᴘʀᴏꜰɪʟᴇꜱ ᴀɴᴅ ꜱᴡɪᴛᴄʙᴇᴛᴡᴇᴇɴ ᴛʜᴇᴍ ᴇᴀꜱɪʟʏ.

**Current Profile:** Profile {current_profile} {'✅' if current_profile == 1 else ''}
"""
    
    keyboard = get_main_menu_keyboard(current_status)
    
    await query.message.edit_text(text=text, reply_markup=keyboard)

async def show_set_metadata_menu(query, user_id):
    """Show the set metadata menu"""
    current = "On" if get_metadata(user_id) else "Off"
    current_profile = get_current_profile(user_id)
    
    text = f"""
**Set Metadata Values**

**Current Status:** {current}
**Current Profile:** Profile {current_profile} {'✅'}

ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀᴋᴇ ᴄʜᴀɴɢᴇꜱ
"""
    keyboard = get_set_metadata_keyboard(current_profile)
    
    await query.message.edit_text(text=text, reply_markup=keyboard)

async def show_all_profiles_overview(query, user_id):
    """Show overview of both profiles"""
    profiles_summary = get_all_profiles_summary(user_id)
    current_profile = get_current_profile(user_id)
    
    text = "**📋 All Metadata Profiles Overview**\n\n"
    
    for profile_num in [1, 2]:
        profile_data = profiles_summary[f"profile_{profile_num}"]
        is_active = " ✅ (Active)" if profile_num == current_profile else ""
        
        text += f"**Profile {profile_num}**{is_active}\n"
        text += f"• **Title:** `{profile_data['title'] or 'Not Set'}`\n"
        text += f"• **Author:** `{profile_data['author'] or 'Not Set'}`\n"
        text += f"• **Artist:** `{profile_data['artist'] or 'Not Set'}`\n"
        text += f"• **Audio:** `{profile_data['audio'] or 'Not Set'}`\n"
        text += f"• **Subtitle:** `{profile_data['subtitle'] or 'Not Set'}`\n"
        text += f"• **Video:** `{profile_data['video'] or 'Not Set'}`\n\n"
    
    text += "ℹ️ *Go back to the Set Metadata menu to switch profiles.*"
    
    keyboard = get_view_all_keyboard(current_profile)
    
    await query.message.edit_text(text=text, reply_markup=keyboard)

@Client.on_message(filters.private & ~filters.command(EXCLUDED_COMMANDS))
async def handle_metadata_value_input(client, message):
    """Handle text input for metadata fields with profile support"""
    user_id = message.from_user.id
    
    # Check if user is in metadata editing mode
    user_data = dbcol.find_one({"_id": int(user_id)})
    if not user_data or "editing_metadata_field" not in user_data or "editing_message_id" not in user_data:
        return

    # Check if message.text exists
    if not message.text:
        try:
            await message.delete()
        except:
            pass
        return
        
    field = user_data["editing_metadata_field"]
    edit_message_id = user_data["editing_message_id"]
    editing_profile = user_data.get("editing_profile", get_current_profile(user_id))
    new_value = message.text.strip()
    
    # Update the specific field with profile support
    success = set_metadata_field_with_profile(user_id, field, new_value, editing_profile)
    
    if success:
        # Clear editing flag
        clear_metadata_state(user_id)
        
        # Show confirmation
        field_display = field.capitalize()
        
        # Create confirmation message
        confirmation_text = f"""
✅ **{field_display} Updated Successfully!**

**Profile:** Profile {editing_profile}
**New Value:** `{new_value}`

Returning to metadata menu...
"""
        
        try:
            # Show brief confirmation
            await client.edit_message_text(
                chat_id=user_id,
                message_id=edit_message_id,
                text=confirmation_text,
                reply_markup=None
            )
            
            # Wait a moment, then show updated menu
            import asyncio
            await asyncio.sleep(1.5)
            
            # Return to set metadata menu with updated values
            await show_set_metadata_menu_direct(
                client, user_id, edit_message_id, editing_profile
            )
            
        except Exception as e:
            # If message editing fails, send new message
            await message.reply_text(
                f"✅ {field_display} updated to: `{new_value}`\n\nUse /metadata to see changes."
            )
        
        # Delete the user's input message
        try:
            await message.delete()
        except:
            pass

async def show_set_metadata_menu_direct(client, user_id, message_id, profile_num):
    """Direct function to show set metadata menu after edit"""
    current = "On" if get_metadata(user_id) else "Off"
    
    text = f"""
**Set Metadata Values**

**Current Status:** {current}
**Current Profile:** Profile {profile_num} {'✅'}

✅ Your changes have been saved!

ᴜꜱᴇ ᴛʜᴇ ʙᴜᴛᴛᴏɴꜱ ʙᴇʟᴏᴡ ᴛᴏ ᴍᴀᴋᴇ ᴍᴏʀᴇ ᴄʜᴀɴɢᴇꜱ
"""
    keyboard = get_set_metadata_keyboard(profile_num)
    
    await client.edit_message_text(
        chat_id=user_id,
        message_id=message_id,
        text=text,
        reply_markup=keyboard
    )
