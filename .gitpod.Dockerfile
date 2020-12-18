FROM gitpod/workspace-full

# Install custom tools, runtime, etc.
RUN apt-get update && apt-get install libglu1-mesa-dev freeglut3-dev mesa-common-dev
