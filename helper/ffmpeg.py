import time
import os
import asyncio
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser



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
    

async def add_metadata(input_path, output_path, metadata, ms, user_id=None):
    try:
        await ms.edit("<i>I Found Metadata, Adding Into Your File ⚡</i>")
        
        if user_id:
            # Get metadata from user's profile
            current_profile = get_current_profile(user_id)
            title = get_metadata_field_with_profile(user_id, "title", current_profile)
            author = get_metadata_field_with_profile(user_id, "author", current_profile)
            artist = get_metadata_field_with_profile(user_id, "artist", current_profile)
            audio = get_metadata_field_with_profile(user_id, "audio", current_profile)
            subtitle = get_metadata_field_with_profile(user_id, "subtitle", current_profile)
            video = get_metadata_field_with_profile(user_id, "video", current_profile)
        else:
            # Fallback to old metadata system
            title = author = artist = audio = subtitle = video = metadata
        
        command = [
            'ffmpeg', '-y', '-i', input_path, '-map', '0', '-c:s', 'copy', '-c:a', 'copy', '-c:v', 'copy',
            '-metadata', f'title={title}',
            '-metadata', f'author={author}',
            '-metadata:s:s', f'title={subtitle}',
            '-metadata:s:a', f'title={audio}',
            '-metadata:s:v', f'title={video}',
            '-metadata', f'artist={artist}',
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

