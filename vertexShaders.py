# vertexShaders.py

# Vertex Shader por defecto (passthrough geom/UV/normal)
default_vs = '''
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

void main() {
    vec4 wp = modelMatrix * vec4(inPosition, 1.0);
    gl_Position  = projectionMatrix * viewMatrix * wp;
    fragPosition = wp;
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
'''

# 1) Twist — retuerce el modelo alrededor del eje Y (fuerte por defecto)
twist_vs = '''
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

void main() {
    // Intensidad efectiva: mínimo 1.2 rad por unidad Y
    float k = 1.2 + 2.5 * clamp(value, 0.0, 1.0);
    float ang = (inPosition.y * k) + time * (0.6 + 0.8 * value);
    float c = cos(ang), s = sin(ang);

    vec3 p = vec3(
        c*inPosition.x + s*inPosition.z,
        inPosition.y,
        -s*inPosition.x + c*inPosition.z
    );

    gl_Position  = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
    fragPosition = modelMatrix * vec4(p, 1.0);
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
'''


# 2) Pulse — “respira” escalando radialmente con onda (base 8% aun con value=0)
pulse_vs = '''
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

void main() {
    float r = length(inPosition);
    // Amplitud efectiva: 0.08..0.45
    float amp = 0.08 + 0.37 * clamp(value, 0.0, 1.0);
    float s = 1.0 + amp * sin(time * (2.6 + 1.2*value) + r * (3.5 + 2.0*value));
    vec3 p = inPosition * s;

    gl_Position  = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
    fragPosition = modelMatrix * vec4(p, 1.0);
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
'''


# 3) Explode — desplaza a lo largo de la normal con “ruido” (base 0.25)
explode_vs = '''
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

float hash31(vec3 p) {
    return fract(sin(dot(p, vec3(12.9898,78.233,37.719))) * 43758.5453);
}

void main() {
    float baseAmp = 0.25;                           // visible aunque value=0
    float extra   = 0.55 * clamp(value,0.0,1.0);    // escala adicional por value
    float speed   = 4.0 + 3.0 * value;

    float n = hash31(inPosition * (2.2 + value*2.0) + vec3(time*0.35));
    float d = (baseAmp + extra) * (0.6 + 0.4*sin(speed * time + n*6.2831));
    vec3 p = inPosition + inNormals * d;

    gl_Position  = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
    fragPosition = modelMatrix * vec4(p, 1.0);
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
'''


# 4) Bubble — “infla” hacia esfera + swirl de UV (base 35%)
bubble_vs = '''
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

void main() {
    float t = clamp(value,0.0,1.0);
    float r = max(0.0001, length(inPosition));
    vec3 sphere = normalize(inPosition) * r;

    // Esferización efectiva: 0.35..0.95
    float sph = mix(0.35, 0.95, t);
    vec3 p = mix(inPosition, sphere, sph);

    // Ondulación de membrana base 0.03..0.09
    float wob = mix(0.03, 0.09, t);
    p += normalize(inPosition) * wob * sin(time*2.2 + r*8.0);

    // Swirl UV animado
    vec2 uv = inTexCoords;
    vec2 c = vec2(0.5, 0.5);
    vec2 d = uv - c;
    float ang = (0.5 + 0.6*t) * exp(-2.0 * length(d)) * sin(time*1.3);
    float ca = cos(ang), sa = sin(ang);
    vec2 uv2 = c + vec2(ca*d.x - sa*d.y, sa*d.x + ca*d.y);

    gl_Position  = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
    fragPosition = modelMatrix * vec4(p, 1.0);
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = uv2;
}
'''


# 5) Ripple — ondas circulares + scroll UV (base visible)
ripple_vs = '''
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

void main() {
    float t = clamp(value,0.0,1.0);
    vec3 p = inPosition;

    float r = length(p.xz);
    // Amplitud base 0.06..0.28, frecuencia 7..16
    float amp  = 0.06 + 0.22 * t;
    float freq = 7.0 + 9.0 * t;
    float spd  = 3.5 + 2.5 * t;

    p.y += amp * sin(r * freq - time * spd);

    // UV: scroll y distorsión radial
    vec2 uv = inTexCoords + vec2(0.03*time, 0.02*time);
    uv += normalize(inTexCoords - vec2(0.5)) * (0.02 + 0.03*t) * sin(time*2.0 + r*5.0);

    gl_Position  = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
    fragPosition = modelMatrix * vec4(p, 1.0);
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = uv;
}
'''


# 6) Kaleido — plegado tipo caleidoscopio en UV (con “breathing”)
kaleido_vs = '''
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

vec2 kaleido(vec2 uv, float sectors){
    vec2 c = vec2(0.5);
    vec2 d = uv - c;
    float a = atan(d.y, d.x);     // -pi..pi
    float r = length(d);
    float seg = 6.2831853 / max(1.0, sectors);
    float k = mod(a, seg);
    float k2 = min(k, seg - k);
    float ang = k2 - seg*0.25;
    vec2 dir = vec2(cos(ang), sin(ang));
    return c + dir * r;
}

void main() {
    float t = clamp(value,0.0,1.0);
    float sectors = 5.0 + 9.0 * (0.6 + 0.4*sin(time*0.7 + t)); // 5..14 aprox

    // Breathing suave para dar vida (base 3%)
    vec3 p = inPosition * (1.0 + (0.03 + 0.04*t) * sin(time*1.1 + length(inPosition)*3.0));

    vec2 uv = kaleido(inTexCoords, sectors);

    gl_Position  = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
    fragPosition = modelMatrix * vec4(p, 1.0);
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = uv;
}
'''
