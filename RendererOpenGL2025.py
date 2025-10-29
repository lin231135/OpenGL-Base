# RendererOpenGL2025.py
import importlib
import vertexShaders
import pygame
import pygame.display
from pygame.locals import *
import glm

from gl import Renderer
from buffer import Buffer
from model import Model
from vertexShaders import *
print("earth_shader" in globals())
0
from fragmentShaders import *

# ---------------- Configuración de ventana ----------------
width = 960
height = 540

deltaTime = 0.0
screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
clock = pygame.time.Clock()

# ---------------- Renderer principal ----------------
rend = Renderer(screen)
rend.pointLight = glm.vec3(1, 1, 1)

currVertexShader = vertex_shader
currFragmentShader = fragment_shader
rend.SetShaders(currVertexShader, currFragmentShader)

# ---------------- Skybox ----------------
skyboxTextures = [
    "skybox/right.jpg",
    "skybox/left.jpg",
    "skybox/top.jpg",
    "skybox/bottom.jpg",
    "skybox/front.jpg",
    "skybox/back.jpg"
]
rend.CreateSkybox(skyboxTextures)

# ---------------- Modelo Pac-Man ----------------
pacmanModel = Model("models/pacman.obj")
pacmanModel.position = glm.vec3(0, -1.5, -3)
pacmanModel.scale = glm.vec3(0.2, 0.2, 0.2)

rend.scene.append(pacmanModel)


# ---------------- Loop principal ----------------
isRunning = True
while isRunning:

    deltaTime = clock.tick(60) / 1000
    rend.elapsedTime += deltaTime

    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                rend.ToggleFilledMode()

            # Cambiar fragment shaders
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

            # Cambiar vertex shaders
            if event.key == pygame.K_7:
                currVertexShader = vertex_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_8:
                currVertexShader = fat_shader
                rend.SetShaders(currVertexShader, currFragmentShader)

            if event.key == pygame.K_0:
                importlib.reload(vertexShaders)  
                currVertexShader = vertexShaders.earth_shader
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("Shader Tierra recargado y activado")

            if event.key == pygame.K_9:
                currVertexShader = melt_shader
                rend.SetShaders(currVertexShader, currFragmentShader)
                print("Shader Melt activado")


    # ---------------- Movimiento cámara ----------------
    if keys[K_UP]:
        rend.camera.position.z += 1 * deltaTime
    if keys[K_DOWN]:
        rend.camera.position.z -= 1 * deltaTime
    if keys[K_RIGHT]:
        rend.camera.position.x += 1 * deltaTime
    if keys[K_LEFT]:
        rend.camera.position.x -= 1 * deltaTime

    # ---------------- Movimiento luz ----------------
    if keys[K_w]:
        rend.pointLight.z -= 10 * deltaTime
    if keys[K_s]:
        rend.pointLight.z += 10 * deltaTime
    if keys[K_a]:
        rend.pointLight.x -= 10 * deltaTime
    if keys[K_d]:
        rend.pointLight.x += 10 * deltaTime
    if keys[K_q]:
        rend.pointLight.y -= 10 * deltaTime
    if keys[K_e]:
        rend.pointLight.y += 10 * deltaTime

    # ---------------- Control del valor uniform ----------------
    if keys[K_z]:
        if rend.value > 0.0:
            rend.value -= 1 * deltaTime
    if keys[K_x]:
        if rend.value < 1.0:
            rend.value += 1 * deltaTime

    # ---------------- Animación ----------------
    pacmanModel.rotation.y += 45 * deltaTime

    # ---------------- Render ----------------
    rend.Render()
    pygame.display.flip()

pygame.quit()
