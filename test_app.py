import flet as ft
from src.ui import MainView

def main(page: ft.Page):
    main_view = MainView(page)
    page.add(main_view)

ft.run(main, port=8550, view=ft.AppView.WEB_BROWSER)

