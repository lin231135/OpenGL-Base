# RendererOpenGL2025.py
# (mantén este comentario con el nombre del archivo)

import pygame
import pygame.display
from pygame.locals import *

import glm

from gl import Renderer
from buffer import Buffer
from model import Model
from vertexShaders import *
from fragmentShaders import *

width = 960
height = 540

deltaTime = 0.0

# --- Init pygame / ventana ---

pygame.display.set_caption("Shaders Lab - CC2018 OpenGL")
screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
clock = pygame.time.Clock()

# --- Renderer y setup básico ---
rend = Renderer(screen)
rend.pointLight = glm.vec3(1, 1, 1)

# Shaders por defecto
currVertexShader = vertex_shader
currFragmentShader = fragment_shader
rend.SetShaders(currVertexShader, currFragmentShader)

# Skybox (asegúrate de que existan estos archivos)
skyboxTextures = [
    "skybox/right.jpg",
    "skybox/left.jpg",
    "skybox/top.jpg",
    "skybox/bottom.jpg",
    "skybox/front.jpg",
    "skybox/back.jpg",
]
rend.CreateSkybox(skyboxTextures)

# --- Modelo principal centrado y al frente de la cámara ---
faceModel = Model("models/Count Batula.obj")

# Carga la(s) textura(s) del MTL automáticamente:
faceModel.AddDiffuseFromMTL(load_all=False)  # o True si quieres todas

# Texturas extra manuales (si las usas en otros shaders):
# faceModel.AddTexture("textures/Robe2.png")
# faceModel.AddTexture("textures/Face.png")

faceModel.position = glm.vec3(0, 0, -5)
faceModel.rotation = glm.vec3(0, 0, 0)
faceModel.scale    = glm.vec3(1, 1, 1)

rend.scene.append(faceModel)


# Ayuda rápida en consola
print("""
=== Shader Switch ===
Fragment   : [1] Base  [2] Toon  [3] Negative  [4] Magma
Vertex     : [7] Base  [8] Fat   [9] Water     [0] Twist
Otros      : [F] Wire/Fill  |  Luz: WASD + Q/E  |  Cam: Flechas
Params     : Z/X = value (0..1)  |  time avanza automáticamente
""")

isRunning = True

while isRunning:

    deltaTime = clock.tick(60) / 1000.0
    rend.elapsedTime += deltaTime

    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                rend.ToggleFilledMode()

            # -------- FRAGMENT SHADERS (1..4) --------
            if event.key == pygame.K_1:
                currFragmentShader = fragment_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_2:
                currFragmentShader = toon_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_3:
                currFragmentShader = negative_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_4:
                currFragmentShader = magma_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            # -------- VERTEX SHADERS (7..0) ----------
            if event.key == pygame.K_7:
                currVertexShader = vertex_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_8:
                currVertexShader = fat_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_9:
                currVertexShader = water_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_0:
                currVertexShader = twist_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

    # --- Movimiento de cámara con flechas ---
    cam_speed = 3.0
    if keys[K_UP]:
        rend.camera.position.z += cam_speed * deltaTime
    if keys[K_DOWN]:
        rend.camera.position.z -= cam_speed * deltaTime
    if keys[K_RIGHT]:
        rend.camera.position.x += cam_speed * deltaTime
    if keys[K_LEFT]:
        rend.camera.position.x -= cam_speed * deltaTime

    # --- Mover luz con WASD+Q/E ---
    light_speed = 10.0
    if keys[K_w]:
        rend.pointLight.z -= light_speed * deltaTime
    if keys[K_s]:
        rend.pointLight.z += light_speed * deltaTime
    if keys[K_a]:
        rend.pointLight.x -= light_speed * deltaTime
    if keys[K_d]:
        rend.pointLight.x += light_speed * deltaTime
    if keys[K_q]:
        rend.pointLight.y -= light_speed * deltaTime
    if keys[K_e]:
        rend.pointLight.y += light_speed * deltaTime

    # --- Parámetro 'value' para vertex shaders (0..1) ---
    if keys[K_z]:
        if rend.value > 0.0:
            rend.value = max(0.0, rend.value - 1.0 * deltaTime)
    if keys[K_x]:
        if rend.value < 1.0:
            rend.value = min(1.0, rend.value + 1.0 * deltaTime)

    # Rotación suave del modelo para apreciar los efectos
    faceModel.rotation.y += 45.0 * deltaTime

    rend.Render()
    pygame.display.flip()

pygame.quit()
