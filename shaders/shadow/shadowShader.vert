#version 150
#extension GL_ARB_explicit_attrib_location : enable

layout(location = 0) in vec3 vertexPosition;

uniform mat4 light_view_matrix;
uniform mat4 model_matrix;
uniform mat4 light_projection_matrix;

void main()
  {

	//Calculate Vertex Position on Screen
	gl_Position = light_projection_matrix * light_view_matrix * model_matrix * vec4(vertexPosition, 1.0);

  }

