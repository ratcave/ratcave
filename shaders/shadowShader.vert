#version 330

layout(location = 0) in vec3 vertexPosition;

uniform mat4 view_matrix;
uniform mat4 model_matrix;//_global, model_matrix_local;
uniform mat4 projection_matrix;

void main()
  {

	//Calculate Vertex Position on Screen
	gl_Position = projection_matrix * view_matrix * model_matrix * vec4(vertexPosition, 1.0);

  }

