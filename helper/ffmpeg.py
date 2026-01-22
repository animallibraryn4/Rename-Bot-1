import time
import os
import asyncio
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.database import find, get_title, get_author, get_artist, get_audio, get_subtitle, get_video

async def fix_thumb(thumb):
    width = 0
    height = 0
    try:
        if thumb != None:
            metadata = extractMetadata(createParser(thumb))
            if metadata.has("width"):
                width = metadata.get("width")
            if metadata.has("height"):
                height = metadata.get("height")
                Image.open(thumb).convert("RGB").save(thumb)
                img = Image.open(thumb)
                img.resize((320, height))
                img.save(thumb, "JPEG")
    except Exception as e:
        print(e)
        thumb = None 
       
    return width, height, thumb
    
async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = f"{output_directory}/{time.time()}.jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name
    ]
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    return None

async def add_metadata_advanced(input_path, output_path, user_id, ms):
    """Advanced metadata function with individual field support"""
    try:
        await ms.edit("<i>I Found Metadata, Adding Into Your File ⚡</i>")
        
        # Get user's metadata settings
        user_data = find(user_id)
        metadata_enabled = user_data[2] if user_data and len(user_data) >= 3 else "Off"
        
        if metadata_enabled != "On":
            # Just copy the file without metadata
            command = [
                'ffmpeg', '-y', '-i', input_path, '-map', '0', '-c', 'copy', output_path
            ]
        else:
            # Get individual metadata fields
            title = get_title(user_id)
            author = get_author(user_id)
            artist = get_artist(user_id)
            audio_title = get_audio(user_id)
            subtitle_title = get_subtitle(user_id)
            video_title = get_video(user_id)
            
            # Build command with individual metadata
            command = [
                'ffmpeg', '-y', '-i', input_path, '-map', '0', '-c', 'copy',
                '-metadata', f'title={title}',
                '-metadata', f'author={author}',
                '-metadata', f'artist={artist}',
                '-metadata:s:a', f'title={audio_title}',
                '-metadata:s:s', f'title={subtitle_title}',
                '-metadata:s:v', f'title={video_title}',
                output_path
            ]
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
        
        if os.path.exists(output_path):
            await ms.edit("<i>Metadata Has Been Successfully Added To Your File ✅</i>")
            return output_path
        else:
            await ms.edit("<i>Failed To Add Metadata To Your File ❌</i>")
            return None
    except Exception as e:
        print(f"Error occurred while adding metadata: {str(e)}")
        await ms.edit("<i>An Error Occurred While Adding Metadata To Your File ❌</i>")
        return None

# Keep the legacy function for compatibility
async def add_metadata(input_path, output_path, metadata, ms):
    """Legacy function - uses single metadata value for all fields"""
    try:
        await ms.edit("<i>I Found Metadata, Adding Into Your File ⚡</i>")
        command = [
            'ffmpeg', '-y', '-i', input_path, '-map', '0', '-c:s', 'copy', '-c:a', 'copy', '-c:v', 'copy',
            '-metadata', f'title={metadata}',
            '-metadata', f'author={metadata}',
            '-metadata:s:s', f'title={metadata}',
            '-metadata:s:a', f'title={metadata}',
            '-metadata:s:v', f'title={metadata}',
            '-metadata', f'artist={metadata}',
            output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode().strip()
        t_response = stdout.decode().strip()
        
        if os.path.exists(output_path):
            await ms.edit("<i>Metadata Has Been Successfully Added To Your File ✅</i>")
            return output_path
        else:
            await ms.edit("<i>Failed To Add Metadata To Your File ❌</i>")
            return None
    except Exception as e:
        print(f"Error occurred while adding metadata: {str(e)}")
        await ms.edit("<i>An Error Occurred While Adding Metadata To Your File ❌</i>")
        return None
