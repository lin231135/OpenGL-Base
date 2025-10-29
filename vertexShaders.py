# vertexShaders.py  (no borrar este comentario con el nombre del archivo)

# 1) Twist — retuerce el modelo alrededor del eje Y
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
    float k = mix(0.0, 2.5, clamp(value, 0.0, 1.0));
    float ang = (inPosition.y * k) + time * 0.8 * value;
    float c = cos(ang), s = sin(ang);

    vec3 p = vec3(
        c*inPosition.x + s*inPosition.z,
        inPosition.y,
        -s*inPosition.x + c*inPosition.z
    );

    gl_Position  = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
    fragPosition = modelMatrix * vec4(p, 1.0);
    // Aproximación: rotación solo geométrica; normal transformada por matriz del modelo
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
'''

# 2) Pulse — “respira” escalando radialmente con una onda
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
    float amp = 0.35 * clamp(value,0.0,1.0);
    float s = 1.0 + amp * sin(time * 3.0 + r * 4.0);
    vec3 p = inPosition * s;

    gl_Position  = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
    fragPosition = modelMatrix * vec4(p, 1.0);
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
'''

# 3) Explode — desplaza a lo largo de la normal con “ruido” hash
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
    float n = hash31(inPosition * 3.1 + vec3(time*0.5));
    float d = mix(0.0, 0.6, clamp(value,0.0,1.0)) * (0.7 + 0.3*sin(time*5.0 + n*6.2831));
    vec3 p = inPosition + inNormals * d;

    gl_Position  = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
    fragPosition = modelMatrix * vec4(p, 1.0);
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = inTexCoords;
}
'''

# 4) Bubble — “infla” hacia una esfera y hace swirl de UV (perfecto con Crystal)
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
    // “Inflado” hacia esfera mezclando posición con su versión normalizada
    float r = max(0.0001, length(inPosition));
    vec3 sphere = normalize(inPosition) * r;
    vec3 p = mix(inPosition, sphere, 0.6 * t);     // 0..0.6 de esferización
    // Ondita suave para parecer membrana de burbuja
    p += normalize(inPosition) * 0.05 * t * sin(time*2.2 + r*8.0);

    // Swirl sutil de UV alrededor del centro para efectos con texturas
    vec2 uv = inTexCoords;
    vec2 c = vec2(0.5, 0.5);
    vec2 d = uv - c;
    float ang = (0.8 * t) * exp(-2.5 * length(d)) * sin(time*1.1);
    float ca = cos(ang), sa = sin(ang);
    vec2 rot = vec2(ca*d.x - sa*d.y, sa*d.x + ca*d.y);
    vec2 uv2 = c + rot;

    gl_Position  = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
    fragPosition = modelMatrix * vec4(p, 1.0);
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = uv2;
}
'''

# 5) Ripple — ondas circulares en Y según (x,z) + scroll de UV
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
    float freq = mix(6.0, 14.0, t);
    float amp  = mix(0.0, 0.25, t);
    p.y += amp * sin(r * freq - time * 4.0);

    // scroll de UV en diagonal + ligera distorsión radial
    vec2 uv = inTexCoords + vec2(time*0.05, time*0.03);
    uv += normalize(inTexCoords - vec2(0.5)) * 0.03 * sin(time*2.0 + r*5.0) * t;

    gl_Position  = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
    fragPosition = modelMatrix * vec4(p, 1.0);
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = uv;
}
'''

# 6) Kaleido — “plegado” tipo caleidoscopio sobre los UV
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
    // Mapea UV al espacio polar en torno a 0.5 y pliega el ángulo
    vec2 c = vec2(0.5);
    vec2 d = uv - c;
    float a = atan(d.y, d.x);             // -pi..pi
    float r = length(d);
    float seg = 6.2831853 / max(1.0, sectors);
    float k = mod(a, seg);
    // espejo en el centro del sector
    float k2 = min(k, seg - k);
    float ang = k2 - seg*0.25;            // re-centra un poco
    vec2 dir = vec2(cos(ang), sin(ang));
    return c + dir * r;
}

void main() {
    float t = clamp(value,0.0,1.0);
    // número de sectores entre 3 y 12
    float sectors = mix(3.0, 12.0, t*(0.6+0.4*sin(time*0.7)));

    // leve “breathing” para dar vida
    vec3 p = inPosition * (1.0 + 0.05 * sin(time*1.3 + length(inPosition)*3.0)*t);

    // UV caleidoscópicos
    vec2 uv = kaleido(inTexCoords, sectors);

    gl_Position  = projectionMatrix * viewMatrix * modelMatrix * vec4(p, 1.0);
    fragPosition = modelMatrix * vec4(p, 1.0);
    fragNormal   = normalize(mat3(modelMatrix) * inNormals);
    fragTexCoords = uv;
}
'''
