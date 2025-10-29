# vertexShaders.py

vertex_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

void main()
{
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(inPosition, 1.0);
    fragPosition = modelMatrix * vec4(inPosition, 1.0);
    fragNormal = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
'''

fat_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float value;

void main()
{
    vec3 expanded = inPosition + inNormals * value;
    fragPosition = modelMatrix * vec4(expanded, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    fragNormal = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
'''

water_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;
uniform float value;

void main()
{
    float displacement = sin(time + inPosition.x + inPosition.z) * value;
    vec3 displaced = inPosition + vec3(0.0, displacement, 0.0);
    fragPosition = modelMatrix * vec4(displaced, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    fragNormal = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
'''

# “Tierra Cayendo”
earth_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;
uniform float value;

void main()
{
    // Efecto de caída tipo tierra/arena
    float fallSpeed = value * 10.0; // velocidad ajustable

    float crumble = fract(sin(dot(inPosition.xz, vec2(12.9898,78.233))) * 43758.5453);
    float offset = (inPosition.y < 0.0) ? crumble * time * fallSpeed : 0.0;

    vec3 displaced = inPosition - vec3(0.0, offset, 0.0);

    fragPosition = modelMatrix * vec4(displaced, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    fragNormal = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
'''

melt_shader = '''
#version 330 core

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float time;
uniform float value;

void main()
{
    vec3 displaced = inPosition;
    displaced.y += sin(time * 3.0 + inPosition.x * 5.0) * value * 0.2;
    fragPosition = modelMatrix * vec4(displaced, 1.0);
    gl_Position = projectionMatrix * viewMatrix * fragPosition;
    fragNormal = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
'''