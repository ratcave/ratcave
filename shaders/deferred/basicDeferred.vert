#version 150
#extension GL_ARB_explicit_attrib_location : enable


layout(location = 0) in vec3 vertexPosition;
layout(location = 2) in vec2 uvTexturePosition;

out vec2 texCoord;

void main()
  {

	//Calculate Vertex Position on Screen
	gl_Position = vec4(vertexPosition, 1.0);
	texCoord = uvTexturePosition;

  }
  
