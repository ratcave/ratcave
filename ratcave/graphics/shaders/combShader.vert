#version 330

layout(location = 0) in vec3 vertexPosition;
layout(location = 1) in vec3 normalPosition;
layout(location = 2) in vec2 uvTexturePosition;

uniform vec3 light_position, playerPos;
uniform mat4 projection_matrix, view_matrix, model_matrix_global, normal_matrix;
uniform mat4 shadow_projection_matrix, shadow_view_matrix;

out float lightAmount;
out vec2 texCoord;
out vec3 vVertex, normal, eyeVec;
out vec4 ShadowCoord;

mat4 texture_bias = mat4(0.5, 0.0, 0.0, 0.0,
                         0.0, 0.5, 0.0, 0.0,
                         0.0, 0.0, 0.5, 0.0,
                         0.5, 0.5, 0.5, 1.0);

float diffuse_weight = .5;

void main()
  {

    //Calculate Vertex Position on Screen
	gl_Position = projection_matrix * view_matrix * model_matrix_global * vec4(vertexPosition, 1.0);

	//Calculate Vertex World Position, and Normal World Direction
	vVertex = (model_matrix_global * vec4(vertexPosition, 1.0)).xyz;
	normal = normalize(normal_matrix * vec4(normalPosition, 1.0)).xyz;

	//Calculate Texture Coordinate for UV and Cubemaps
	texCoord = uvTexturePosition;
	eyeVec = vVertex - playerPos;
  
  	//Calculate Shadow Coordinate
  	ShadowCoord = (texture_bias * shadow_projection_matrix * shadow_view_matrix * model_matrix_global * vec4(vertexPosition, 1.0));

    // Calculate Diffusion Intensity, and Subtract it out (only used for cubemaps)
    vec3 lightDir0 = normalize( light_position - vVertex );
    float lambertTerm0 = dot(normal, lightDir0);
    lightAmount = 1. - (diffuse_weight * lambertTerm0);  // Cancel out diffusion effects
  }
  
