# button.py
import pygame

# Create system cursor objects for default and hand pointers.
arrow_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
hand_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)

class Button:
    def __init__(self, text, x, y, width, height, font,
                 normal_color=(235, 153, 176), hover_color=(223, 130, 155),
                 border_color=(255, 255, 255), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.border_color = border_color
        self.text_color = text_color
        self.text_image = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_image.get_rect(center=self.rect.center)

    def draw(self, surface):
        # Only decide the current color here; remove the call to pygame.mouse.set_cursor()
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            current_color = self.hover_color
        else:
            current_color = self.normal_color

        pygame.draw.rect(surface, current_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        
        self.text_image = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_image.get_rect(center=self.rect.center)
        surface.blit(self.text_image, self.text_rect)


    def is_clicked(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    return True
        return False