from aiogram.fsm.state import State, StatesGroup


class LangStates(StatesGroup):
    choosing_language = State()
    choosing_mode = State()


class QuickStates(StatesGroup):
    waiting_for_prompt = State()


class WizardStates(StatesGroup):
    asking_topic = State()
    asking_slides = State()
    asking_slides_custom = State()
    asking_grade = State()
    asking_tone = State()
