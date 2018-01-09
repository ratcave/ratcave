#version 150

uniform sampler2D TextureMap;
uniform vec2 frameBufSize;
//uniform int grayscale;

in vec2 texCoord;

out vec4 color;

void main( void ) {
    float mipmapLevel = textureQueryLod(TextureMap, texCoord).y;
    color = vec4(textureLod(TextureMap, texCoord, mipmapLevel).rgb, 1.);
    return;
}