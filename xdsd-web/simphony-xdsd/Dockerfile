FROM simphonyproject/ubuntu-18.04-vncapp:latest

LABEL eu.simphony-project.docker.ui_name="XDSD"
LABEL eu.simphony-project.docker.description="Ubuntu machine running XDSD on Simphony-Remote"

SHELL ["/bin/bash", "-c"]
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8


# Install ProMo dependencies
RUN apt-get update && apt-get install -qq -y \
 	rxvt-unicode \
        evince \
        # Install LaTeX dependencies
        texlive \
        texlive-science \
        texlive-latex-extra \
        # Install pnglatex dependencies
        dvipng \
        imagemagick \
        # Install Python dependencies
        python3-pip \
        python3-setuptools \
        # Install the `dot` command-line utility indirectly
        graphviz \
   && rm -rf /var/lib/apt/lists/*

# Install PyQt5 dependencies
RUN apt-get update
RUN apt-get install -y \
    qt5-default \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0

RUN apt-get install -y python3-venv

# Set up xdsd directory hierarchy
RUN mkdir /xdsd_home
RUN mkdir /xdsd_home/xdsd


COPY container-files/XDSD /xdsd_home/xdsd
COPY container-files/environment.yml /xdsd_home/environment.yml
RUN chmod 777 /xdsd_home/xdsd/examples

# Set up the autostart logic for `openbox-session`
RUN mkdir -p /etc/skel/.config/openbox
COPY container-files/autostart /etc/skel/.config/openbox/autostart
RUN chmod 755 /etc/skel/.config/openbox/autostart



ENV PATH /opt/conda/bin:$PATH
ENV PATH /opt/conda/envs/xdsd/bin:$PATH

#Install conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.5.11-Linux-x86_64.sh -O ~/miniconda.sh --no-check-certificate && /bin/bash ~/miniconda.sh -b -p /opt/conda
RUN rm ~/miniconda.sh

#Update conda
RUN conda update -n base -c defaults conda

# activate conda base env
RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc
RUN echo "conda activate base" >> ~/.bashrc

# create xdsd conda virtual env 
RUN conda env create -f /xdsd_home/environment.yml
# activate xdsd conda virtual env 
RUN echo "conda activate xdsd" >> ~/.bashrc

# activate xdsd env for new bash-shell launch
SHELL ["conda", "run", "-n", "xdsd", "/bin/bash", "-c"]

# activate env
RUN conda --version \
  && conda install -c conda-forge pyqt \
  && source activate xdsd



