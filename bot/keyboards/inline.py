from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang:uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
    )
    return builder.as_markup()


def mode_keyboard(t: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t["mode_quick"], callback_data="mode:quick"))
    builder.row(InlineKeyboardButton(text=t["mode_wizard"], callback_data="mode:wizard"))
    return builder.as_markup()


def slides_keyboard(t: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t["slides_5"], callback_data="slides:5"),
        InlineKeyboardButton(text=t["slides_10"], callback_data="slides:10"),
        InlineKeyboardButton(text=t["slides_15"], callback_data="slides:15"),
    )
    builder.row(InlineKeyboardButton(text=t["slides_custom"], callback_data="slides:custom"))
    builder.row(InlineKeyboardButton(text=t["cancel"], callback_data="cancel"))
    return builder.as_markup()


def grade_keyboard(t: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t["grade_primary"], callback_data="grade:primary"),
        InlineKeyboardButton(text=t["grade_middle"], callback_data="grade:middle"),
    )
    builder.row(
        InlineKeyboardButton(text=t["grade_high"], callback_data="grade:high"),
        InlineKeyboardButton(text=t["grade_university"], callback_data="grade:university"),
    )
    builder.row(InlineKeyboardButton(text=t["cancel"], callback_data="cancel"))
    return builder.as_markup()


def tone_keyboard(t: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t["tone_formal"], callback_data="tone:formal"),
        InlineKeyboardButton(text=t["tone_simple"], callback_data="tone:simple"),
        InlineKeyboardButton(text=t["tone_fun"], callback_data="tone:fun"),
    )
    builder.row(InlineKeyboardButton(text=t["cancel"], callback_data="cancel"))
    return builder.as_markup()


def back_to_menu_keyboard(t: dict) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t["back_to_menu"], callback_data="menu:main"))
    return builder.as_markup()
