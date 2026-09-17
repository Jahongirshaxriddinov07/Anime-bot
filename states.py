from aiogram.fsm.state import StatesGroup, State

class Registration(StatesGroup):
    name = State()
    phone = State()

class AdminState(StatesGroup):
    add_anime_code = State()
    add_anime_file = State()
    add_anime_title = State()
    broadcast = State()
    add_channel_id = State()
    add_channel_url = State()
