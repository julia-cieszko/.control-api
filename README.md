# .control - A smart tool supporting melanoma diagnosis
[.Control](https://github.com/julia-cieszko/.control/tree/master) is an application for scoring benigns as malignant or not and therefore supporting early diagnosis of melanoma based on CNN trained on open datasets of ISIC.
This repository is a part of .control app project. For detailed description of different modules and technologies, check the [main repository](https://github.com/julia-cieszko/.control/tree/master).

## What's in this repository?
This API is used to serve the trained AI model as an endpoint and recieves images to be analyzed from the mobile application. After performing analysis this application stores the recieved image in Firebase Storage and sends the result of the analysis to Firebase Firestore and upon completion notifies the mobile app that the process is over.
