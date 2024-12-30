from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
W_Width, W_Height = 450, 750

car1 = {'x': -150, 'y': -W_Height // 2 + 20, 'speed': 5}
car2 = {'x': 150, 'y': -W_Height // 2 + 20, 'speed': 5}
car_width = 0
car_height = 0

rain_drops = []
rain_speed = 10
rain_active = False
rain_start_frame = 0
rain_stop_frame = 0

middle_lines = [W_Height // 2 - 95 * i for i in range(10)]
middle_line_speed = 1
frame_count = 0

obstacle_cars = []
obstacle_cars_speed = 1
spawn_interval = 350
obstacle_car_frame_count = 0

falling_coins = []
coin_radius = 15
special_coin_radius = 20
coin_speed = 1
coin_spawn_interval = 200
coin_frame_count = 0

score_red = 0
score_blue = 0
red_lives = 3
blue_lives = 3
red_lives_circles = [(-210, 357), (-180, 357), (-150, 357)]
blue_lives_circles = [(147, 357), (177, 357), (207, 357)]
lives_circles_radius = 12

target_score = 2
game_over = False
paused = False

red_message_duration_frames = 90
red_message_timer = False
blue_message_duration_frames = 90
blue_message_timer = False
button_width, button_height = 20, 20
terminate_button_pos = (W_Width // 2 - 225, W_Height // 2 - 35)

def spawn_obstacle_car():
    x_positions = [-W_Width // 3, 0, W_Width // 3]
    x = random.choice(x_positions)
    y = W_Height // 2 + 30
    obstacle_cars.append({'x': x, 'y': y})
    
def update_obstacle_cars():
    global obstacle_cars, obstacle_cars_speed, obstacle_car_frame_count, spawn_interval
    for car in obstacle_cars:
        car['y'] -= obstacle_cars_speed
    obstacle_cars = [car for car in obstacle_cars if car['y'] > -W_Height // 2 - car_height]

    dynamic_spawn_interval = max(100, int(spawn_interval / obstacle_cars_speed))
    obstacle_car_frame_count += 1
    if obstacle_car_frame_count >= dynamic_spawn_interval:
        spawn_obstacle_car()
        obstacle_car_frame_count = 0
        

def InitializeRaining():
    global rain_drops
    rain_drops = [[random.randint(-W_Width // 2, W_Width // 2), random.randint(-W_Height // 2, W_Height // 2)]
        for drops in range(160)]
    
def RainDrops():
    global rain_drops
    glColor3f(0.7, 0.7, 1.0)

    glBegin(GL_LINES)
    for drop in rain_drops:
        x, y = drop
        glVertex2f(x, y)
        glVertex2f(x, y - 10)
    glEnd()
        
def find_zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) >= abs(dy):
        if dx >= 0 and dy >= 0:
            return 0
        elif dx <= 0 <= dy:
            return 3
        elif dx <= 0 and dy <= 0:
            return 4
        else:
            return 7
    else:
        if dx >= 0 and dy >= 0:
            return 1
        elif dx <= 0 <= dy:
            return 2
        elif dx <= 0 and dy <= 0:
            return 5
        else:
            return 6


def convert_to_zone_zero(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    elif zone == 7:
        return x, -y


def convert_to_original_zone(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    elif zone == 7:
        return x, -y


def draw_line(x1, y1, x2, y2):
    zone = find_zone(x1, y1, x2, y2)
    x1, y1 = convert_to_zone_zero(x1, y1, zone)
    x2, y2 = convert_to_zone_zero(x2, y2, zone)

    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    incrE = 2 * dy
    incrNE = 2 * (dy - dx)

    x, y = x1, y1
    glBegin(GL_POINTS)
    while x <= x2:
        original_x, original_y = convert_to_original_zone(x, y, zone)
        glVertex2f(original_x, original_y)
        if d > 0:
            y += 1
            d += incrNE
        else:
            d += incrE
        x += 1
    glEnd()

def spawn_coins():
    
    coin_type = "special" if random.random() < 0.09 else "normal"
    x = random.randint(-W_Width // 2 + coin_radius, W_Width // 2 - coin_radius)
    y = W_Height // 2 + coin_radius
    falling_coins.append({'x': x, 'y': y, 'type': coin_type})
    
def draw_lives(cx, cy, r, color):
    x, y = 0, r
    d = 1 - r
    glColor3f(color[0], color[1], color[2])
    glBegin(GL_POINTS)
    while x <= y:
        glVertex2f(cx + x, cy + y)
        glVertex2f(cx - x, cy + y)
        glVertex2f(cx + x, cy - y)
        glVertex2f(cx - x, cy - y)
        glVertex2f(cx + y, cy + x)
        glVertex2f(cx - y, cy + x)
        glVertex2f(cx + y, cy - x)
        glVertex2f(cx - y, cy - x)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
    glEnd()

    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy < (r * r):
                glColor3f(color[0], color[1], color[2])
                glBegin(GL_POINTS)
                glVertex2f(cx + dx, cy + dy)
                glEnd()
                
def draw_coin(cx, cy, r, coin_type):
    x, y = 0, r
    d = 1 - r
    
    if coin_type == "special":
        glColor3f(0.3, 0.5, 0.2)
    else:
        glColor3f(0.5, 0.3, 0.1)
    glBegin(GL_POINTS)
    while x <= y:
        glVertex2f(cx + x, cy + y)
        glVertex2f(cx - x, cy + y)
        glVertex2f(cx + x, cy - y)
        glVertex2f(cx - x, cy - y)
        glVertex2f(cx + y, cy + x)
        glVertex2f(cx - y, cy + x)
        glVertex2f(cx + y, cy - x)
        glVertex2f(cx - y, cy - x)
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1
    glEnd()

    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            if dx * dx + dy * dy < ((r * r) - 90):
                if coin_type == "special":
                    glColor3f(0.6, 0.7, 0.6)
                else:
                    glColor3f(0.8, 0.5, 0.2)
                glBegin(GL_POINTS)
                glVertex2f(cx + dx, cy + dy)
                glEnd()
            elif (r * r) > dx * dx + dy * dy >= ((r * r) - 90):
                if coin_type == "special":
                    glColor3f(0.3, 0.5, 0.2)
                else:
                    glColor3f(0.5, 0.3, 0.1)
                glBegin(GL_POINTS)
                glVertex2f(cx + dx, cy + dy)
                glEnd()


def update_coins():
    global falling_coins, coin_frame_count, coin_speed, coin_spawn_interval, score_red, score_blue
    for circle in falling_coins:
        circle['y'] -= coin_speed
        
    remaining_coins = []
    for coin in falling_coins:
        if is_coin_collision(car1, coin):
            if coin['type'] == "normal":
                score_red += 1
            else:
                score_red += 5
        elif is_coin_collision(car2, coin):
            if coin['type'] == "normal":
                score_blue += 1
            else:
                score_blue += 5
        else:
            remaining_coins.append(coin)
    falling_coins = remaining_coins
    falling_coins = [circle for circle in falling_coins if circle['y'] > -W_Height // 2 - coin_radius]
    
    coin_frame_count += 1
    if coin_frame_count >= coin_spawn_interval:
        spawn_coins()
        coin_frame_count = 0


def draw_car(x, y, color):
    global car_width, car_height
    glColor3f(color[0], color[1], color[2])
    body_width = 76
    body_height = 86
    body_bottom = y
    body_top = body_bottom + body_height
    draw_line(x - (body_width // 2) + 5, body_bottom - 15, x + (body_width // 2) - 5, body_bottom - 15)
    draw_line(x - body_width // 2, body_bottom, x - body_width // 2, body_top + 25)
    draw_line(x + body_width // 2, body_bottom, x + body_width // 2, body_top + 25)
    
    draw_line(x - body_width // 2 + 7, body_top + 5, x + body_width // 2 - 7, body_top + 5)
    draw_line(x - body_width // 2 + 10, body_top + 35, x + body_width // 2 - 10, body_top + 35)
    
    draw_line(x - body_width // 2, body_top + 25, x - body_width // 2 + 10, body_top + 35)
    draw_line(x + body_width // 2, body_top + 25, x + body_width // 2 - 10, body_top + 35)
        
    draw_line(x - (body_width // 2) + 5, body_bottom - 15, x - (body_width // 2), body_bottom)
    draw_line(x + (body_width // 2) - 5, body_bottom - 15, x + (body_width // 2), body_bottom)
    draw_line(x - (body_width // 2) + 15, body_bottom, x + (body_width // 2) - 15, body_bottom)
    draw_line(x - (body_width // 2) + 10, body_bottom - 10, x + (body_width // 2) - 10, body_bottom - 10)
    
    draw_line(x - (body_width // 2) + 15, body_bottom, x - (body_width // 2) + 10, body_bottom - 10)
    draw_line(x + (body_width // 2) - 15, body_bottom, x + (body_width // 2) - 10, body_bottom - 10)         

    draw_line(x - (body_width // 2) + 15, body_top - 15, x + (body_width // 2) - 15, body_top - 15)
    
    draw_line(x - (body_width // 2) + 7, body_top + 5, x - (body_width // 2) + 15, body_top - 15)
    draw_line(x + (body_width // 2) - 7, body_top + 5, x + (body_width // 2) - 15, body_top - 15)
    
    draw_line(x + (body_width // 2) - 5, body_top, x + (body_width // 2) - 5, body_bottom - 5)
    draw_line(x - (body_width // 2) + 5, body_top, x - (body_width // 2) + 5, body_bottom - 5)
    
    draw_line(x - (body_width // 2) + 15, body_top - 20, x - (body_width // 2) + 15, body_bottom + 5)
    draw_line(x + (body_width // 2) - 15, body_top - 20, x + (body_width // 2) - 15, body_bottom + 5)

    draw_line(x + (body_width // 2) - 15, body_top - 20, x + (body_width // 2) - 5, body_top)    
    draw_line(x - (body_width // 2) + 15, body_top - 20, x - (body_width // 2) + 5, body_top)
    
    draw_line(x + (body_width // 2) - 15, body_bottom + 5, x + (body_width // 2) - 5, body_bottom - 5)    
    draw_line(x - (body_width // 2) + 15, body_bottom + 5, x - (body_width // 2) + 5, body_bottom - 5)    
    car_width = 76
    car_height = 86 + 35 - (-15)
    
def draw_dividers():
    line_width = 4
    glColor3f(0.8, 0.8, 0.8) 

    for line_w in range(-line_width // 2, line_width // 2 + 1):
        draw_line(-W_Width // 3 + 75 + line_w, W_Height // 2, -W_Width // 3 + 75 + line_w, -W_Height // 2)

    for line_w in range(-line_width // 2, line_width // 2 + 1):
        draw_line(W_Width // 3 - 75 + line_w, W_Height // 2, W_Width // 3 - 75 + line_w, -W_Height // 2)

def draw_middle_lines():
    line_length = 40
    line_width = 2
    glColor3f(0.8, 0.8, 0.8)

    x_center = 0
    x_left = -W_Width // 3
    x_right = W_Width // 3

    for y in middle_lines:
        for offset in range(-line_width // 2, line_width // 2 + 1):
            draw_line(x_center + offset, y, x_center + offset, y - line_length)
            draw_line(x_left + offset, y, x_left + offset, y - line_length)
            draw_line(x_right + offset, y, x_right + offset, y - line_length)

def draw_buttons():
    glColor3f(1, 1, 0)
    x, y = terminate_button_pos
    draw_terminate_symbol(x, y)

def draw_terminate_symbol(x, y):
    size = 9

    draw_line(x - size, y - size, x + size, y + size)
    draw_line(x - size, y + size, x + size, y - size)


def is_within_button(x, y, button_pos):
    bx, by = button_pos
    return (
        bx - button_width // 2 <= x <= bx + button_width // 2 and
        by - button_height // 2 <= y <= by + button_height // 2
    )
    
keys = set()
def keyboard_listener(key, x, y):
    global keys, paused, game_over, terminate_flag, obstacle_cars, obstacle_cars_speed, falling_coins, coin_speed
    global middle_line_speed, rain_drops, rain_active, frame_count, obstacle_car_frame_count
    global rain_start_frame, rain_stop_frame, coin_frame_count, car1, car2
    global score_red, score_blue, red_lives, blue_lives, red_lives_circles, blue_lives_circles
    global red_message_duration_frames, blue_message_duration_frames, red_message_timer, blue_message_timer
    keys.add(key)
    if key == b'p':
        if not game_over:
            paused = not paused
    elif key == b'r':
        paused =False
        game_over = False
        obstacle_cars = []
        obstacle_cars_speed = 1
        falling_coins = []
        coin_speed = 1
        middle_line_speed = 1
        rain_drops = []
        red_message_duration_frames, blue_message_duration_frames = 90, 90
        red_message_timer, blue_message_timer = False, False
        rain_start_frame, rain_stop_frame, obstacle_car_frame_count, frame_count = 0, 0, 0, 0
        rain_active = False
        update_rain_timing()
        InitializeRaining()
        coin_frame_count, score_red, score_blue, red_lives, blue_lives = 0, 0, 0, 3, 3
        red_lives_circles = [(-210, 357), (-180, 357), (-150, 357)]
        blue_lives_circles = [(147, 357), (177, 357), (207, 357)]
        car1 = {'x': -150, 'y': -W_Height // 2 + 20, 'speed': 5}
        car2 = {'x': 150, 'y': -W_Height // 2 + 20, 'speed': 5}
        

def keyboard_up_listener(key, x, y):
    global keys
    if key in keys:
        keys.remove(key)

def special_key_listener(key, x, y):
    global keys
    keys.add(key)

def special_key_up_listener(key, x, y):
    global keys
    if key in keys:
        keys.discard(key)

def mouse_listener(button, state, x, y):
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        gl_x = x - W_Width // 2
        gl_y = (W_Height // 2 - y)
    if is_within_button(gl_x, gl_y, terminate_button_pos):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glColor3f(1, 0.7, 0)
        render_text(-60, 0, "A D I O S", GLUT_BITMAP_TIMES_ROMAN_24)
        glutSwapBuffers()
        time.sleep(1)
        glutLeaveMainLoop()
        
def is_collision(car1, car2):
    global car_height, car_width
    box1 = {
        'x': car1['x'] - car_width // 2,
        'y': car1['y'] - car_height // 2,
        'width': car_width,
        'height': car_height
    }
    box2 = {
        'x': car2['x'] - car_width // 2,
        'y': car2['y'] - car_height // 2,
        'width': car_width,
        'height': car_height
    }
    return (
        box1['x'] < box2['x'] + box2['width'] and
        box1['x'] + box1['width'] > box2['x'] and
        box1['y'] < box2['y'] + box2['height'] and
        box1['y'] + box1['height'] > box2['y']
    )

def is_coin_collision(car, coin):
    global car_height, car_width
    car_box = {
        'x': car['x'] - car_width // 2,
        'y': car['y'] - 15,
        'width': car_width,
        'height': car_height
    }
    coin_box = {
        'x': coin['x'] - coin_radius,
        'y': coin['y'] - coin_radius,
        'width': 2 * coin_radius,
        'height': 2 * coin_radius
    }
    return (
        car_box['x'] < coin_box['x'] + coin_box['width'] and
        car_box['x'] + car_box['width'] > coin_box['x'] and
        car_box['y'] < coin_box['y'] + coin_box['height'] and
        car_box['y'] + car_box['height'] > coin_box['y']
    )

def handle_movement():
    global car1, car2, obstacle_cars
    
    if b'w' in keys:
        car1['y'] += car1['speed']
    if b's' in keys:
        car1['y'] -= car1['speed']
    if b'a' in keys:
        car1['x'] -= car1['speed']
    if b'd' in keys:
        car1['x'] += car1['speed']

    if GLUT_KEY_UP in keys:
        car2['y'] += car2['speed']
    if GLUT_KEY_DOWN in keys:
        car2['y'] -= car2['speed']
    if GLUT_KEY_LEFT in keys:
        car2['x'] -= car2['speed']
    if GLUT_KEY_RIGHT in keys:
        car2['x'] += car2['speed']

    car1['x'] = max(-W_Width // 2 + (car_width + 10) // 2, min(W_Width // 2 - (car_width + 10) // 2, car1['x']))
    car1['y'] = max(-W_Height // 2 + car_height - 120, min(W_Height // 2 - car_height + 10, car1['y']))
    car2['x'] = max(-W_Width // 2 + (car_width + 10) // 2, min(W_Width // 2 - (car_width + 10) // 2, car2['x']))
    car2['y'] = max(-W_Height // 2 + car_height - 120, min(W_Height // 2 - car_height + 10, car2['y']))

    if is_collision(car1, car2):
        if b'w' in keys:
            car1['y'] -= car1['speed']
        if b's' in keys:
            car1['y'] += car1['speed']
        if b'a' in keys:
            car1['x'] += car1['speed']
        if b'd' in keys:
            car1['x'] -= car1['speed']
        if GLUT_KEY_UP in keys:
            car2['y'] -= car2['speed']
        if GLUT_KEY_DOWN in keys:
            car2['y'] += car2['speed']
        if GLUT_KEY_LEFT in keys:
            car2['x'] += car2['speed']
        if GLUT_KEY_RIGHT in keys:
            car2['x'] -= car2['speed']

def update_rain_timing():
    global rain_start_frame, rain_stop_frame, frame_count
    start_interval = random.randint(500, 1000)
    stop_interval = random.randint(500, 1000)
    rain_start_frame = frame_count + start_interval
    rain_stop_frame = rain_start_frame + stop_interval
    
def render_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(font, ord(char))  

def display():
    global rain_active, red_message_timer, red_message_duration_frames, lives_circles_radius, paused
    global blue_message_timer, blue_message_duration_frames
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluOrtho2D(-W_Width // 2, W_Width // 2, -W_Height // 2, W_Height // 2)
    draw_dividers()
    draw_middle_lines()
    draw_buttons()
    draw_car(car1['x'], car1['y'], (0.7, 0.0, 0.0))
    draw_car(car2['x'], car2['y'], (0.0, 0.7, 1.0))
    if not paused:
        handle_movement()
        update_obstacle_cars()
        update_coins()
    if rain_active:
        RainDrops()
    for lives in red_lives_circles:
        draw_lives(lives[0], lives[1], lives_circles_radius, color=(0.4, 0.1, 0.3))
    for lives in blue_lives_circles:
        draw_lives(lives[0], lives[1], lives_circles_radius, color=(0.2, 0.2, 0.8))       
    for coin in falling_coins:
        if coin['type'] == "special":
            draw_coin(coin['x'], coin['y'], special_coin_radius, coin['type'])
        else:
            draw_coin(coin['x'], coin['y'], coin_radius, coin['type'])

    for car in obstacle_cars:
        draw_car(car['x'], car['y'], (1, 1, 0))


    
    glColor3f(0.2, 0.8, 0.2)    
    render_text(-W_Width // 2 + 160, W_Height // 2 - 20, f"Target Score:{target_score}")    
    glColor3f(0.7, 0.0, 0.0)    
    render_text(-W_Width // 2 + 5, W_Height // 2 - 50, f"Score:{score_red}")
    glColor3f(0.7, 0.0, 0.0)   
    render_text(-W_Width // 2 + 5, W_Height // 2 - 70, f"Lives:{red_lives}")
    glColor3f(0.0, 0.7, 1.0)  
    render_text(W_Width // 2 - 90, W_Height // 2 - 50, f"Score:{score_blue}")
    glColor3f(0.0, 0.7, 1.0)  
    render_text(W_Width // 2 - 90, W_Height // 2 - 70, f"Lives:{blue_lives}")
    if not paused:
        if (target_score // 2) == score_red and red_message_timer is False:
            red_message_timer = True
        if red_message_duration_frames > 0 and red_message_timer is True:
            glColor3f(0.7, 0.0, 0.0)
            render_text(-220, 15, "Red Car Has Reached", GLUT_BITMAP_TIMES_ROMAN_24)
            render_text(-220, -15, "Half of the Target Score", GLUT_BITMAP_TIMES_ROMAN_24)
            red_message_duration_frames -= 1
        if (target_score // 2) == score_blue and blue_message_timer is False:
            blue_message_timer = True
        if blue_message_duration_frames > 0 and blue_message_timer is True:
            glColor3f(0.0, 0.7, 1.0)
            render_text(-30, 15, "Blue Car Has Reached", GLUT_BITMAP_TIMES_ROMAN_24)
            render_text(-30, -15, "Half of the Target Score", GLUT_BITMAP_TIMES_ROMAN_24)
            blue_message_duration_frames -= 1 
    
    glutSwapBuffers()

def animate():
    global rain_drops, rain_speed, middle_lines, middle_line_speed
    global frame_count, rain_active, obstacle_cars_speed, coin_speed
    global red_lives, blue_lives, score_red, score_blue, game_over, paused, terminate_flag
    global red_message_duration_frames, blue_message_duration_frames
    if paused or game_over:
        return
    if rain_active:
        for drop in rain_drops:
            drop[1] -= rain_speed
        rain_drops[:] = [drop for drop in rain_drops if drop[1] > -W_Height // 2]

        while len(rain_drops) < 160:
            new_x = random.randint(-W_Width, W_Width)
            new_y = random.randint((W_Height // 2) + 5, (W_Height // 2) + 20)
            rain_drops.append([new_x, new_y])

    frame_count += 1
    if frame_count == rain_start_frame:
        rain_active = True
    elif frame_count == rain_stop_frame:
        rain_active = False
        update_rain_timing()

    if frame_count % 500 == 0:
        middle_line_speed += 0.7
        obstacle_cars_speed += 0.7
        coin_speed += 0.5
    for i in range(len(middle_lines)):
        middle_lines[i] -= middle_line_speed
        if middle_lines[i] < -W_Height // 2:
            middle_lines[i] = W_Height // 2 + 90

    for obstacle in obstacle_cars:
        if is_collision(car1, obstacle):
            if not obstacle.get('collided_car1', False):
                red_lives -= 1
                red_lives_circles.pop()
                obstacle['collided_car1'] = True
        else:
            obstacle['collided_car1'] = False

        if is_collision(car2, obstacle):
            if not obstacle.get('collided_car2', False):
                blue_lives -= 1
                blue_lives_circles.pop()
                obstacle['collided_car2'] = True
        else:
            obstacle['collided_car2'] = False
    if score_red >= target_score:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glColor3f(0.7, 0.0, 0.0)
        render_text(-74, 15, "Congratulations!", GLUT_BITMAP_TIMES_ROMAN_24)
        render_text(-71, -15, "Red Car Wins!", GLUT_BITMAP_TIMES_ROMAN_24)
        glutSwapBuffers()
        time.sleep(1)
        glutLeaveMainLoop()
    if score_blue >= target_score:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glColor3f(0.0, 0.7, 1.0)
        render_text(-74, 15, "Congratulations!", GLUT_BITMAP_TIMES_ROMAN_24)
        render_text(-71, -15, "Blue Car Wins!", GLUT_BITMAP_TIMES_ROMAN_24)   
        glutSwapBuffers()
        time.sleep(1)
        glutLeaveMainLoop()
    if blue_lives == 0:
        game_over = True
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glColor3f(0.7, 0.0, 0.0)
        render_text(-72, 15, "Game Over!", GLUT_BITMAP_TIMES_ROMAN_24)        
        render_text(-76, -15, "Red Car Wins!", GLUT_BITMAP_TIMES_ROMAN_24)
        glutSwapBuffers()
        time.sleep(1)
        glutLeaveMainLoop()

    if red_lives == 0:
        game_over = True    
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glColor3f(0.0, 0.7, 1.0)
        render_text(-72, 15, "Game Over!", GLUT_BITMAP_TIMES_ROMAN_24)        
        render_text(-76, -15, "Blue Car Wins!", GLUT_BITMAP_TIMES_ROMAN_24)
        glutSwapBuffers()
        time.sleep(1)
        glutLeaveMainLoop()
    glutPostRedisplay()


def main():
    glutInit()
    InitializeRaining()
    update_rain_timing()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(W_Width, W_Height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Turbo Road Rivals")
    glClearColor(0.1, 0.1, 0.1, 1.0)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_listener)
    glutKeyboardUpFunc(keyboard_up_listener)    
    glutSpecialFunc(special_key_listener)
    glutSpecialUpFunc(special_key_up_listener)
    glutMouseFunc(mouse_listener)  
    glutIdleFunc(animate)
    glutMainLoop()


if __name__ == "__main__":
    main()
