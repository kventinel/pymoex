#!/usr/bin/env python3
import datetime
import unittest

import moexapi


class Tickers(unittest.TestCase):
    def test_shares(self):
        for ticker in ["SBERP03", "SELG-003D", "MAGN-002D"]:
            moexapi.get_ticker(ticker)


class Candles(unittest.TestCase):
    def test_index(self):
        ticker = moexapi.get_ticker("IMOEX")
        candles = moexapi.get_candles(
            ticker,
            start_date=datetime.date(2023, 1, 1),
            end_date=datetime.date(2023, 1, 31),
        )
        history = moexapi.get_history(
            ticker,
            start_date=datetime.date(2023, 1, 1),
            end_date=datetime.date(2023, 1, 31),
        )
        self.assertGreater(len(candles), 0)
        self.assertGreater(len(history), 0)

    def test_share(self):
        for ticker in ["GAZP", "SBERP", "MSRS"]:
            ticker = moexapi.get_ticker(ticker)
            candles = moexapi.get_candles(
                ticker,
                start_date=datetime.date(2023, 1, 1),
                end_date=datetime.date(2023, 1, 31),
            )
            history = moexapi.get_history(
                ticker,
                start_date=datetime.date(2023, 1, 1),
                end_date=datetime.date(2023, 1, 31),
            )
            self.assertGreater(len(candles), 0)
            self.assertGreater(len(history), 0)

    def test_currency(self):
        ticker = moexapi.get_ticker("CNY")
        candles = moexapi.get_candles(
            ticker,
            start_date=datetime.date(2023, 1, 1),
            end_date=datetime.date(2023, 1, 31),
        )
        history = moexapi.get_history(
            ticker,
            start_date=datetime.date(2023, 1, 1),
            end_date=datetime.date(2023, 1, 31),
        )
        self.assertGreater(len(candles), 0)
        self.assertGreater(len(history), 0)

    def test_midprice(self):
        ticker = moexapi.get_ticker('SU26229RMFS3')
        history = moexapi.get_history(ticker, start_date=datetime.date(2019, 6, 5), end_date=datetime.date(2019, 6, 5))
        self.assertEqual(len(history), 1)
        self.assertAlmostEqual(history[0].mid_price, 97.865)


class Dividends(unittest.TestCase):
    def test_dividends(self):
        for ticker in ["CHMF", "MOEX", "SFIN"]:
            ticker = moexapi.get_ticker(ticker, market=moexapi.Markets.SHARES)
            dividends = moexapi.get_dividends(ticker)
            self.assertGreater(len(dividends), 0)


class Bonds(unittest.TestCase):
    def test_bonds(self):
        ofz29013 = moexapi.Bond(moexapi.get_ticker('ОФЗ29013'))
        self.assertEqual(ofz29013.issue_date, datetime.date(2020, 4, 8))
        self.assertEqual(ofz29013.mat_date, datetime.date(2030, 9, 18))
        self.assertEqual(ofz29013.early_repayment, True)
        self.assertEqual(ofz29013.evening_session, True)
        self.assertAlmostEqual(ofz29013.coupon_percent, 4.0)
        self.assertEqual(ofz29013.coupon_frequency, 4)


if __name__ == '__main__':
    unittest.main()
