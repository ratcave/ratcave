FROM gitpod/workspace-full

# Install custom tools, runtime, etc.
RUN sudo apt-get update && sudo apt-get install -y libglu1-mesa-dev freeglut3-dev mesa-common-dev
