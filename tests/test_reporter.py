"""Tests for the output/reporter module."""

import sys
import os
import json
import csv
import tempfile
sys.path.insert(0, "stockbot")

import pytest

from output.reporter import (
    _color_for_score,
    _signal_icon,
    cli_report_single,
    cli_report_summary,
    export_signals_to_json,
    export_signals_to_csv,
)


class TestColorForScore:
    def test_high_score_green(self):
        assert _color_for_score(90) == "green"
        assert _color_for_score(80) == "green"

    def test_mid_score_cyan(self):
        assert _color_for_score(70) == "cyan"
        assert _color_for_score(60) == "cyan"

    def test_low_mid_score_yellow(self):
        assert _color_for_score(50) == "yellow"
        assert _color_for_score(40) == "yellow"

    def test_low_score_red(self):
        assert _color_for_score(30) == "red"
        assert _color_for_score(0) == "red"


class TestSignalIcon:
    def test_buy_returns_buy_icon(self):
        assert "BUY" in _signal_icon("buy")

    def test_sell_returns_sell_icon(self):
        assert "SELL" in _signal_icon("sell")

    def test_other_returns_hold(self):
        assert "HOLD" in _signal_icon("neutral")
        assert "HOLD" in _signal_icon("hold")


class TestCLIReportSingle:
    def test_runs_with_valid_signal(self, sample_analysis_result):
        # Just ensure no exceptions
        cli_report_single(sample_analysis_result)

    def test_runs_with_sell_signal(self, sample_analysis_result):
        result = dict(sample_analysis_result)
        result["signal"] = "sell"
        cli_report_single(result)


class TestCLIReportSummary:
    def test_empty_consolidated(self):
        cli_report_summary([], 5.0, 100)

    def test_with_signals(self, sample_analysis_result):
        cli_report_summary([sample_analysis_result], 5.0, 10)

    def test_multiple_signals(self, sample_analysis_result):
        signals = [sample_analysis_result] * 3
        signals[0]["signal"] = "buy"
        signals[1]["signal"] = "sell"
        signals[2]["signal"] = "buy"
        cli_report_summary(signals, 10.0, 50)


class TestExportSignalsToJson:
    def test_returns_none_for_empty(self):
        assert export_signals_to_json([]) is None

    def test_exports_to_file(self, sample_analysis_result, monkeypatch, tmp_path):
        monkeypatch.setattr("output.reporter.OUTPUT_DIR", tmp_path)
        path = export_signals_to_json([sample_analysis_result])
        assert path is not None
        assert "signals_" in path
        with open(path) as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["ticker"] == "AAPL"
        assert data[0]["signal"] == "buy"

    def test_export_multiple(self, sample_analysis_result, monkeypatch, tmp_path):
        monkeypatch.setattr("output.reporter.OUTPUT_DIR", tmp_path)
        signals = [sample_analysis_result] * 3
        for i, s in enumerate(signals):
            s["ticker"] = f"TICK{i}"
        path = export_signals_to_json(signals)
        assert path is not None
        with open(path) as f:
            data = json.load(f)
        assert len(data) == 3


class TestExportSignalsToCsv:
    def test_returns_none_for_empty(self):
        assert export_signals_to_csv([]) is None

    def test_exports_to_file(self, sample_analysis_result, monkeypatch, tmp_path):
        monkeypatch.setattr("output.reporter.OUTPUT_DIR", tmp_path)
        path = export_signals_to_csv([sample_analysis_result])
        assert path is not None
        assert "signals_" in path
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["ticker"] == "AAPL"

    def test_csv_has_headers(self, sample_analysis_result, monkeypatch, tmp_path):
        monkeypatch.setattr("output.reporter.OUTPUT_DIR", tmp_path)
        path = export_signals_to_csv([sample_analysis_result])
        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            assert "ticker" in reader.fieldnames
            assert "price" in reader.fieldnames
            assert "signal" in reader.fieldnames
            assert "score" in reader.fieldnames
