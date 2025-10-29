# RendererOpenGL2025.py

import importlib
import pygame
import pygame.display
from pygame.locals import *
import glm

from gl import Renderer
from buffer import Buffer
from model import Model

# Shaders
from vertexShaders import *
from fragmentShaders import *

# ---------------- Inicialización Pygame + OpenGL ----------------
pygame.init()
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)

# ---------------- Ventana ----------------
width, height = 960, 540
screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
clock = pygame.time.Clock()

# ---------------- Renderer ----------------
rend = Renderer(screen)
rend.pointLight = glm.vec3(1, 1, 1)
rend.value = 0.85

# ---------------- Helpers: estado/ayuda ----------------
def set_title():
    pygame.display.set_caption(
        f"VS={current_vs_name} | FS={current_fs_name} | value={rend.value:.2f}  "
        f"[H: Ayuda]"
    )

HELP_TEXT = """
Controles:
  R: Reset (modelo normal)
  F: Alterna Fill/Wireframe

  FRAGMENT SHADERS:
    1: Rim-Toon
    2: Gold-Metal
    3: UV-Ink
    4: Crystal

  VERTEX SHADERS:
    5: Twist
    6: Pulse
    7: Explode
    8: Bubble
    9: Ripple
    0: Kaleido

  Z / X: Disminuir / Aumentar 'value'
  Flechas: Mover cámara (X/Z)
  W A S D Q E: Mover luz (X/Y/Z)
  R: Volver modelo a default
"""

def show_help():
    print(HELP_TEXT)
    pygame.display.set_caption("Ayuda mostrada en la consola (H para ocultar/volver).")

def set_shaders_safe(vs_src, fs_src):
    try:
        rend.SetShaders(vs_src, fs_src)
    except Exception as e:
        # Si hay error de compilación, volvemos a default
        rend.SetShaders(default_vs, default_fs)

# --------- Reset a estado “normal” ----------
def reset_to_default():
    global currVertexShader, currFragmentShader, current_vs_name, current_fs_name
    currVertexShader   = default_vs
    currFragmentShader = default_fs
    current_vs_name = "Default"
    current_fs_name = "Default"
    set_shaders_safe(currVertexShader, currFragmentShader)
    set_title()

# --------- Diccionarios de mapeo teclas → shaders ---------
FRAG_MAP = {
    K_1: ("Rim-Toon",  rim_toon_fs),
    K_2: ("Gold-Metal", gold_metal_fs),
    K_3: ("UV-Ink",    uv_debug_fs),
    K_4: ("Crystal",   crystal_fs),
    # Si quieres reactivar Pixelate, añade:
    # K_5: ("Pixelate", pixelate_fs),
}
VERT_MAP = {
    K_5: ("Twist",   twist_vs),
    K_6: ("Pulse",   pulse_vs),
    K_7: ("Explode", explode_vs),
    K_8: ("Bubble",  bubble_vs),
    K_9: ("Ripple",  ripple_vs),
    K_0: ("Kaleido", kaleido_vs),
}

# Shaders iniciales → NORMAL
current_vs_name = "Default"
current_fs_name = "Default"
reset_to_default()

# ---------------- Skybox (opcional) ----------------
skyboxTextures = [
    "skybox/right.jpg",
    "skybox/left.jpg",
    "skybox/top.jpg",
    "skybox/bottom.jpg",
    "skybox/front.jpg",
    "skybox/back.jpg"
]
rend.CreateSkybox(skyboxTextures)

# ---------------- Modelo ----------------
model = Model("models/tomato.obj")   # o "models/pacman.obj"
model.position = glm.vec3(0.0, -1.5, -4.0)
model.scale    = glm.vec3(0.25, 0.25, 0.25)
rend.scene.append(model)

# ---------------- Loop principal ----------------
isRunning = True
show_help()
set_title()

while isRunning:
    deltaTime = clock.tick(60) / 1000.0
    rend.elapsedTime += deltaTime

    for event in pygame.event.get():
        if event.type == QUIT:
            isRunning = False

        elif event.type == KEYDOWN:
            # Reset a NORMAL
            if event.key == K_r:
                reset_to_default()
                continue

            # Toggle fill/wireframe
            if event.key == K_f:
                rend.ToggleFilledMode()
                set_title()
                continue

            # Mostrar ayuda
            if event.key == K_h:
                show_help()
                set_title()
                continue

            # ---------- FRAGMENT SHADERS ----------
            if event.key in FRAG_MAP:
                name, fs = FRAG_MAP[event.key]
                current_fs_name = name
                set_shaders_safe(currVertexShader, fs)
                currFragmentShader = fs
                set_title()
                continue

            # ---------- VERTEX SHADERS ----------
            if event.key in VERT_MAP:
                name, vs = VERT_MAP[event.key]
                current_vs_name = name
                set_shaders_safe(vs, currFragmentShader)
                currVertexShader = vs
                set_title()
                continue

    # Cámara
    keys = pygame.key.get_pressed()
    spd = 2.0 * deltaTime
    if keys[K_UP]:    rend.camera.position.z += spd
    if keys[K_DOWN]:  rend.camera.position.z -= spd
    if keys[K_RIGHT]: rend.camera.position.x += spd
    if keys[K_LEFT]:  rend.camera.position.x -= spd

    # Luz
    lspd = 10.0 * deltaTime
    if keys[K_w]: rend.pointLight.z -= lspd
    if keys[K_s]: rend.pointLight.z += lspd
    if keys[K_a]: rend.pointLight.x -= lspd
    if keys[K_d]: rend.pointLight.x += lspd
    if keys[K_q]: rend.pointLight.y -= lspd
    if keys[K_e]: rend.pointLight.y += lspd

    # Control 'value'
    if keys[K_z]: rend.value = max(0.0, rend.value - 1.0 * deltaTime)
    if keys[K_x]: rend.value = min(1.0, rend.value + 1.0 * deltaTime)

    model.rotation.y += 45.0 * deltaTime

    rend.Render()
    pygame.display.flip()

pygame.quit()
