#version 120
//#extension GL_NV_shadow_samplers_cube : enable

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


vec4 PhongLighting(vec3 vertex, vec3 normal, vec3 light_position, vec3 camera_position, vec3 ambient, vec3 diffuse, vec3 specular, float spec_weight){
    vec4 color = vec4(ambient, 1.);
    vec3 light_direction = normalize(light_position - vertex);
    float diffuse_coeff = clamp(max(dot(normalize(normal), light_direction), 0), 0.0, 1.0);
    color.rgb += diffuse_coeff * diffuse;

    if (spec_weight > 1.0) {
        vec3 reflectionVector = reflect(light_direction, normalize(normal));
        float cosAngle = max(0.0, -dot(normalize(camera_position - vertex), reflectionVector));
        float specular_coeff = pow(cosAngle, spec_weight);
        color.rgb += 1.5 * (specular_coeff * specular);
    }
    return clamp(color, 0, 1);
}


void main()
{
    // Apply Lighting
    if (flat_shading > 0) {
        gl_FragColor = vec4(diffuse, 1.0);
    } else {
        gl_FragColor = PhongLighting(vVertex.xyz, normal, light_position, camera_position, ambient, diffuse, specular, spec_weight);
    }

    // Depth-Map Shadows
    if (DepthMap_isBound > 0){
        if (ShadowCoord.w > 0.0){
            vec4 shadowCoordinateWdivide = ShadowCoord / ShadowCoord.w;
            shadowCoordinateWdivide.z -= .0001; // to prevent "shadow acne" caused from precision errors
            vec4 distanceFromLight = shadow2D(DepthMap, shadowCoordinateWdivide.xyz);
            gl_FragColor.rgb *= 0.65 + (0.35 * distanceFromLight.rgb);
        }
    }

    // UV Texture
    if (TextureMap_isBound > 0){
        gl_FragColor.rgb *= texture2D(TextureMap, texCoord).rgb;
    }

    return;
 }
