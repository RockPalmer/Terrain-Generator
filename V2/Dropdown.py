import pygame

class Dropdown:
    def __init__(self, x, y, width, height, options):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected = options[0]
        self.open = False
        self.font = pygame.font.SysFont(None, 30)

        self.option_height = 30
        self.scroll_offset = 0

        # Maximum number of options visible at once
        self.max_visible = 5

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:

            # Open/close dropdown
            if self.rect.collidepoint(event.pos):
                self.open = not self.open
                self.scroll_offset = 0
                return

            if self.open:
                # Mouse wheel
                if event.button == 4:  # Scroll up
                    self.scroll_offset = max(0, self.scroll_offset - 1)

                elif event.button == 5:  # Scroll down
                    max_scroll = max(
                        0,
                        len(self.options) - self.max_visible
                    )
                    self.scroll_offset = min(
                        max_scroll,
                        self.scroll_offset + 1
                    )

                # Select an option
                elif event.button == 1:
                    dropdown_rect = pygame.Rect(
                        self.rect.x,
                        self.rect.y + self.rect.height,
                        self.rect.width,
                        self.option_height * self.max_visible
                    )

                    if dropdown_rect.collidepoint(event.pos):

                        # Convert mouse position to option index
                        relative_y = (
                            event.pos[1]
                            - dropdown_rect.y
                        )

                        visible_index = relative_y // self.option_height
                        option_index = (
                            self.scroll_offset + visible_index
                        )

                        if option_index < len(self.options):
                            self.selected = self.options[option_index]
                            self.open = False

                    else:
                        # Clicked outside dropdown
                        self.open = False

        # Handle mouse wheel using pygame 2's MOUSEWHEEL event
        elif event.type == pygame.MOUSEWHEEL and self.open:

            mouse_pos = pygame.mouse.get_pos()

            dropdown_rect = pygame.Rect(
                self.rect.x,
                self.rect.y + self.rect.height,
                self.rect.width,
                self.option_height * self.max_visible
            )

            if dropdown_rect.collidepoint(mouse_pos):
                max_scroll = max(
                    0,
                    len(self.options) - self.max_visible
                )

                self.scroll_offset -= event.y
                self.scroll_offset = max(
                    0,
                    min(self.scroll_offset, max_scroll)
                )

        return False

    def draw(self, screen):
        # Draw main button
        color = (200, 200, 200) if not self.open else (150, 150, 150)

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 1)

        text = self.font.render(
            self.selected,
            True,
            (0, 0, 0)
        )

        screen.blit(
            text,
            (self.rect.x + 10, self.rect.y + 10)
        )

        if self.open:

            # Number of options that can actually be displayed
            visible_count = min(
                self.max_visible,
                len(self.options)
            )

            dropdown_height = (
                visible_count * self.option_height
            )

            dropdown_rect = pygame.Rect(
                self.rect.x,
                self.rect.y + self.rect.height,
                self.rect.width,
                dropdown_height
            )

            # Draw dropdown background
            pygame.draw.rect(
                screen,
                (255, 255, 255),
                dropdown_rect
            )

            pygame.draw.rect(
                screen,
                (0, 0, 0),
                dropdown_rect,
                1
            )

            # Draw visible options
            for i in range(visible_count):

                option_index = self.scroll_offset + i

                if option_index >= len(self.options):
                    break

                opt = self.options[option_index]

                y_pos = (
                    dropdown_rect.y
                    + i * self.option_height
                )

                opt_rect = pygame.Rect(
                    self.rect.x,
                    y_pos,
                    self.rect.width,
                    self.option_height
                )

                pygame.draw.rect(
                    screen,
                    (255, 255, 255),
                    opt_rect
                )

                pygame.draw.rect(
                    screen,
                    (0, 0, 0),
                    opt_rect,
                    1
                )

                txt = self.font.render(
                    opt,
                    True,
                    (0, 0, 0)
                )

                screen.blit(
                    txt,
                    (opt_rect.x + 10, opt_rect.y + 5)
                )


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    clock = pygame.time.Clock()

    dropdown = Dropdown(
        x = 50,
        y = 50,
        width = 200,
        height = 40,
        options = [
            "Option 1",
            "Option 2",
            "Option 3",
            "Option 4",
            "Option 5",
            "Option 6",
            "Option 7",
            "Option 8",
            "Option 9",
            "Option 10",
            "Option 11",
            "Option 12",
        ]
    )

    running = True

    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            dropdown.handle_event(event)

        screen.fill((240, 240, 240))

        dropdown.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
