#!/usr/bin/env python3
import datetime
import unittest

import moexapi


class Candles(unittest.TestCase):
    def test_index(self):
        ticker = moexapi.get_ticker("IMOEX")
        candles = moexapi.get_candles(ticker)
        history = moexapi.get_history(ticker)
        self.assertGreater(len(candles), 0)
        self.assertGreater(len(history), 0)

    def test_share(self):
        ticker = moexapi.get_ticker("GAZP")
        candles = moexapi.get_candles(ticker)
        history = moexapi.get_history(ticker)
        self.assertGreater(len(candles), 0)
        self.assertGreater(len(history), 0)

    def test_currency(self):
        ticker = moexapi.get_ticker("CNY")
        candles = moexapi.get_candles(ticker)
        history = moexapi.get_history(ticker)
        self.assertGreater(len(candles), 0)
        self.assertGreater(len(history), 0)

    def test_midprice(self):
        ticker = moexapi.get_ticker('SU26229RMFS3')
        history = moexapi.get_history(ticker, start_date=datetime.date(2019, 6, 5), end_date=datetime.date(2019, 6, 5))
        self.assertEqual(len(history), 1)
        self.assertAlmostEqual(history[0].mid_price, 97.865)


class Dividends(unittest.TestCase):
    def test_dividends(self):
        for ticker in ["CHMF", "MOEX"]:
            ticker = moexapi.get_ticker(ticker, market=moexapi.Markets.SHARES)
            dividends = moexapi.get_dividends(ticker)
            self.assertGreater(len(dividends), 10)


if __name__ == '__main__':
    unittest.main()