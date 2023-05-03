from django.shortcuts import render,redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings
import requests
import os,uuid
import random,string
import speech_recognition as sr
from pydub import AudioSegment
from .models import Video
import json
import aiohttp
import io
import pafy,base64
import time
import moviepy.editor as mp
from pytube import YouTube
from django.http import JsonResponse
# Create your views here.
def home_page(request):
    return render(request,'myapp/index.html')

@csrf_exempt
def show_result(request):
    # some code to generate context data
   
    return render(request,'myapp/transcription_result.html')



@csrf_exempt
def download_video(request):
    data=json.loads(request.body)
    video_url=data['video_url']
    is_file=data['file']
    print(video_url)
    print(is_file)
    if is_file:
        video_data = base64.b64decode(video_url)
        filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + '.mp4'
        filepath = os.path.join(settings.BASE_DIR,'temp', filename)
        with open(filepath, 'wb') as f:
            f.write(video_data)
        text=convert_to_audio(filename)
        video = Video()
        video.video_url = video_url
        video.created_at = timezone.now()
        video.transcript = text
        video.save()
        return JsonResponse({'data':text})

    else:
        i = 0
        video = None
        text = None
        result = "Video Cannot be Parsed, Please try again"
        while i < 100:
            i += 1
            print(i)
            try:
                video = YouTube(video_url) 
                stream = video.streams.get_highest_resolution()
                filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + '.mp4'
                stream.download(os.path.join(settings.BASE_DIR,'temp'),filename=filename)
                text=convert_to_audio(filename)
                video = Video()
                video.video_url = video_url
                video.created_at = timezone.now()
                video.transcript = text
                video.save()
                return JsonResponse({'data':text})
            except:
                try:
                    stream = video.streams.filter(progressive=True).order_by('resolution').first()
                    filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + '.mp4'
                    stream.download(os.path.join(settings.BASE_DIR,'temp'),filename=filename)
                    text=convert_to_audio(filename)
                    result=text
                    video = Video()
                    video.video_url = video_url
                    video.created_at = timezone.now()
                    video.transcript = text
                    video.save()
                    return JsonResponse({'data':text})
                except:
                    time.sleep(1)
                 
        context = {'data': result}
        return JsonResponse({'data':'video cannot be parsed, please try again'})



# def download_video(video_url):

#     video_filename = os.path.join(settings.BASE_DIR, 'temp', 'video2.mp4')
#     r = requests.get(video_url, stream=True)
#     print(2)
#     with open(video_filename, 'wb') as f:
#         for chunk in r.iter_content(chunk_size=1024):
#             if chunk:
#                 f.write(chunk)
#     print(3)
#     print(video_filename)
#     return video_filename

def download_audio(audio_url):
    r = requests.get(audio_url)
    return io.BytesIO(r.content)

    


def convert_to_audio(filename):
    video_file_path = os.path.join(settings.BASE_DIR,'temp', filename)
    audio_filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + '.wav'
    audio_file_path = os.path.join(settings.BASE_DIR,'temp', audio_filename)
    print(video_file_path)
    print(audio_file_path)
    # Convert video to audio using ffmpeg
    sound = AudioSegment.from_file(video_file_path)
    sound.export(audio_file_path, format="wav")

    # Return the audio file as a response
    with open(audio_file_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='audio/wav')
        response['Content-Disposition'] = 'attachment; filename=example_audio.wav'
        text=print_transcribe(audio_filename)
        print("transribed:",text)
        return text


@csrf_exempt
def print_transcribe(filename):
    # get path of the audio file
    audio_path = os.path.join(settings.BASE_DIR,'temp',filename)
    print(audio_path)
    sound=AudioSegment.from_file(audio_path)
    sound=sound.high_pass_filter(1000)
    sound=sound.low_pass_filter(1000)
    audio_filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)) + '.wav'
    audio_path = os.path.join(settings.BASE_DIR,'temp',audio_filename)
    sound.export(audio_path,format="wav")
    # create a recognizer instance
    r = sr.Recognizer()

    # open the audio file using the recognizer
    with sr.AudioFile(audio_path) as source:
        # read the entire audio file
        audio = r.record(source)

    # transcribe the audio using Google Speech Recognition
    try:
        text = r.recognize_google(audio)
    except sr.UnknownValueError:
        text = "Could not understand audio"
    except sr.RequestError as e:
        text = "Could not request results from Google Speech Recognition service; {0}".format(e)

    # print the transcribed text
    print("transcribe:",text)
    
    # return the transcribed text as a response
    return text
