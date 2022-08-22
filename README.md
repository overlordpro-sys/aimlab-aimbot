# aimlab-aimbot
AimLab aim training software is designed to improve a player's reflexes and accuracy in games like [Fortnite](https://www.epicgames.com/fortnite/en-US/home).  I thought it would be interesting to have a robot take the place of a human being trained - just because.

## The Failures
My original idea was to utilize machine learning. The plan was to train an object detection model and then use reinforcement learning to determine how far to move the mouse. 

Model training was the first order of business.  In order to generate the training images, I recorded an AimLab session and wrote a Python script to output each individual frame as an image. After annotating each image in [labelImg](https://blog.roboflow.com/labelimg/#:~:text=What%20is%20LabelImg%3F,your%20next%20object%20detection%20project), I used the [TensorFlow Object Detection API](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2.md) to train using those images. This was done in a Python Jupyter notebook.

At this point, performance and accuracy were mediocre.  I knew I would have to annotate many more images, with each image having three targets to annotate. In order to make it easier for myself, I wrote [a script](https://github.com/overlordpro-sys/tfod-auto-annotate) that would use my partially trained model to generate more annotated data. Although I still had to audit each image to make sure bounding boxes were placed correctly, it was still much faster than hand annotating thousands of images. 

Results seemed good after a few weeks of training.

![image](https://user-images.githubusercontent.com/64398319/182468155-601e5671-da00-4dfe-a780-2746f14ef67a.png)

I used OBS Virtual Camera to get real time coordinates for each target. A script then converted each read frame into a numpy array and passed it into the model. The reported center of each target was then the calculated center of each bounding box. 

Feedback and clicking was much easier. Because of how reinforcement learning works, I needed some way to provide positive feedback to the script. In AimLab, a sound is played each time a target is hit. Thus, the program detects the associated amplitude changes in the sound stream in real-time. As for mouse control, while many methods seemed available only [win32api](https://www.delftstack.com/howto/python/python-win32api/) was viable.  This enabled the ML model to autonomously move the crosshair around in game.

The reinforcement learning section was next now that I had basic I/O and the necessary mechanisms for a model to sense and interact with its environment. To achieve this, I used (Stable Baselines3)[https://github.com/DLR-RM/stable-baselines3] and a custom OpenAI Gym environment. Creating a custom environment was relatively simple due to the excellent SB3 documentation. 

After finishing everything, it was finished! But not really. 

## What Worked

There were a couple significant issues. The worst was the object detection model. Even after training, the model was extremely inaccurate at times. This was most likely due to how dynamically the targets' backgrounds changes during training. Furthermore, the model was far too slow for what I was aiming for: a fast and accurate aimbot.  

![ezgif com-gif-maker (5)](https://user-images.githubusercontent.com/64398319/182521148-778dd34a-0d58-473d-9bcc-d8bb1050c2d4.gif)

Then I remembered something I had seen about using grayscale images and a threshold for computer vision.  I could easily do this using (cv2)[https://pypi.org/project/opencv-python/]. 

A read frame is converted into grayscale then thresholded. After that, I can use (cv2.findContours)[https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html] and cv2.moments to find the center of each target. I also changed to using (mss)[https://python-mss.readthedocs.io/examples.html] for frame capture.  This ran much faster than prior methods. After changing the wall colors to black, the targets to white, and adjusting the threshold, I was able to significantly accelerate the how fast targets could be detected. To better present results for visualization, the program uses cv2 draw a large green circle at the returned coordinates. 

The program runs sufficiently fast that it is as smooth as the original stream.  Please excuse the stuttery gif animation, however; the video to gif converter used for this animation is limited to just 30 fps.

![ezgif com-gif-maker (6)](https://user-images.githubusercontent.com/64398319/182525392-f6df306b-02fd-4adb-872d-92ddc8f800f1.gif)

Now, I still had an issue. Even with the speed increase the reinforcement learning aspect was still unsatisfactory.  As model training was done on a real time game, vectorized environments could not be used; training was relatively slow. Even after running it for a few nights, I was unable to achieve any significant progress. The model was not advancing through many training rounds at all.

I decided to try something else. Overall, it was probably best that I did not end up using a reinforcement learning agent for this.  The same computer probably would not likely have fallen behind at runtime as well. 

I decided to try the simplest approach. The idea was to subtract the coordinates for the center of my screen (960, 540) from the coordinates of the center of the target closest to the crosshair. This would give me the coordinate of the target relative to the middle of the screen. For example, if the closest target was a coordinate to the left, my relative coordinate would be in terms of (-x, +/- y). However, Aimlab allows the user to input their mouse sensitivity for another game in order to give the same experience as aiming in the game itself. In my Aimlab settings, I had my sensitivity set to a custom value, 0.32 for the game Valorant. Due to this, the script was not moving the mouse far enough to hit the target. To accomodate this, I tested multiplying the relative values by a scalar. 

When doing this, I found that the script was undershooting closer targets and overshooting further targets. To accomodate this I increased the multiplier for lower values and increased the multipler for higher values:

```   
if abs(relx) < 50:
        scalarx = 3.35
elif abs(relx) < 100:
        scalarx = 3.3
elif abs(relx) < 200:
        scalarx = 3.22
elif abs(relx) < 400:
        scalarx = 3.15
else:
        scalarx = 3.00
        
if abs(rely) < 50:
        scalary = 3.35
elif abs(rely) < 100:
        scalary = 3.3
elif abs(rely) < 200:
        scalary = 3.22
elif abs(relx) < 400:
        scalary = 3.15
else:
        scalary = 2.90
```
I did notice that multiplying my adjusted scalar values (~3) by my sensitivity (.32) was about 1, so I tried removing my multipliers and setting my in-game sensitivity to 1. This almost worked but the script still missed on targets that were further away. 

Using the multipliers above, everything worked. In this video, you can see how quickly and accurately the script was able to hit the targets. 

https://user-images.githubusercontent.com/64398319/182534633-55d006c6-e0b9-42f5-be83-bedec25ff857.mp4

# Conclusion

At the beginning, I intended to entirely rely on machine learning for this project. However, over its course, I learned that sometimes simpler is better. Machine learning is not always the best for every situation. However, it was a really interesting experience seeing my object detection model come together. One thing I may try in the future is using a neural network to replace the scalars I used for moving the mouse. Overall, this project was a very fun project and I'm very happy with how it turned out.

I have uploaded both what didn't work and what did work as reference for myself in the future. 
