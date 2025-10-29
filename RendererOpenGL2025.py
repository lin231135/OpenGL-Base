# RendererOpenGL2025.py  (no borrar este comentario con el nombre del archivo)

import importlib
import pygame
import pygame.display
from pygame.locals import *
import glm

from gl import Renderer
from buffer import Buffer
from model import Model

# Shaders NUEVOS
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

def set_shaders_safe(vs_src, fs_src, label=""):
    try:
        rend.SetShaders(vs_src, fs_src)
        if label: print(f"[OK] Shaders activos → {label}")
    except Exception as e:
        print(f"[ERR] Falló compilación de shaders ({label}):\n{e}")

# Shaders iniciales
currVertexShader   = pulse_vs
currFragmentShader = rim_toon_fs
set_shaders_safe(currVertexShader, currFragmentShader, "VS=Pulse | FS=Rim-Toon")

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

# Utilidades
def is_key(event, *keys):
    return event.key in keys

# ---------------- Loop principal ----------------
isRunning = True
while isRunning:
    deltaTime = clock.tick(60) / 1000.0
    rend.elapsedTime += deltaTime

    for event in pygame.event.get():
        if event.type == QUIT:
            isRunning = False

        elif event.type == KEYDOWN:
            print("KEYDOWN:", event.key)  # DEBUG

            # Toggle fill/wireframe
            if event.key == K_f:
                rend.ToggleFilledMode()
                print("[Info] Toggle Fill/Wireframe")

            # ---------- FRAGMENT SHADERS (1..6) ----------
            if event.key in (K_1, K_KP1):
                currFragmentShader = rim_toon_fs
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("[OK] Shaders activos → VS=var | FS=Rim-Toon")

            elif event.key in (K_2, K_KP2):
                currFragmentShader = gold_metal_fs
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("[OK] Shaders activos → VS=var | FS=Gold-Metal")

            elif event.key in (K_3, K_KP3):
                currFragmentShader = uv_debug_fs
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("[OK] Shaders activos → VS=var | FS=UV-Debug")

            elif event.key in (K_4, K_KP4):
                currFragmentShader = crystal_fs
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("[OK] Shaders activos → VS=var | FS=Crystal")

            elif event.key in (K_5, K_KP5):
                currFragmentShader = pixelate_fs
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("[OK] Shaders activos → VS=var | FS=Pixelate")

            # ---------- VERTEX SHADERS ----------
            elif event.key in (K_6, K_KP6):
                currVertexShader = twist_vs
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("[OK] Shaders activos → VS=Twist | FS=var")

            elif event.key in (K_7, K_KP7):
                currVertexShader = pulse_vs
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("[OK] Shaders activos → VS=Pulse | FS=var")

            elif event.key in (K_8, K_KP8):
                currVertexShader = explode_vs
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("[OK] Shaders activos → VS=Explode | FS=var")

            elif event.key in (K_9, K_KP9):
                currVertexShader = bubble_vs
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("[OK] Shaders activos → VS=Bubble | FS=var")

            elif event.key in (K_0, K_KP0):
                currVertexShader = ripple_vs
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("[OK] Shaders activos → VS=Ripple | FS=var")

            elif event.key == K_MINUS:  # Tecla '-'
                currVertexShader = kaleido_vs
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("[OK] Shaders activos → VS=Kaleido | FS=var")


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
