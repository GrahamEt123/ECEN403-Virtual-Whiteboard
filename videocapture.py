import cv2 as cv 
import mediapipe as mp
import pyautogui as pag
#import mouse
import numpy as np
import math
import random 
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from time import *

# This function is to guage the accuracy of the model
def accuracyTest(frames,model_x, model_y,image_height, image_width):
  count = 0
  state = True
  x = random.randint(0,image_width)
  y = random.randint(0,image_height)
  cv.circle(frames, (x,y), 50 , (0,0,0), -1)
  # calculate deviation from drawn circle
  deviation = math.sqrt(abs(model_x - (x+5))**2 + abs(model_y - (y+5))**2)
  if deviation < 10:
    count += 1
  print (deviation)

# def gestureRecognizer(frames):
#   base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
#   options = vision.GestureRecognizerOptions(base_options=base_options)
#   recognizer = vision.GestureRecognizer.create_from_options(options)
#   results = []
#     # STEP 4: Recognize gestures in the input image.
#   recognition_result = recognizer.recognize(frames)
#   print(recognition_result)


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# For static images:
# static image function lets you control how mediapipe will reagard inputs
# when false it regards inputs as a stream or video where they are related
# when false it takes every input as an uncorrelated picture

# For webcam
e1 = 0
e2 = 0
pos_x = 300
pos_y = 300
start = time()
passes = 0
tests = 0
accuracy = ''
posList = []
late = ''
accuracyList = []
cap = cv.VideoCapture(0)
with mp_hands.Hands( # similar to a struct in c++. It holds all the data that the model will use to set its running state
  static_image_mode = False,
  model_complexity = 1,
  min_detection_confidence=0.5,
  min_tracking_confidence=0.5,
  max_num_hands = 1) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
    
      continue
#################################
    if_pos_x = 0
    if_pos_y = 0
    mf_pos_y = 0
    mf_pos_x = 0
    image.flags.writeable = False
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    image = cv.flip(image,1)
    results = hands.process(image)
    #print('Handedness:', results.multi_handedness)
    if not results.multi_hand_landmarks:
      results.multi_hand_landmarks = range(0)
    image_height, image_width, _ = image.shape
   #annotated_image = image.copy()
    e1 = cv.getTickCount()
    for hand_landmarks in results.multi_hand_landmarks:
      #print('hand_landmarks:', hand_landmarks)
      #print(
        #f'Mid finger tip coordinates: (',
        #f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y *image_height}, '
        #f' {hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * image_height})'
        #)
        
      if_pos_x = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width)
      if_pos_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height)
      mf_pos_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y * image_height
      mf_pos_x = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].x * image_width
      
      #rf_pos_y = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y * image_height
      #rf_pos_x = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x * image_width
    
      
      if if_pos_y <= mf_pos_y:
        #posList.append((if_pos_x,if_pos_y))
        pag.moveTo(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x *image_width,
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height, _pause=False)
      if if_pos_y < mf_pos_y:
        pag.mouseDown(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x *image_width,
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height,
        button = 'left', _pause = False)
        
      if mf_pos_y < if_pos_y: 
        pag.mouseUp(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x *image_width,
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height,
        button = 'left', _pause = False)
        
      if not results.multi_hand_world_landmarks:
        continue
    #draw hand annotations on image
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
          image,
          hand_landmarks,
          mp_hands.HAND_CONNECTIONS,
          mp_drawing_styles.get_default_hand_landmarks_style(),
          mp_drawing_styles.get_default_hand_connections_style())
    #for position in posList:
    # accuracy test 
    cv.circle(image, (pos_x,pos_y), 15, (0,0,0), -1)
    e2 = cv.getTickCount()
    #start = 0
    #time() - start > 10 or
    if (if_pos_x <= pos_x + 10 and if_pos_x >= pos_x - 10 and if_pos_y <= pos_y + 10 and if_pos_y >= pos_y - 10 or time() - start > 5):
      if (if_pos_x <= pos_x + 10 and if_pos_x >= pos_x - 10 and if_pos_y <= pos_y + 10 and if_pos_y >= pos_y - 10 ):
        passes += 1
      pos_x = random.randint(0,image_width-100)
      pos_y = random.randint(0,image_height-100)
      
      start = time()
      tests += 1
      #print (time())
    if (tests > 5): 
      accuracy = str(round((passes/tests) * 100)) + "%" + " accuracy"
      accuracyList.append(accuracy)
    latency = (e2-e1)/(cv.getTickFrequency())    # latency calculations and output
    late = "Latency test: " + str(round(latency*1000,2)) + " ms"
    cv.putText(image,accuracy,(900,50), cv.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.5,(0,0,0),1,cv.LINE_AA)
    cv.putText(image,late,(900,70), cv.FONT_HERSHEY_SCRIPT_SIMPLEX, 0.5,(0,0,0),1,cv.LINE_AA)

    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    cv.imshow('Mediapipe Hands', image)
    
    
    #deviation = math.sqrt(abs(if_pos_x - (pos_x+5))**2 + abs(if_pos_y - (pos_y+5))**2)
    #print(passes)
    #print(tests)
    #print(str(round(time*1000,2)))
    #accuracyTest(image, if_pos_x , if_pos_y,image_height=50, image_width=50)
    #gestureRecognizer(image)
    if cv.waitKey(1) == ord('q'):
     break

cap.release()












      