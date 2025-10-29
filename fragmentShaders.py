# fragmentShaders.py  (no borrar este comentario con el nombre del archivo)

# 1) Rim-Toon (conservado) — look cartoon con halo
rim_toon_fs = '''
#version 330 core
in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float value;   // grosor del rim (0..1)
uniform float time;

void main() {
    vec3 N = normalize(fragNormal);
    vec3 L = normalize(pointLight - fragPosition.xyz);
    vec3 V = normalize(-fragPosition.xyz);

    float lambert = max(0.0, dot(N, L));
    if (lambert < 0.25) lambert = 0.15;
    else if (lambert < 0.5) lambert = 0.45;
    else if (lambert < 0.75) lambert = 0.75;
    else lambert = 1.0;

    float rim = 1.0 - max(0.0, dot(N, V));
    rim = smoothstep(1.0 - mix(0.25, 0.85, clamp(value,0.0,1.0)), 1.0, rim);

    vec4 base = texture(tex0, fragTexCoords);
    vec3 color = base.rgb * (lambert + ambientLight);
    color += rim * vec3(1.0, 0.96, 0.88);
    fragColor = vec4(color, base.a);
}
'''


# 2) GOLD METAL — pinta TODO de dorado brillante (ignora albedo)
gold_metal_fs = '''
#version 330 core
in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform vec3 pointLight;
uniform float ambientLight;
uniform float value;  // controla "pulido": 0 mate, 1 espejo
uniform float time;

void main() {
    vec3 N = normalize(fragNormal);
    vec3 L = normalize(pointLight - fragPosition.xyz);
    vec3 V = normalize(-fragPosition.xyz);
    vec3 H = normalize(L + V);

    // Oro (sRGB aproximado)
    vec3 gold = vec3(1.000, 0.766, 0.336);

    // Diffuse mínimo (metales casi no difunden color de luz blanca)
    float NdotL = max(0.0, dot(N, L));
    vec3 diffuse = gold * (0.15 * NdotL);

    // Especular tipo Blinn-Phong
    float gloss = mix(32.0, 256.0, clamp(value,0.0,1.0));
    float spec = pow(max(0.0, dot(N, H)), gloss);
    // Especular tintado de oro
    vec3 specular = gold * spec * mix(0.6, 1.25, clamp(value,0.0,1.0));

    // Ambient dorado
    vec3 ambient = gold * (ambientLight * 0.8);

    // Ligerísima variación para “anodizado” (shimmer)
    float shimmer = 0.02 * sin(time*6.0 + fragPosition.x*3.0 + fragPosition.y*4.0);

    vec3 color = ambient + diffuse + specular + shimmer;
    fragColor = vec4(color, 1.0);
}
'''


# 3) RAINBOW SHIFT — recolorea la textura con rotación de HUE (arcoíris)
rainbow_fs = '''
#version 330 core
in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float value;  // 0..1 cuánta rotación de tono
uniform float time;

// Matriz de rotación de HUE (YIQ-like)
mat3 hueMatrix(float a){
    float c = cos(a), s = sin(a);
    // Coefs para aproximar hue rotation en sRGB
    return mat3(
        0.299 + 0.701*c + 0.168*s, 0.587 - 0.587*c + 0.330*s, 0.114 - 0.114*c - 0.497*s,
        0.299 - 0.299*c - 0.328*s, 0.587 + 0.413*c + 0.035*s, 0.114 - 0.114*c + 0.292*s,
        0.299 - 0.300*c + 1.250*s, 0.587 - 0.588*c - 1.050*s, 0.114 + 0.886*c - 0.203*s
    );
}

void main() {
    vec3 N = normalize(fragNormal);
    vec3 L = normalize(pointLight - fragPosition.xyz);

    vec3 albedo = texture(tex0, fragTexCoords).rgb;

    float hue = (time*0.7) + (fragTexCoords.x - 0.5)*4.0 + (fragTexCoords.y - 0.5)*2.0;
    hue *= mix(0.0, 1.0, clamp(value,0.0,1.0)); // cuánto giramos el tono
    vec3 recolor = hueMatrix(hue) * albedo;

    float NdotL = max(0.0, dot(N, L));
    vec3 color = recolor * (NdotL + ambientLight);

    fragColor = vec4(color, 1.0);
}
'''


