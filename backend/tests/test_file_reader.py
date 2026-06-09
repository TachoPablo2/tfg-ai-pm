import pytest
import io
from fastapi import UploadFile
from app.data.ingestion.file_reader import JiraFileReader
from app.core.exceptions import FileValidationError


class TestLeerArchivo:
    @pytest.mark.asyncio
    async def test_read_csv_utf8(self, csv_bytes):
        file = UploadFile(filename="test.csv", file=io.BytesIO(csv_bytes))
        df = await JiraFileReader.leer_archivo(file)
        assert len(df) == 2
        assert "Issue key" in df.columns

    @pytest.mark.asyncio
    async def test_read_csv_latin1(self):
        content = "Issue key,Summary\nPRO-101,Test tarea".encode("latin-1")
        file = UploadFile(filename="test.csv", file=io.BytesIO(content))
        df = await JiraFileReader.leer_archivo(file)
        assert len(df) == 1

    @pytest.mark.asyncio
    async def test_empty_file(self):
        file = UploadFile(filename="empty.csv", file=io.BytesIO(b""))
        with pytest.raises(FileValidationError):
            await JiraFileReader.leer_archivo(file)

    @pytest.mark.asyncio
    async def test_invalid_extension(self):
        file = UploadFile(filename="data.pdf", file=io.BytesIO(b"data"))
        with pytest.raises(FileValidationError, match="pdf"):
            await JiraFileReader.leer_archivo(file)

    @pytest.mark.asyncio
    async def test_no_filename(self):
        file = UploadFile(filename=None, file=io.BytesIO(b"data"))
        with pytest.raises(FileValidationError, match="nombre"):
            await JiraFileReader.leer_archivo(file)

    @pytest.mark.asyncio
    async def test_file_too_large(self):
        large_content = b"x" * (60 * 1024 * 1024)
        file = UploadFile(filename="large.csv", file=io.BytesIO(large_content))
        with pytest.raises(FileValidationError, match="excede"):
            await JiraFileReader.leer_archivo(file)

    @pytest.mark.asyncio
    async def test_csv_fails_all_encodings(self, mocker):
        mocker.patch(
            "app.data.ingestion.file_reader.pd.read_csv",
            side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "mock"),
        )
        file = UploadFile(filename="test.csv", file=io.BytesIO(b"a,b\n1,2"))
        with pytest.raises(FileValidationError, match="encoding"):
            await JiraFileReader.leer_archivo(file)

    @pytest.mark.asyncio
    async def test_sanitize_filename_with_newlines(self):
        content = "a,b\n1,2".encode()
        file = UploadFile(filename="test\nfile.csv", file=io.BytesIO(content))
        df = await JiraFileReader.leer_archivo(file)
        assert len(df) == 1


class TestSanitizeFilename:
    def test_removes_newlines(self):
        from app.data.ingestion.file_reader import _sanitize_filename
        assert _sanitize_filename("test\nfile.csv") == "testfile.csv"

    def test_truncates_long_names(self):
        from app.data.ingestion.file_reader import _sanitize_filename
        long_name = "a" * 300 + ".csv"
        result = _sanitize_filename(long_name)
        assert len(result) <= 200
