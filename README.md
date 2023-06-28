Twitter-Database Management System

Helps you make task-boards for projects so your team can create, share and manage tasks easily.

Note: This is a cloud application based on Google App Engine. A working Google cloud account is required to run this application. Also, This app doesnot require you to pay for cloud services. Follow the steps below to setup a free Google App Engine project to run this app.

Leave a message if you are having problems and need any help at abinbaby96@gmail.com

Requirements Python 3.8 Google-App-Engine SDK Google Cloud Project Cloud Datastore Firebase Authentication Installing Google App Engine SDK Go to following link: https://cloud.google.com/sdk/docs/install

The instruction in following lines are for Windows. If you have any other operating system follow the instruction on the page.

Under Windows tab, download the Google Cloud CLI Installer Once downloaded, install.bat will run automatically During installation, it will ask following questions Do you want to help improve the Google Cloud SDK? (your answer is N) Modify your profile to update your $PATH and enable shell command completion (your answer is Y) If asked (Enter a path to an rc file to update, or leave blank to use [default] ) -> (accept the default) Once done, it will give you a GCloud console similar command prompt Run the following commands in Cloud shell to install app-engine-python and app-engine-python-extras gcloud components install app-engine-python app-engine-python-extras

Setting up free App Engine Project Go to following link and signin with google account if necessary https://console.cloud.google.com/

Go to the option to add a new project and give it a name. Without modifying the location, hit create. Once the project is created then you should see it in the dashboard. Go to the hamburger menu on the top left (the three horizontal lines denoting a menu) and under “Serverless” click on “App Engine” don’t go into the sub menu here.

Click on the button “Create Application”. Choose your region. (Mine is europe west for Ireland). Click Next. Language should be “python” and the environment should be “standard”. Your app engine project is now setup.

Setting up cloud datastore to save data Go to following link and signin with google account if necessary https://console.cloud.google.com/

Go to the hamburger menu on the top left and under “Databases” click on “Datastore”, don’t go into the submenu.

If you see "Your database is ready to go. Just add data" and on top right "Cloud Firestore in Datastore mode" than its perfect. We are done. If instead you get a page asking you to create a datastore in either “Native mode” or “Datastore mode” click “Datastore mode” and you should get to the page described in the first bullet point. Next, On the hamburger menu in the submenu for “IAM & Admin” click “Service accounts”

Click on the single account and under name it shows “App Engine default service account” and do following:

Click on keys on top Under "add key" click "Create new key" Select JSON key type and create Download JSON file and rename it datastore.json place it one directory before this project This JSON file links this application to datastore. Before you run this application in your command line you will need to set the session variable GOOGLE_APPLICATION_CREDENTIALS with the location of this JSON file. In my case I have the JSON file above the directory of this project runs in so I would run the following command to set that session variable

set GOOGLE_APPLICATION_CREDENTIALS=..\datastore.json

note ".." means one directory before

Thats it, The application is linked to your cloud account's datastore. Now whatever happens in the app... the data gets stored in your datastore.

Setting up firestore authentication for user logins Go to the following URL: https://console.firebase.google.com/u/0/

Click “Add project” under “Your Firebase Projects” It should pop up a dialog with the message “Add firebase to one of your existing Google Cloud projects” Select your cloud project created above in the beginning and click continue and continue again Disable Google Analytics for the project and click "Add Firebase" Once created click "Conitnue" again Next, On the left click “Authentication” then “Get started” In the list of “Sign-in providers” enable “Email/password”. Click on the gear icon above "Authentication" than click "..." than click an icon that looks like html tag "</>". Finally, Give the app a name and do not check the box for firebase hosting. After clicking “Create” you will then click the option “Use a <script> tag” and take a copy of the template code provided there and fill in the details in the lines below.

In application folder, open the file following the path ../static/app-setup.js

This file includes a code like this

var firebaseConfig = { apiKey: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", authDomain: "xxxxxxxxxxxxxx.firebaseapp.com", projectId: "xxxxxxxxxxxxxxxxxx", storageBucket: "xxxxxxxxxxxxxxxx.appspot.com", messagingSenderId: "xxxxxxxxxxxxxxxxx", appId: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" }; Just copy paste your firebase details you got in the code and your are good to go. Datastore is attached to your Application.

Leave a message if you are having problems and need any help at abinbaby96@gmail.com
