# IAS-project
Image Analysis web application
Backend - FastApi
Frontend - React
## Environment Setup

### Use scripts
1. double click the start.sh file. This will download, build and run both the back-end and front-end.
2. To stop, press CTRL-C in the terminal that opened when you started the start.sh script, or close the terminal.
3. double click the stop.sh script. This will stop the back-end services.

If for some reason start.sh is not working it could be because a container or volume got corrupted.
Please run the reset.sh script and once that has finished running you can run start.sh again.

### Use docker compose
- Run the following command in the IAS-project folder to start all backend services
  ```sh
  # If this is the first time running this command it will take some time while the docker images are downloaded.
  # Future uses will be very fast.
  $ docker compose up
  ``` ( *** On ubuntu - use : docker-compose build, docker-compse up -d)
- To start a development version of the front end, please input the following commands.
  ```sh
  $ cd react
  
  # this will install all modules and could take some time
  $ npm install 
  
  # this will build and serve the project.
  $ npm start 
  ```
- [http://localhost:3000/]() to see the frontend


- [http://localhost:8000/docs]() to see the backend documentation


- [http://localhost:8081/devDB/]() to see the database

### Monitoring
To monitor the celery worker tasks / microservices. Go to [http://localhost:5555/]()
To monitor RabbitMQ, the message broker. Go to [http://localhost:15672/]()
And enter the username and password set in the celery_task.env file in ./env_files.
Default: 
- User: 'user'
- Password: 'password'


## License

Apache License 2.0

---
### Explanation about backend
- The backend was configurated as docker container
1. mainApi is fastAPI framework backend to provider api to the frontend ( ias-project-react-mainapi)
2. Database docker container ( mongo )
3. Backend database server container ( mongo-express ) 
4. Others are image processing module working as docker container.
So main point is to install docker environment as perfectly to prepare development environment.
- Backend Development Environment
Because the backend was configurated docker system. the development should be docker devcontainer.
For example - vscode docker environment (Remote Containers)
### Explanation about frontend
- The frontend was configurated with react.js
The gole is Viv viewer to display every images on frontend by using backend that customize image processing using ashlar python module.

- Detail Explanation about Frontend project structure and Data system.
 Main Page file is MainFrame.js 
 Descibe full page of the frontend and most skeleton was configured on this file , Should touch carefully and understand as fully.
 There are three parts called - left panel area, central panel area, right panel area
 1. Left Panel part + Right Panel Part
    Both parts are existed in /src/components/tabs
 2. Central Panel 
    Are existed in /src/viv/
    * This is important part in this project. 

*** This project structure is configured as perfectly and as well for image processing and viv viewer.

### About Azure: no longer used
Use Azure for server and link subscription to Microsoft Azure Sponsorship.
https://portal.azure.com/#home
ID: daisukekubota@outlook.jp
Pass : Kubo@0823

### About GCP
Current(24.10.2022) use GCP for server and link subscription google.
https://console.cloud.google.com/home/dashboard?project=capable-alcove-265511
ID: daisukekubota0823@google.com
Pass : Life@Analytics

To be able to operate on the following sites.
  - Project Name : LifeAnalytics
  - Vm instance : Compute Engine / Vm Instances / lifeanalytics-vm
  - External IP : 34.72.210.99
  - account name(ssh key account) : iasgcp
  - Reference File : gitaction workflow command - ssh_ci.yml
  
  
### About Web page
 - login page http://ias.lifeanalytics.org/
    