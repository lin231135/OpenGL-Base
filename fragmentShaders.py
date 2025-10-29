# fragmentShaders.py
# --------------------------------------------
# (mantén este comentario con el nombre del archivo)

fragment_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;

void main()
{
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(normalize(fragNormal), lightDir)) + ambientLight;

    fragColor = texture(tex0, fragTexCoords) * intensity;
}
'''

toon_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;

void main()
{
    vec3 N = normalize(fragNormal);
    vec3 L = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(N, L)) + ambientLight;

    if (intensity < 0.33)
        intensity = 0.15;
    else if (intensity < 0.66)
        intensity = 0.55;
    else
        intensity = 1.0;

    fragColor = texture(tex0, fragTexCoords) * intensity;
}
'''

negative_shader = '''
#version 330 core

in vec2 fragTexCoords;
out vec4 fragColor;

uniform sampler2D tex0;

void main()
{
    vec4 c = texture(tex0, fragTexCoords);
    fragColor = vec4(1.0 - c.rgb, c.a);
}
'''

magma_shader = '''
#version 330 core

in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0; // base
uniform sampler2D tex1; // lava overlay
uniform vec3 pointLight;
uniform float ambientLight;
uniform float time;

void main()
{
    vec3 N = normalize(fragNormal);
    vec3 L = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(N, L)) + ambientLight;

    // base lit albedo
    vec4 base = texture(tex0, fragTexCoords) * intensity;

    // simple scrolling lava overlay
    vec2 flow = fragTexCoords + vec2(time * 0.08, sin(time*0.7)*0.05);
    vec4 lava = texture(tex1, flow);

    // combinar con un brillo animado
    float glow = (sin(time * 2.0) * 0.5 + 0.5) * 0.65;
    fragColor = mix(base, lava, glow);
}
'''