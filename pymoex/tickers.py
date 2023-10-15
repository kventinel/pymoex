import typing as T

import dataclasses

from . import boards
from . import markets
from . import utils


@dataclasses.dataclass
class OneBoardTicker:
    secid: str
    market: markets.Markets
    board: str
    shortname: str
    price: float


@dataclasses.dataclass
class Ticker:
    secid: str
    boards: list[str]
    market: markets.Markets
    shortname: str
    price: float
    subtype: T.Optional[str]

    def __init__(self, secid: str, market: T.Optional[markets.Markets] = None, board: T.Optional[str] = None):
        tickers = _parse_tickers(market=market, board=board, secid=secid)
        assert len(tickers) > 0, f"Can't find ticker {secid}"
        if any(ticker.market != tickers[0].market for ticker in tickers):
            raise RuntimeError(f"Different markets for ticker {secid}")
        if any(ticker.shortname != tickers[0].shortname for ticker in tickers):
            raise RuntimeError(f"Different shortnames for ticker {secid}")
        ticker_boards = [ticker.board for ticker in tickers]
        main_tickers = [ticker for ticker in tickers if ticker.board == boards.get_main_board(ticker_boards)]
        if len(main_tickers) != 1:
            raise RuntimeError(f"Can't find main ticker {main_tickers}")
        self.secid = secid
        self.boards = list(set(ticker.board for ticker in tickers))
        self.market = tickers[0].market
        self.shortname = tickers[0].shortname
        self.price = main_tickers[0].price
        self.subtype = _parse_subtype(secid)


class Tickers(list[Ticker]):
    def __init__(self, market: T.Optional[markets.Markets] = None, board: T.Optional[str] = None):
        tickers = _parse_tickers(market=market, board=board)
        market_secids = set((ticker.market, ticker.secid) for ticker in tickers)
        secids = set(ticker.secid for ticker in tickers)
        if len(secids) != len(market_secids):
            raise RuntimeError(f"One secid in different markets")
        for market, secid in market_secids:
            self.append(Ticker(secid=secid, market=market))


def _parse_response(market: markets.Markets, response: T.Any) -> list[OneBoardTicker]:
    securities = response["securities"]
    sec_columns: list = securities["columns"]
    sec_data: list = securities["data"]
    marketdata = response["marketdata"]
    market_columns: list = marketdata["columns"]
    market_data: list = marketdata["data"]
    assert len(sec_data) == len(market_data)
    result = []
    for sec_line, market_line in zip(sec_data, market_data):
        secid = sec_line[sec_columns.index("SECID")]
        price = sec_line[sec_columns.index("PREVPRICE")]
        if price is None:
            price = market_line[market_columns.index("LAST")]
        result.append(OneBoardTicker(
            secid=secid,
            board=sec_line[sec_columns.index("BOARDID")],
            market=market,
            shortname=sec_line[sec_columns.index("SHORTNAME")],
            price=price,
        ))
    return result


def _parse_tickers(
    market: T.Optional[markets.Markets] = None,
    board: T.Optional[str] = None,
    secid: T.Optional[str] = None
) -> list[OneBoardTicker]:
    secid_str = f"/securities/{secid}" if secid else "/securities"
    board_str = f"/boards/{board}" if board else ""
    if market:
        market_str = f"/markets/{market}" if market else ""
        url = f"https://iss.moex.com/iss/engines/stock{market_str}{board_str}{secid_str}.json"
        return _parse_response(market, utils.json_api_call(url))
    tickers = []
    for market in markets.Markets:
        tickers.extend(_parse_tickers(secid=secid, board=board, market=market))
    return tickers


def _parse_subtype(secid: str) -> T.Optional[str]:
    response = utils.json_api_call(f"https://iss.moex.com/iss/securities/{secid}.json")
    description = response["description"]
    columns = description["columns"]
    data = description["data"]
    for line in data:
        if line[columns.index("name")] == "SECSUBTYPE":
            return line[columns.index("value")]
    return None
