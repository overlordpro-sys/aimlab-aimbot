# aimlab-aimbot
Using computer vision to hit targets in aim trainers

## The Failures
When coming up with this project, my original idea was to utilize machine learning. My original plan was to train an object detection model and then use reinforcement learning to determine how far to move the mouse. 

In order to get anywhere, I first had to train that model. In order to generate the training images, I recorded a video and wrote a Python script to output each individual frame as an image. After annotating each image in labelImg, I used a Python Jupyter notebook and the [TensorFlow Object Detection API](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2.md) to train using those images. 

At this point, performance and accuracy were mediocre and I knew I would have to annotate many more images, each image having three targets to annotate. In order to make it easier for myself, I wrote [a script](https://github.com/overlordpro-sys/tfod-auto-annotate) that would use my partially trained model to generate more annotated data. Although I still had to audit each image to make sure bounding boxes were placed correctly, it was still much faster than hand annotating thousands of images. 

After training over a few weeks, results seemed good.

![image](https://user-images.githubusercontent.com/64398319/182468155-601e5671-da00-4dfe-a780-2746f14ef67a.png)

To get real time coordinates for each target, I used OBS Virtual Camera. I converted each read frame into a numpy array and passed into the model. Afterwards, I simply averaged out the x and y values of each bounding box to obtain the center of each target. 

Feedback and clicking was much easier. Because of how reinforcement learning works, I needed some way to provide positive feedback to the script. In AimLab, each time a target is hit, a hitsound is played. All I had to do was to check for amplitude changes during the hitsound in the sound stream at a very high rate. Regarding the mouse, many mouse control methods I found didn't work and couldn't look around using the camera. Fortunately, one method, using win32api, still worked and could move the crosshair around in game.

Now that I had basic I/O working, the reinforcement learning section was next. To achieve this, I used SB3 (Stable Baselines 3)  and a custom OpenAI Gym environment. Creating a custom environment was relatively simple due to documentation SB3 provides. 

After finishing everything, it was finished! But not really. 

## The Solution

There were a couple significant issues. The worst was the object detection model. Even after training, the model was extremely unaccurate at times. This was most likely due to how the targets' backgrounds changed during training due to their different positions in each image. Furthermore, the model was far too slow for what I was aiming for: a fast and accurate aimbot.  

![ezgif com-gif-maker (5)](https://user-images.githubusercontent.com/64398319/182521148-778dd34a-0d58-473d-9bcc-d8bb1050c2d4.gif)

And then I remembered something I had seen about using grayscale images and a threshold for computer vision. Using cv2, I could easily do this. After reading a frame, it is converted into grayscale and thresholded. After that, I can use cv2.findContours and cv2.moments to find the center of each target. I also changed my method of capturing a frame and used mss, which supposedly is the fastest way to capture an image of the screen. After changing the wall colors to black, the targets to white, and adjusting the threshold, I was able to significantly accelerate the how fast targets could be detected. To illustrate the coordinates, I had cv2 draw a large green circle at the returned coordinates. 
Unfortunately, I couldn't get what I was using to convert the video to a gif to output at more than 30 fps, but I was able to run the program fast enough to the point where it looked just as smooth as the original.

![ezgif com-gif-maker (6)](https://user-images.githubusercontent.com/64398319/182525392-f6df306b-02fd-4adb-872d-92ddc8f800f1.gif)

However, I still had an issue. Even with the speed increase, I still had issues with the reinforcement learning aspect. Because I had to train the model on a real time game and couldn't use vectorized environments, training was relatively slow. Even after running it for a few nights, I was unable to achieve any significant progress. I decided to try something else. Overall, it was probably best that I didn't end up using a reinforcement learning agent for this, as it would have slowed down run time. 

I decided to try the simplest approach. The basis for my approach was to subtract the coordinates for the center of my screen (960, 540) from the coordinates of the center of the target closest to the crosshair. After that I tested multiple scalars until the script wasn't under or over aiming anymore. For some reason though, the scalar needed to hit the target wait

