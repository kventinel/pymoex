import typing as T

import dataclasses
import datetime

from . import boards
from . import tickers
from . import utils


@dataclasses.dataclass
class Candle:
    date: datetime.date
    low: float
    high: float
    open: float
    close: float
    mid_price: float
    numtrades: int
    volume: int
    value: float

    @classmethod
    def merge(cls, first: 'Candle', second: 'Candle'):
        assert first.date == second.date
        return cls(
            date=first.date,
            low=min(first.low, second.low),
            high=max(first.high, second.high),
            open=(first.open + second.open) / 2,
            close=(first.close + second.close) / 2,
            mid_price=(first.mid_price + second.mid_price) / 2,
            numtrades=first.numtrades + second.numtrades,
            volume=first.volume + second.volume,
            value=first.value + second.value,
        )


class Candles(list[Candle]):
    def __init__(
        self,
        ticker: tickers.Ticker,
        start_date: T.Optional[datetime.date] = None,
        end_date: T.Optional[datetime.date] = None,
        only_main_board: bool = True,
    ):
        if not only_main_board:
            candles = []
            for board in ticker.boards:
                candles.append(_parse_candles(ticker, board, start_date=start_date, end_date=end_date))
            for idx in range(1, len(candles)):
                candles[0] = _merge_candles(candles[0], candles[idx])
            self.extend(candles[0])
        else:
            board = boards.get_main_board(ticker.boards)
            self.extend(_parse_candles(ticker, board, start_date=start_date, end_date=end_date))


def _parse_candles(
    ticker: tickers.Ticker,
    board: str,
    start_date: T.Optional[datetime.date] = None,
    end_date: T.Optional[datetime.date] = None,
) -> list[Candle]:
    result = []
    while True:
        start_str = f"?from={start_date.isoformat()}" if start_date else ""
        response = utils.json_api_call(
            f"https://iss.moex.com/iss/history/engines/stock/markets/{ticker.market}/boards/{board}/"
            f"securities/{ticker.secid}.json{start_str}"
        )
        history = response["history"]
        columns = history["columns"]
        data = history["data"]
        for line in data:
            date = datetime.date.fromisoformat(line[columns.index("TRADEDATE")])
            start_date = date + datetime.timedelta(days=1)
            if end_date and date > end_date:
                break
            low = line[columns.index("LOW")]
            high = line[columns.index("HIGH")]
            open = line[columns.index("OPEN")]
            close = line[columns.index("CLOSE")]
            if low is None and high is None and open is None and close is None:
                continue
            result.append(
                Candle(
                    date=date,
                    low=low,
                    high=high,
                    open=open,
                    close=close,
                    mid_price=line[columns.index("WAPRICE")],
                    numtrades=line[columns.index("NUMTRADES")],
                    volume=line[columns.index("VOLUME")],
                    value=line[columns.index("VALUE")],
                )
            )
        if len(data) == 0 or (end_date and start_date and start_date > end_date):
            break
    return result


def _merge_candles(first: list[Candle], second: list[Candle]) -> list[Candle]:
    i = 0
    j = 0
    result: list[Candle] = []
    while i < len(first) and j < len(second):
        if first[i].date == second[j].date:
            result.append(Candle.merge(first[i], second[j]))
            i += 1
            j += 1
        elif first[i].date < second[j].date:
            result.append(first[i])
            i += 1
        else:
            result.append(second[j])
            j += 1
    while i < len(first):
        result.append(first[i])
        i += 1
    while j < len(second):
        result.append(second[j])
        j += 1
    return result