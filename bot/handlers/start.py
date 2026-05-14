from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.i18n import load, t
from bot.keyboards.inline import language_keyboard, mode_keyboard
from bot.states import LangStates

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(LangStates.choosing_language)
    await message.answer(
        "👋 Assalomu alaykum! / Привет! / Hello!\n\n"
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=language_keyboard(),
    )


@router.callback_query(F.data.startswith("lang:"), LangStates.choosing_language)
async def cb_language(call: CallbackQuery, state: FSMContext) -> None:
    lang = call.data.split(":")[1]
    await state.update_data(lang=lang)
    await state.set_state(LangStates.choosing_mode)

    strings = load(lang)
    await call.message.edit_text(
        strings["welcome"] + "\n\n" + strings["mode_prompt"],
        reply_markup=mode_keyboard(strings),
    )


@router.callback_query(F.data == "menu:main")
async def cb_back_to_menu(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.set_state(LangStates.choosing_mode)

    strings = load(lang)
    await call.message.edit_text(
        strings["mode_prompt"],
        reply_markup=mode_keyboard(strings),
    )


@router.callback_query(F.data == "cancel")
async def cb_cancel(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.clear()
    await call.message.edit_text(t(lang, "cancelled"))
