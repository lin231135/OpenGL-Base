# vertexShaders.py
# --------------------------------------------
# (mantén este comentario con el nombre del archivo)

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
    vec4 worldPos = modelMatrix * vec4(inPosition, 1.0);
    gl_Position = projectionMatrix * viewMatrix * worldPos;

    fragPosition = worldPos;
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
''';

fat_shader = '''
#version 330 core
// Expande/contrae el modelo a lo largo de la normal

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float value; // usa Z/X para variar (0..1 aprox)

void main()
{
    vec3 displaced = inPosition + inNormals * (value * 0.5); // rango suave
    vec4 worldPos = modelMatrix * vec4(displaced, 1.0);

    gl_Position = projectionMatrix * viewMatrix * worldPos;

    fragPosition = worldPos;
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
''';

water_shader = '''
#version 330 core
// Ondas senoidales verticales tipo "agua"

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
uniform float value; // amplitud

void main()
{
    float disp = sin(time + inPosition.x * 1.5 + inPosition.z * 1.2) * (value * 0.4);
    vec3 displaced = inPosition + vec3(0.0, disp, 0.0);
    vec4 worldPos = modelMatrix * vec4(displaced, 1.0);

    gl_Position = projectionMatrix * viewMatrix * worldPos;

    fragPosition = worldPos;
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
''';

twist_shader = '''
#version 330 core
// Twist alrededor del eje Y

layout (location = 0) in vec3 inPosition;
layout (location = 1) in vec2 inTexCoords;
layout (location = 2) in vec3 inNormals;

out vec2 fragTexCoords;
out vec3 fragNormal;
out vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;
uniform float value; // controla la cantidad de torsión (0..1 aprox)

void main()
{
    float k = value * 2.5; // fuerza del twist
    float angle = inPosition.y * k;
    float c = cos(angle);
    float s = sin(angle);

    // rota XZ en función de Y (torsión)
    vec3 twisted = vec3(
        inPosition.x * c - inPosition.z * s,
        inPosition.y,
        inPosition.x * s + inPosition.z * c
    );

    vec4 worldPos = modelMatrix * vec4(twisted, 1.0);

    gl_Position = projectionMatrix * viewMatrix * worldPos;

    fragPosition = worldPos;
    fragNormal   = normalize(mat3(modelMatrix) * inNormals); // aprox
    fragTexCoords = inTexCoords;
}
''';
