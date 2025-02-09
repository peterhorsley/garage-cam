import cv2
import time
import datetime
import requests

# URL of the RTSP stream
rtsp_url = "rtsp://192.168.1.10:8554/garage"
controller_url = "http://192.168.1.94/jc"

win_name = 'Garage Cam'
cv2.namedWindow(win_name, flags=cv2.WINDOW_GUI_NORMAL|cv2.WINDOW_AUTOSIZE)
cv2.moveWindow(win_name, 0, 0)
fixed_width = 400

running = True
while running:
  try:

    print("opening video capture")
    # Create a VideoCapture object
    cap = cv2.VideoCapture(rtsp_url)
    initialized = False

    # Check if the stream is opened correctly
    if not cap.isOpened():
      raise Exception("Error: Could not open video stream.")
    else:
      cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Experiment with different buffer sizes
      counter = 0
      door_text = ''
      door_color = (255, 255, 255)
      while True:
        # Read one frame
        ret, frame = cap.read()

        if ret:
          counter += 1
          # Get current dimensions
          height, width = frame.shape[:2]
          
          # Calculate the proportional height
          ratio = fixed_width / width
          new_height = int(height * ratio)
          
          # Resize the frame
          frame = cv2.resize(frame, (fixed_width, new_height), interpolation=cv2.INTER_AREA)
                  
          timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          cv2.putText(frame, timestamp, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
          
          if not initialized or counter > 100:
            initialized = True
            counter = 0
            door_open = None
            door_text = ''
            try:
                # Make the GET request
                response = requests.get(controller_url)
                
                # Check if the response status code is 200
                if response.status_code == 200:
                    # Parse JSON response
                    json_data = response.json()
                    door_open = json_data['door'] == 1
            except Exception as e:
                print("Failed to get door status: " + str(e))
                door_text = 'UNKNOWN'
                door_color = (255, 0, 0)
                        
            if door_open != None:
              door_text = 'DOOR OPEN' if door_open else 'DOOR SHUT'
              door_color = (0, 255, 0) if door_open else (255, 216, 0)
          
          cv2.putText(frame, door_text, (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, door_color, 2, cv2.LINE_AA)
            
          cv2.imshow(win_name, frame)
          if cv2.waitKey(1) >= 0:
            running = False
            break
        else:
          raise Exception("Failed to grab frame")
  except Exception as ex:
    print("Error: " + str(ex))
    if cap:
      cap.release()
    time.sleep(3)

# When everything is done, release the capture
if cap:
  cap.release()

cv2.destroyAllWindows()
