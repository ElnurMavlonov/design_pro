import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.i18n import load, t

logger = logging.getLogger(__name__)
from bot.keyboards.inline import (
    back_to_menu_keyboard,
    grade_keyboard,
    slides_keyboard,
    tone_keyboard,
)
from bot.states import LangStates, WizardStates
from core.claude import generate_presentation
from core.pptx_gen import build_pptx, slugify
from core.prompts import build_wizard_prompt

router = Router()


@router.callback_query(F.data == "mode:wizard", LangStates.choosing_mode)
async def cb_wizard_start(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.set_state(WizardStates.asking_topic)
    await call.message.edit_text(t(lang, "wizard_topic"))


@router.message(WizardStates.asking_topic)
async def handle_topic(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(topic=message.text)
    await state.set_state(WizardStates.asking_slides)
    await message.answer(
        t(lang, "wizard_slides"),
        reply_markup=slides_keyboard(load(lang)),
    )


@router.callback_query(F.data.startswith("slides:"), WizardStates.asking_slides)
async def cb_slides(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    value = call.data.split(":")[1]

    if value == "custom":
        await state.set_state(WizardStates.asking_slides_custom)
        await call.message.edit_text(t(lang, "slides_custom_ask"))
        return

    await state.update_data(slides=int(value))
    await state.set_state(WizardStates.asking_grade)
    await call.message.edit_text(
        t(lang, "wizard_grade"),
        reply_markup=grade_keyboard(load(lang)),
    )


@router.message(WizardStates.asking_slides_custom)
async def handle_slides_custom(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")

    try:
        count = int(message.text.strip())
        if not (3 <= count <= 20):
            raise ValueError
    except ValueError:
        await message.answer(
            t(lang, "slides_invalid"),
            reply_markup=slides_keyboard(load(lang)),
        )
        await state.set_state(WizardStates.asking_slides)
        return

    await state.update_data(slides=count)
    await state.set_state(WizardStates.asking_grade)
    await message.answer(
        t(lang, "wizard_grade"),
        reply_markup=grade_keyboard(load(lang)),
    )


@router.callback_query(F.data.startswith("grade:"), WizardStates.asking_grade)
async def cb_grade(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    grade = call.data.split(":")[1]
    await state.update_data(grade=grade)
    await state.set_state(WizardStates.asking_tone)
    await call.message.edit_text(
        t(lang, "wizard_tone"),
        reply_markup=tone_keyboard(load(lang)),
    )


@router.callback_query(F.data.startswith("tone:"), WizardStates.asking_tone)
async def cb_tone(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("lang", "uz")
    tone = call.data.split(":")[1]
    await state.update_data(tone=tone)

    strings = load(lang)
    status_msg = await call.message.edit_text(strings["generating"])

    topic = data.get("topic", "")
    slides = data.get("slides", 5)
    grade = data.get("grade", "middle")

    try:
        user_prompt = build_wizard_prompt(topic, slides, grade, tone, lang)
        slide_data = await generate_presentation(user_prompt)
        pptx_buffer = build_pptx(slide_data)

        filename = slugify(slide_data.get("title", topic)) + ".pptx"

        await status_msg.delete()
        await call.message.answer_document(
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
