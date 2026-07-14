import os
import subprocess
from gtts import gTTS
import imageio_ffmpeg

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Telugu Narration Scripts
SCENES_TELUGU = [
    {
        "id": 1,
        "image": "scene_1.png",
        "text": "అది ఒక ఇంజనీరింగ్ కాలేజీ ఉదయం. కబీర్ చూపులు ఎప్పుడూ జారా వైపే ఉండేవి. జారా కూడా అది గమనించినా, ఏమీ మాట్లాడకుండా సైలెంట్‌గా ఉండేది."
    },
    {
        "id": 2,
        "image": "scene_2.png",
        "text": "కంప్యూటర్ ల్యాబ్‌లో జారా కోడింగ్ చేస్తుంటే కబీర్ చూశాడు. జారా కూడా తనని గమనించినా, ఏమీ మాట్లాడకుండా తలదించుకుంది."
    },
    {
        "id": 3,
        "image": "scene_3.png",
        "text": "లైబ్రరీలో కబీర్ చదువుతున్నట్లు నటిస్తూ జారాను చూశాడు. జారా కూడా అది గమనించినా, ఇద్దరూ ఏమీ మాట్లాడుకోలేదు."
    },
    {
        "id": 4,
        "image": "scene_4.png",
        "text": "కాలేజీ అయిపోయాక జారా నడుస్తూ వెళ్తోంది. వెనుక కబీర్ వస్తున్నట్లు ఆమె గమనించినా, ఏమీ తెలియనట్లు నడుస్తూ వెళ్ళిపోయింది."
    },
    {
        "id": 5,
        "image": "scene_5.png",
        "text": "చెప్పలేని ప్రేమ ఒక మధురమైన జ్ఞాపకం. ఒకరికొకరు గమనించుకున్నా, ఇద్దరూ ఏమీ మాట్లాడుకోలేదు."
    }
]

def generate_telugu_voiceover():
    print("=== Generating Telugu Voice-Over Audio Clips via gTTS ===")
    for scene in SCENES_TELUGU:
        mp3_path = os.path.join(ASSETS_DIR, f"scene_{scene['id']}_te.mp3")
        wav_path = os.path.join(ASSETS_DIR, f"scene_{scene['id']}_te.wav")
        text = scene["text"]
        print(f"Generating Scene {scene['id']} Telugu audio...")
        
        tts = gTTS(text=text, lang="te", slow=False)
        tts.save(mp3_path)
        # Convert mp3 to wav via ffmpeg
        cmd = [FFMPEG_EXE, "-y", "-i", mp3_path, "-ar", "44100", "-ac", "2", wav_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
        print(f"  -> Generated {wav_path}")

def get_audio_duration(file_path):
    cmd = [FFMPEG_EXE, "-i", file_path]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in res.stderr.split('\n'):
        if "Duration:" in line:
            dur_str = line.split("Duration:")[1].split(",")[0].strip()
            parts = dur_str.split(":")
            return float(parts[0])*3600 + float(parts[1])*60 + float(parts[2])
    return 6.0

def format_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def assemble_telugu_video():
    print("=== Assembling Telugu Video and SRT Subtitles ===")
    
    current_time = 0.0
    pause_after_scene = 2.5
    
    srt_lines = []
    concat_txt_path = os.path.join(ASSETS_DIR, "slides_te.txt")
    audio_concat_txt = os.path.join(ASSETS_DIR, "audios_te.txt")
    
    silence_path = os.path.join(ASSETS_DIR, "silence.wav")
    
    with open(concat_txt_path, "w", encoding="utf-8") as f_slides, \
         open(audio_concat_txt, "w", encoding="utf-8") as f_audios:
         
        for idx, scene in enumerate(SCENES_TELUGU):
            wav_path = os.path.join(ASSETS_DIR, f"scene_{scene['id']}_te.wav")
            dur = get_audio_duration(wav_path)
            slide_dur = dur + pause_after_scene
            
            img_path = os.path.join(ASSETS_DIR, scene['image'])
            f_slides.write(f"file '{img_path}'\n")
            f_slides.write(f"duration {slide_dur:.3f}\n")
            
            f_audios.write(f"file '{wav_path}'\n")
            f_audios.write(f"file '{silence_path}'\n")
            
            start_t = current_time + 0.2
            end_t = current_time + dur + 1.0
            
            srt_lines.append(f"{idx+1}")
            srt_lines.append(f"{format_srt_time(start_t)} --> {format_srt_time(end_t)}")
            srt_lines.append(scene["text"])
            srt_lines.append("")
            
            current_time += slide_dur
            
        last_img = os.path.join(ASSETS_DIR, SCENES_TELUGU[-1]['image'])
        f_slides.write(f"file '{last_img}'\n")
        
    srt_path = os.path.join(ASSETS_DIR, "love_story_telugu.srt")
    with open(srt_path, "w", encoding="utf-8") as f_srt:
        f_srt.write("\n".join(srt_lines))
    print(f" -> Generated Telugu Subtitles at {srt_path}")
    
    master_voice_path = os.path.join(ASSETS_DIR, "master_voice_te.wav")
    subprocess.run([
        FFMPEG_EXE, "-y", "-f", "concat", "-safe", "0", "-i", audio_concat_txt,
        "-c", "copy", master_voice_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    bgm_path = os.path.join(ASSETS_DIR, "romantic_background.wav")
    final_mp4 = os.path.join(ASSETS_DIR, "love_story_telugu.mp4")
    
    print(" -> Running FFmpeg final render (Slides + Telugu Voice + BGM)...")
    cmd = [
        FFMPEG_EXE, "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt_path,
        "-i", master_voice_path,
        "-stream_loop", "-1", "-i", bgm_path,
        "-filter_complex",
        "[1:a]volume=1.0[voice];[2:a]volume=0.22[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[audio]",
        "-map", "0:v", "-map", "[audio]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "30",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest", final_mp4
    ]
    subprocess.run(cmd, check=True)
    print(f" -> SUCCESSFULLY GENERATED TELUGU VIDEO: {final_mp4}")

if __name__ == "__main__":
    generate_telugu_voiceover()
    assemble_telugu_video()
