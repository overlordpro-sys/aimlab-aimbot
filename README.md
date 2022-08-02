# aimlab-aimbot
Using computer vision to hit targets in aim trainers

## The Failures
When coming up with this project, my original idea was to utilize machine learning. My original plan was to train an object detection model and then use reinforcement learning to determine how far to move the mouse. 

In order to get anywhere, I first had to train that model. In order to generate the training images, I recorded a video and wrote a Python script to output each individual frame as an image. After annotating each image in labelImg, I used a Python Jupyter notebook and the [TensorFlow Object Detection API](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/tf2.md) to train using those images. 

At this point, performance and accuracy were mediocre and I knew I would have to annotate many more images, each featuring three targets. In order to make it easier for myself, I wrote [a script](https://github.com/overlordpro-sys/tfod-auto-annotate) that would use my partially trained model to generate more annotated data. Although I still had to audit each image to make sure bounding boxes were placed correctly, it was still much faster than hand annotating thousands of images. 

After training over a few weeks, results seemed good.

![image](https://user-images.githubusercontent.com/64398319/182468155-601e5671-da00-4dfe-a780-2746f14ef67a.png)

To get real time predictions based on what was on my screen, I used OBS Virtual Camera. 
Now that I had a working model, I got started on how the script would receive feedback and output clicks. Because of how reinforcement learning works, I needed some way to provide positive feedback to the script. In AimLab, each time a target is hit, a hitsound is played. All I had to do to check for hits was to check for amplitude changes in the sound stream at a very high rate. Regarding the mouse, many mouse control methods I found didn't work and couldn't look around using the camera. Fortunately, one method, using win32api, still worked and could move the crosshair around in game.

The next step was to use the information output by the object detection model and to move the mouse to that location. To achieve this, I used SB3 (Stable Baselines 3)  and a custom OpenAI Gym environment. Creating a custom environment was relatively simple due to documentation SB3 provides. 




During last month setup and trained meh model for targets with a pretrained coco model, low accuracy
5.7.22 wrote python file to autoannotate images using the already trained model. Now do not have to hand annotate for more training data. Started training a new model with only config, no pretrained model. Will see how it will go. Will use to resume from checkpoint after training finishes. 

## The Solution
