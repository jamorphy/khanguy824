import pygame
import sys
import random
from openai import OpenAI
import os
import json

colormap = {
    'r': (255, 0, 0),
    'o': (255, 165, 0),
    'y': (255, 255, 0),
    'g': (0, 255, 0),
    'b': (0, 0, 255),
    'p': (128, 0, 128),
    'w': (255, 255, 255),
    'l': (0, 0, 0)
}

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

msgs = []
# Screen dimensions
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("khanguy824")
pygame.font.init()
font = pygame.font.Font(None, 20)
block_size = 20
grid_size = 16

grid = "bbbbbbbbbbbbbbbbbbwbbbbbbbbbwbbbbpppbbbbbbpppbbbpppppbbbpppppbbgggpppgggggpppggggggggggggggggggggggrrrrrrgggggggggggooooooogggggggggowoowogggggggggooooooooggggggggllllllllggggggglllllllllllggggllllllllllllggyyllllllllllllyyyyyyyllllllllllyyyyyyyyyyyyyyyyyy"

input_box = pygame.Rect(10, 430, 300, 40)
active = False
text = ''
color = colormap['w']

# LLM output box
output_box = pygame.Rect(10, 330, 300, 30)
llm_output = 'Great Khan. Our forces are dwindling. I have failed you. Take my sword. I deserve death.'
desc_text = "sad_soldier"

def load_system_prompt():
    try:
        with open('system.txt', 'r') as f:
            raw = f.read()
            return raw
    except:
        print('Could not load sysprompt')
        exit(1)

sysprompt = load_system_prompt()
msgs.append({"role": "system", "content": sysprompt})

def send_msg(user_input):
    msgs.append({"role": "user", "content": user_input})
    completion = client.chat.completions.create(
        messages=msgs,
        model="gpt-4-turbo",
    )

    response = completion.choices[0].message.content
    print(response)

    return json.loads(response)

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    return lines


# Update the draw_grid function to use the colormap
def draw_grid():
    for i, color_key in enumerate(grid):
        x = i % 16
        y = i // 16
        rect = pygame.Rect(x * block_size, y * block_size, block_size, block_size)
        if color_key in colormap:
            color = colormap[color_key]
            pygame.draw.rect(screen, color, rect)

# Initialize Pygame
pygame.init()

while not None:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect
            if input_box.collidepoint(event.pos):
                # Toggle the active variable
                active = not active
            else:
                active = False
                # Change the current color of the input box
            color = colormap['g'] if active else colormap['w']
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    res = send_msg(text)
                    llm_output = res['text']
                    grid = res['world']
                    desc_text = res['world_desc']
                    text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode


    # Render                     
    screen.fill((0, 0, 0))
    draw_grid()
    
    top_output_box = pygame.Rect(10, 10, 300, 30)
    s = pygame.Surface((top_output_box.width, top_output_box.height))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    screen.blit(s, (top_output_box.x, top_output_box.y))

    top_output_surface = font.render(desc_text, True, colormap['w'])
    screen.blit(top_output_surface, (top_output_box.x + 5, top_output_box.y + 5))

    txt_surface = font.render(text, True, color)
    width = max(300, txt_surface.get_width() + 10)
    input_box.w = width
    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    pygame.draw.rect(screen, color, input_box, 2)

    wrapped_output = wrap_text(llm_output, font, output_box.width - 10)
    y_offset = 0
    for line in wrapped_output:
        llm_output_surface = font.render(line, True, colormap['w'])
        screen.blit(llm_output_surface, (output_box.x + 5, output_box.y + 5 + y_offset))
        y_offset += font.get_linesize()

    output_box.height = max(30, y_offset + 10)

    # Refresh the screen
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
