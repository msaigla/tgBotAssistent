from aiogram.fsm.state import StatesGroup, State


class CreateUserFSM(StatesGroup):
    name = State()
    gender = State()
    city = State()
    where_practicing = State()
    were_clients = State()
    massage_technique = State()
    using_social = State()
    finish = State()
