import flet as ft
from ui import MainView

def main(page: ft.Page):
    page.title = "Live Translation"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.spacing = 20

    main_view = MainView(page)
    page.add(main_view)

if __name__ == "__main__":
    ft.run(main)
