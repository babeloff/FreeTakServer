# Docker Quickstart

> [!WARNING]
> **THIS IS NOT WELL SUPPORTED BY THE FTS TEAM RIGHT NOW, 
> YOU ARE IN UNCHARTED TERRITORY**

I'd like to set this repo up to use github actions to push to pip and docker hub at the same time.
Until that happens, here's how you can build and use this repo to build a docker image and run a container from it.
It assumes you've already cloned it where you plan to use it.
It _also_ means you'll be running whatever's in development,
_not_ what's been released / in Pypi. 

> [!WARNING]
> **That means you might be running unreleased code with this method**

## Persistence
By default, docker will save pretty much nothing between runs of this container.
So before we run this, we _really_ want somewhere for FreeTAKServer to store data.
This container expects you to mount that volume at `/opt/fts/` inside the container.
Let's put this in your home directory, for now. 

This should work for all dockers, linux, windows, etc.
```shell
docker volume create fts_data 
```

> [!WARNING]
> FTS will store its database, data packages, ExCheck lists, and importantly, 
> your _certificates_ in this volume. Keep all of these safe. 

## Creating a docker image from this repo.
```shell
docker build . -t fts:local
```
| Arg       | Description                                          |
|-----------|------------------------------------------------------|
| build .   | build the container image using the local Dockerfile |
| fts:local | the container image name                             |  


## Run the container
OK, there's a lot to put in this command line,
because there's lots of options we want to pass.

| Arg                                              | Description                                                 |
|--------------------------------------------------|-------------------------------------------------------------|
| run -it                                          | run the container interactively (hold the shell open)       |
| -e FTS_DP_ADDRESS "$(curl ifconfig.me)"          | dynamically get your address for data-packages (using curl) |
| --mount type=bind,src=fts_data,target=~/fts_data | mount the volume for persistent data                        |
| -p 8080:8080                                     | expose Data Package port                                    |
| -p 8087:8087                                     | expose Cursor on Target (CoT) port                          |
| -p 8443:8443                                     | expose SSL Data Package port                                |
| -p 9000:9000                                     | expose Federation ports                                     |
| -p 19023:19023                                   | expose API port. Use with caution                           |
| --name fts-node-1                                | it is a good practice to name the container                 |
| fts:local                                        | the container image for docker to run                       |  

Let's run this interactively to start, so we can control the server.
This assumes you want to use your public IP for the relevant IP Address configurations.

Linux
```bash
mkdir -p ~/fts_data
docker run -it \
	-e FTS_DP_ADDRESS="$(curl ifconfig.me)" \
	--mount type=bind,src=fts_data,target=~/fts_data \
	-p 8080:8080 -p 8087:8087 -p 8443:8443 \
	-p 9000:9000 -p 19023:19023 \
	--name fts-node-1 \
	fts:local
```
Windows11
```powershell
mkdir $home/fts_data
$fts_data = wsl -d podman-machine-default -- wslpath -a "'$home\fts_data'"
docker run -it `
	-e FTS_DP_ADDRESS=$(curl ifconfig.me).Content `
	--mount type=bind,src=fts_data,target=$fts_data `
	-p 8080:8080 -p 8087:8087 -p 8443:8443 `
	-p 9000:9000 -p 19023:19023 `
	--name fts-node-1 `
	fts:local
```

Once this is running, point your ATAK clients at it, and make sure it works.
Once you are sure it works,
we are going to set it to run in the background and restart all the time.

Put the fts_data in a place where it will persist.
```bash
sudo mkdir -p /opt/fts_data
sudo chown $(whoami) /opt/fts_data
```

| Arg                                       | Description                                                 |
|-------------------------------------------|-------------------------------------------------------------|
| run --restart unless-stopped              | run the container forever, unless stopped intentionally     |
| --mount src=fts_data,target=/opt/fts_data | mount the volume for persistent data                        |

```bash 
docker run --restart unless-stopped \
	-e FTS_DP_ADDRESS="$(curl ifconfig.me)" \
	--mount src=fts_data,target=/opt/fts_data \
	-p 8080:8080 -p 8087:8087 -p 8443:8443 \
	-p 9000:9000 -p 19023:19023 \
	--name fts-service \
	fts:local
```

You man force it to stop with `docker stop fts-node-1`. 
