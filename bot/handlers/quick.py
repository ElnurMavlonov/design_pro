import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.i18n import load, t

logger = logging.getLogger(__name__)
from bot.keyboards.inline import back_to_menu_keyboard
from bot.states import LangStates, QuickStates
from core.claude import generate_presentation
from core.pptx_gen import build_pptx, slugify
from core.prompts import build_quick_prompt

router = Router()


@router.callback_query(F.data == "mode:quick", LangStates.choosing_mode)
async def cb_quick_mode(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.set_state(QuickStates.waiting_for_prompt)
    await call.message.edit_text(
        t(lang, "quick_ask"),
        parse_mode="HTML",
    )


@router.message(QuickStates.waiting_for_prompt)
async def handle_quick_prompt(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    strings = load(lang)

    status_msg = await message.answer(strings["generating"])

    try:
        user_prompt = build_quick_prompt(message.text, lang)
        slide_data = await generate_presentation(user_prompt)
        pptx_buffer = build_pptx(slide_data)

        filename = slugify(slide_data.get("title", "presentation")) + ".pptx"

        await status_msg.delete()
        await message.answer_document(
            document=BufferedInputFile(pptx_buffer.read(), filename=filename),
            caption=strings["done"],
            reply_markup=back_to_menu_keyboard(strings),
        )
    except Exception as e:
        logger.exception("Failed to generate presentation: %s", e)
        await status_msg.edit_text(
            strings["error"],
            reply_markup=back_to_menu_keyboard(strings),
        )

    await state.set_state(LangStates.choosing_mode)
