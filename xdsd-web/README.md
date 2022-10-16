XDSD-Web:
========

Setup for xdsd-web deployment is prepared using **xdsd-desktop** and [simphony-remote](https://github.com/simphony/simphony-remote).

## Instructions to prepare setup:

1. To prepare a deployment setup of the **xdsd-web**, clone the xdsd repository from its github link (https://github.com/dnaforge/xdsd)   and `cd` into the `xdsd-web` directory:

    git clone git@github.com:dnaforge/xdsd.git
    cd xdsd-web


2. Clone the [simphony-remote](https://github.com/simphony/simphony-remote),[simphony-remote-docker-scripts](https://github.com/simphony/simphony-remote-docker-scripts), and  [simphony-remote-docker-base](https://github.com/simphony/simphony-remote-docker-base) repositories inside the `xdsd-web` directory:

    git clone git@github.com:simphony/simphony-remote.git
    git clone git@github.com:simphony/simphony-remote-docker-scripts.git
    git clone git@github.com:simphony/simphony-remote-docker-base.git

3. First, we will use the scripts from `simphony-remote-docker-scripts` to create a base image of Ubuntu OS (tested with version 16/18) and a few libraries to enable desktop GUI acess using `novnc` (a open-source VNC client):
      
      cd simphony-remote-docker-scripts/scripts
      bash create_production_base.sh ../../simphony-remote-docker-base/build.conf
      bash build_base.sh ../../simphony-remote-docker-base/build.conf


4. Second, we will create docker images of xdsd-web app for production and deployment. After this step, a docker image (`simphonyproject/xdsd-web`; TAG latest) of the xdsd-web app should be seen by running `docker images` command

      bash create_production_app.sh ../../simphony-remote-docker-xdsd-web/build.conf
      bash build_app.sh ../../simphony-remote-docker-xdsd-web/build.conf

5.  We can now prepare the simphony-remote service for deployment of the created docker images of the xdsd-web app:
     
     For preparing a simphony-remote web service setup for single-user or multi-user deployment, read the detailed instructions from here: https://simphony-remote.readthedocs.io/en/latest/  
       


# DISCLAIMER: 
The use of simphony-remote software in the XDSD tool do not imply any endorsement or promotion in any form from the SimPhony Consortium and its contributors. 