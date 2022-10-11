# xdsd
Development repository for the XDSD tool.
XDSD tool is available in two versions: XDSD-Desktop and XDSD-Web.

# XDSD-Desktop: 
The desktop version of the app has a Python backend and a PyQt5 based frontend. The Desktop version can be downloaded and run locally by the user. Please read the installation instructions and how-to guide that is available inside the XDSD-Desktop directory.
# XDSD-Web: 
The web version is based on a containerisation of the XDSD-Desktop app using Simphony-remote web service (https://simphony-remote.readthedocs.io/en/latest/)that uses JupyterHub to spawn the XDSD app per user. The web version is deployed on the Digital Ocean cloud platform using the concept of Infrastructure-as-a-Service (IaaS). To acess the web-version, the user is prompted to authenticate (currently authenticator used Github) to get access to the service.
# Access the web version here:
 [XDSD-WEB](https://www.xdsd-web.org)   