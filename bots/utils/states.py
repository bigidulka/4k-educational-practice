from aiogram.fsm.state import StatesGroup, State

class CurrencySelection(StatesGroup):
    waiting_for_base_currency = State()
    waiting_for_quote_currency = State()

class SearchStocks(StatesGroup):
    waiting_for_search_query = State()

class ChartTimeframe(StatesGroup):
    waiting_for_timeframe_selection = State()

class SetAlert(StatesGroup):
    waiting_for_alert_type = State()
    waiting_for_price_input = State()
