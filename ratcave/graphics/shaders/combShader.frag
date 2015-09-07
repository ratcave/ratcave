#version 330
#extension GL_NV_shadow_samplers_cube : enable

uniform int hasTexture, hasShadow, hasCubeMap, hasLighting;
uniform float spec_weight, opacity;
uniform vec3 camera_position, light_position;
uniform vec3 diffuse, spec_color, ambient;
uniform sampler2D ShadowMap, ImageTextureMap;
uniform samplerCube my_cube_texture;

in float lightAmount;
in vec2 texCoord;
in vec3 normal, eyeVec;
in vec4 vVertex, ShadowCoord;

out vec4 final_color;

void main()
{

    //If lighting is turned off, just use the diffuse color and return. (Flat lighting)
    if (hasLighting < 1) {
        final_color = vec4(diffuse, 1.0);
        return;
    }

    //Shade Cube Map and return, if needed
    if (hasCubeMap > 0) {
        final_color = textureCube(my_cube_texture, eyeVec) * lightAmount;
        return;
    }

    // Ambient Lighting
    float ambient_coeff = .25;

    // UV Texture
    vec3 texture_coeff = vec3(1.0);
    if (hasTexture > 0){
        texture_coeff = texture2D(ImageTextureMap, texCoord).rgb;
    }

    //// Phong Model
    vec3 normal = normalize(normal);
    vec3 light_direction = normalize(light_position - vVertex.xyz);

    // Phong Diffuse
    float diffuse_coeff = clamp(max(dot(normal,light_direction),0), 0.0, 1.0);

    // Phong Specularity
    float specular_coeff = 0.;
    if (spec_weight > 1.0) {
        vec3 reflectionVector = reflect(light_direction, normal);
        float cosAngle = max(0.0, -dot(normalize(camera_position - vVertex.xyz), reflectionVector));
        specular_coeff = pow(cosAngle, spec_weight);
    }

    // Depth-Map Shadows
    float shadow_coeff = 1.;
    if (hasShadow > 0){
        if (ShadowCoord.w > 0.0){
            vec4 shadowCoordinateWdivide = ShadowCoord / ShadowCoord.w;
            float distanceFromLight = texture2D(ShadowMap,shadowCoordinateWdivide.xy).z;

            if ( distanceFromLight < shadowCoordinateWdivide.z - .0001) { // to prevent "shadow acne" caused from precision errors
                shadow_coeff = 0.65;
            }
        }
    }

    // Calculate Final Color and Opacity
    vec3 color = shadow_coeff * texture_coeff *
                 (1.5 * (specular_coeff * spec_color) +
                 (diffuse_coeff * diffuse) +
                 (ambient_coeff * ambient));
    final_color = vec4(clamp(color, 0, 1), opacity);


 }
 
