import pytest

from unittest.mock import MagicMock, call, patch
from urllib.error import HTTPError, URLError

import speedtest


class TestValidateUrl:
    """Тесты проверки URL."""

    def test_valid_http_url(self):
        speedtest.validate_url("http://example.com/image.jpg")

    def test_valid_https_url(self):
        speedtest.validate_url("https://example.com/image.jpg")

    @pytest.mark.parametrize(
        "url",
        [
            "invalid-url",
            "ftp://example.com/file",
            "example.com",
            "",
        ],
    )
    def test_invalid_url(self, url):
        with pytest.raises(ValueError):
            speedtest.validate_url(url)


class TestDownloadOnce:
    """Тесты скачивания одного файла."""

    @patch("speedtest.time.perf_counter", side_effect=[10.0, 12.5])
    @patch("speedtest.urlopen")
    def test_successful_download(self, mock_urlopen, mock_timer):
        # Создаём имитацию HTTP-ответа
        response = MagicMock()
        response.read.side_effect = [
            b"Hello ",
            b"World",
            b"",
        ]

        mock_urlopen.return_value.__enter__.return_value = response

        # Выполняем скачивание
        byte_count, elapsed_seconds = speedtest.download_once(
            "https://example.com/file"
        )

        # Проверяем результат
        assert byte_count == 11
        assert elapsed_seconds == 2.5

        # Проверяем, что ответ читался до конца
        assert response.read.call_count == 3

    @patch("speedtest.urlopen")
    def test_http_error(self, mock_urlopen):
        # Имитируем HTTP-ошибку 404
        mock_urlopen.side_effect = HTTPError(
            "https://example.com/file",
            404,
            "Not Found",
            {},
            None,
        )

        with pytest.raises(HTTPError) as error:
            speedtest.download_once("https://example.com/file")

        assert error.value.code == 404

    @patch("speedtest.urlopen")
    def test_connection_error(self, mock_urlopen):
        # Имитируем ошибку подключения
        mock_urlopen.side_effect = URLError("Connection failed")

        with pytest.raises(URLError):
            speedtest.download_once("https://example.com/file")


class TestMain:
    """Тесты основной функции программы."""

    @patch("sys.argv", ["speedtest.py", "https://example.com/file"])
    @patch("speedtest.download_once")
    def test_successful_execution(self, mock_download, capsys):
        # Имитируем успешные результаты десяти запросов
        mock_download.return_value = (1_000_000, 2.0)

        result = speedtest.main()

        output = capsys.readouterr().out

        assert result == 0
        assert mock_download.call_count == 10

        assert "Выполнено запросов: 10" in output
        assert "10,000,000 байт" in output
        assert "Среднее время запроса: 2.000 с" in output
        assert "Средняя скорость скачивания: 0.500 MB/s" in output

    @patch("sys.argv", ["speedtest.py", "invalid-url"])
    def test_invalid_url(self, capsys):
        result = speedtest.main()

        output = capsys.readouterr()

        assert result == 1
        assert "Некорректный URL" in output.err

    @patch("sys.argv", ["speedtest.py", "https://example.com/file"])
    @patch("speedtest.download_once")
    def test_download_error(self, mock_download, capsys):
        # Имитируем HTTP-ошибку
        mock_download.side_effect = HTTPError(
            "https://example.com/file",
            404,
            "Not Found",
            {},
            None,
        )

        result = speedtest.main()

        output = capsys.readouterr()

        assert result == 1
        assert "404" in output.err

    @patch("sys.argv", ["speedtest.py", "https://example.com/file"])
    @patch("speedtest.download_once")
    def test_keyboard_interrupt(self, mock_download, capsys):
        # Имитируем прерывание программы
        mock_download.side_effect = KeyboardInterrupt

        result = speedtest.main()

        output = capsys.readouterr()

        assert result == 130
        assert "прервано пользователем" in output.err