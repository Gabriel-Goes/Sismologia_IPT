from tensorflow.keras.models import load_model
import shap
import numpy as np
import matplotlib.pyplot as plt
import os


# Substitua isso com o caminho para seus arquivos .npy
# parse through the directory and get the npy files
# Dir is ./files/spectro/EVENTID/*.py
# there is thousands of EVENTID folders
# each EVENTID folder has some files
# each file is a numpy array
# each numpy array is a spectrogram

'''
Error : no such file or directory : 'file.npy'.
I am getting the error `no such file or directory : 'file.npy'` because the file is inside a folder. How do I get the path of the file inside the folder?
I am using the `os.walk` function to parse through the directory and get the files. The files are inside a folder. I am getting the error `no such file or directory : 'file.npy'` because the file is inside a folder. How do I get the path of the file inside the folder?
'''


# create an array of 100 spectrograms to input to shap.explainer
i = 0
print(' INICIO ')
for root, events, files in os.walk("./files/spectro/"):

    print(f'root = {root}')
    print(f'events = {events[:10]}')
    print(f'files = {files}')
    print('-----------------------------------')
    for event in events:
        print(f'event = {event}')
        if i == 100:
            break
        for spectro in os.listdir(os.path.join(root, event)):
            print(f'spectro = {spectro}')
            i += 1
            break
        break
    break

# load the model
model = load_model('./files/model/model_2021354T1554.h5')
