#version 120

attribute vec3 vertexPosition;
attribute vec3 normalPosition;
attribute vec2 uvTexturePosition;

uniform vec3 light_position, playerPos;
uniform mat4 model_matrix, normal_matrix;
uniform mat4 view_matrix = mat4(1.0);
uniform mat4 projection_matrix = mat4(vec4(1.38564062,  0.,  0.,  0.),
                                      vec4(0.,  1.73205078,  0.,  0.),
                                      vec4(0., 0., -1.01680672, -1. ),
                                      vec4(0., 0., -0.20168068, 0.)
                                      );
uniform mat4 light_projection_matrix, light_view_matrix;

varying float lightAmount;
varying vec2 texCoord;
varying vec3 normal, eyeVec;
varying vec4 vVertex, ShadowCoord;

mat4 texture_bias = mat4(0.5, 0.0, 0.0, 0.0,
                         0.0, 0.5, 0.0, 0.0,
                         0.0, 0.0, 0.5, 0.0,
                         0.5, 0.5, 0.5, 1.0);

float diffuse_weight = .5;

void main()
  {

    //Calculate Vertex World Position and Normal Direction
    vVertex = model_matrix * vec4(vertexPosition, 1.0);
    normal = normalize(normal_matrix * vec4(normalPosition, 1.0)).xyz;

    //Calculate Vertex Position on Screen
	gl_Position = projection_matrix * view_matrix * vVertex;

	//Calculate Texture Coordinate for UV and Cubemaps
	texCoord = uvTexturePosition;
	eyeVec = vVertex.xyz - playerPos;

  	//Calculate Shadow Coordinate
  	ShadowCoord = (texture_bias * light_projection_matrix * light_view_matrix * vVertex);

    // Calculate Diffusion Intensity, and Subtract it out (only used for cubemaps)
    float lambertTerm0 = dot(normal, normalize(light_position - vVertex.xyz));
//    lightAmount = 1.; // - (diffuse_weight * lambertTerm0);  // Cancel out diffusion effects
//    lightAmount = - (diffuse_weight * lambertTerm0);  // Cancel out diffusion effects

    return;
  }
