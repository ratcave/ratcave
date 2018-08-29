#version 130
#extension GL_NV_shadow_samplers_cube : enable

uniform int flat_shading, TextureMap_isBound, DepthMap_isBound;
uniform float spec_weight, opacity;
uniform vec3 camera_position, light_position;
uniform vec3 diffuse, specular, ambient;
uniform sampler2D TextureMap;
uniform sampler2DShadow DepthMap;
uniform samplerCube CubeMap;

//varying float lightAmount;
varying vec2 texCoord;
varying vec3 normal, eyeVec;
varying vec4 vVertex, ShadowCoord;


void main()
{

    // Depth-Map Shadows
    float shadow_coeff = 1.;
    if (DepthMap_isBound > 0){
        if (ShadowCoord.w > 0.0){
            vec4 shadowCoordinateWdivide = ShadowCoord / ShadowCoord.w;
            shadowCoordinateWdivide.z -= .0001; // to prevent "shadow acne" caused from precision errors
            float distanceFromLight = texture(DepthMap, shadowCoordinateWdivide.xyz);
            shadow_coeff = 0.65 + (0.35 * distanceFromLight);
        }
    }

    // UV Texture
    vec3 texture_coeff = vec3(1.0);
    if (TextureMap_isBound > 0){
        texture_coeff = texture2D(TextureMap, texCoord).rgb;
    }

    //If lighting is turned off, just use the diffuse color and return. (Flat lighting)
    if (flat_shading > 0) {
        gl_FragColor = vec4(diffuse, 1.0) * shadow_coeff * vec4(texture_coeff, 1.);
        return;
    }

    // Ambient Lighting
    float ambient_coeff = 0.;

    // Phong Model
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

    // Calculate Final Color and Opacity
    vec3 color = shadow_coeff * texture_coeff *
                 (1.5 * (specular_coeff * specular) +
                 (diffuse_coeff * diffuse) +
                 (ambient_coeff * ambient));
    gl_FragColor = vec4(clamp(color, 0, 1), 1.0);

 }
