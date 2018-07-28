# remove exited containers:
sudo docker ps --filter status=dead --filter status=exited -aq | xargs -r docker rm -v
    
# remove unused images:
sudo docker images --no-trunc | grep '<none>' | awk '{ print $3 }' | xargs -r docker rmi

# stragglers
sudo docker image prune -a
sudo docker container prune --filter "until=72h"
sudo docker volume prune
sudo docker network prune --filter "until=72h"

#spin up your docker images and run streamiot app
#sudo docker build --no-cache -t streamiot_mvp_1
docker-compose down --remove orphans



#
sudo ln -sf `pwd`/fednode.py /usr/local/bin/fednode

#start up streamiot fednode full master
fednode install full master

# start up the streamiot node
sudo docker-compose.streamiot.yml build
sudo docker-compose.streamiot.yml up