# 4) UV INK — “pinta” por UV (tintas intensas + contorno), ignora albedo
uv_debug_fs = '''
#version 330 core
in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform vec3 pointLight;
uniform float ambientLight;
uniform float value;  // controla contraste/contorno
uniform float time;

vec3 palette(float t){
    // paleta intensa (cyan-magenta-amarillo-azul)
    vec3 a = vec3(0.0, 1.0, 1.0);
    vec3 b = vec3(1.0, 0.0, 1.0);
    vec3 c = vec3(1.0, 1.0, 0.0);
    vec3 d = vec3(0.2, 0.3, 1.0);
    if(t < 0.33) return mix(a, b, t/0.33);
    else if(t < 0.66) return mix(b, c, (t-0.33)/0.33);
    else return mix(c, d, (t-0.66)/0.34);
}

void main() {
    vec2 uv = fragTexCoords;
    // rayas/ondas por UV animadas
    float stripes = 0.5 + 0.5*sin( (uv.x*20.0) + (uv.y*10.0) + time*2.0 );
    float dots    = step(0.5, fract(uv.x*40.0)) * step(0.5, fract(uv.y*40.0));
    float t = mix(stripes, dots, 0.35 + 0.35*sin(time*1.3));

    // contorno por facing (rim)
    vec3 N = normalize(fragNormal);
    vec3 V = normalize(-fragPosition.xyz);
    float rim = pow(1.0 - max(0.0, dot(N, V)), mix(2.0, 6.0, clamp(value,0.0,1.0)));

    vec3 ink = palette(fract(t + time*0.1));
    // mezcla tinta con rim para borde brillante
    vec3 base = ink + rim*vec3(1.0, 0.9, 0.8);

    // luz básica
    vec3 L = normalize(pointLight - fragPosition.xyz);
    float NdotL = max(0.0, dot(N, L));
    vec3 color = base * (NdotL + ambientLight*0.8);

    fragColor = vec4(color, 1.0);
}
'''


# 5) CRYSTAL GLASS — vidrio translúcido (transparente + “refracción” + aberración)
crystal_fs = '''
#version 330 core
in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float value;  // 0..1: fuerza de refracción y transparencia
uniform float time;

void main() {
    vec3 N = normalize(fragNormal);
    vec3 V = normalize(-fragPosition.xyz);
    vec3 L = normalize(pointLight - fragPosition.xyz);

    // fuerza de “refracción”
    float k = mix(0.004, 0.03, clamp(value,0.0,1.0));
    vec2 bend = N.xy * (0.6 + 0.4*sin(time*1.5)) * k;

    // aberración cromática (RGB sampleados en uv distintos)
    float r = texture(tex0, fragTexCoords + bend).r;
    float g = texture(tex0, fragTexCoords + bend*0.6).g;
    float b = texture(tex0, fragTexCoords - bend).b;
    vec3 refrCol = vec3(r,g,b);

    // highlight fuerte (vidrio pulido)
    vec3 H = normalize(L + V);
    float spec = pow(max(0.0, dot(N, H)), 180.0);
    vec3 specular = vec3(1.0) * spec * 0.9;

    // tinte frío sutil
    vec3 tint = vec3(0.85, 0.92, 1.0);
    vec3 color = refrCol * tint;

    // lambert + ambiente (muy suave en vidrio)
    float NdotL = max(0.0, dot(N, L));
    color = color * (0.25*NdotL + ambientLight*0.4) + specular;

    // transparencia: más en el borde por Fresnel
    float fres = pow(1.0 - max(0.0, dot(N, V)), 2.0);
    float alpha = mix(0.35, 0.75, clamp(value,0.0,1.0));
    alpha = mix(alpha, 0.15 + alpha*0.6, fres); // borde más transparente

    fragColor = vec4(color, alpha);
}
'''


# 6) PIXELATE — estilo “mosaico” (conservado, porque te gustó)
pixelate_fs = '''
#version 330 core
in vec2 fragTexCoords;
in vec3 fragNormal;
in vec4 fragPosition;

out vec4 fragColor;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float value;
uniform float time;

void main() {
    float blocks = mix(8.0, 100.0, clamp(value,0.0,1.0));
    blocks *= (0.9 + 0.1*sin(time*2.0));
    vec2 uvq = floor(fragTexCoords * blocks) / blocks;

    vec3 col = texture(tex0, uvq).rgb;

    vec3 N = normalize(fragNormal);
    vec3 L = normalize(pointLight - fragPosition.xyz);
    float lambert = max(0.0, dot(N, L)) + ambientLight;

    fragColor = vec4(col * lambert, 1.0);
}
'''