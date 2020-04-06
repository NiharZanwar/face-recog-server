# face-recog-server
## Steps to get docker up and running

* Clone this repository
        
        $ git clone https://github.com/NiharZanwar/face-recog-server.git
        $ cd face-recog-server/
        
* Build image - set <name_of_image> parameter as per your choice:

        $ cd face-recog-server/
        $ sudo docker build -t <name_of_image> .

* Check if image is successfully created

        $ sudo docker image ls
       check for the name_of_image in the list that is shown

* Now to run the container

        $ sudo docker run -d --restart always -p 8008:8008 -p 5005:5005 --name <name_of_container> -v absolute/path/for/data:/data <name_of_image>
    