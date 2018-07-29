

###docker-compose ps # lists all services (id, name)
#33docker-compose stop <id/name> #this will stop only the selected container
###docker-compose rm <id/name> # this will remove the docker container permanently 
###docker-compose up # builds/rebuilds all not already built container 

# start up the streamiot node
sudo docker-compose -f docker-compose.streamiot.yml  up --build
