from src.utils.logger import info, warning, error


# Test logging of INFO level message
def test_info_logging(caplog):
    # Enable capturing logs at INFO level
    with caplog.at_level("INFO"):
        info("Test info message")  # Log an INFO message
    # Check that the message appears in the captured logs
    assert "Test info message" in caplog.text


# Test logging of WARNING level message
def test_warning_logging(caplog):
    # Enable capturing logs at WARNING level
    with caplog.at_level("WARNING"):
        warning("Test warning message")  # Log a WARNING message
    # Check that the message appears in the captured logs
    assert "Test warning message" in caplog.text


# Test logging of ERROR level message
def test_error_logging(caplog):
    # Enable capturing logs at ERROR level
    with caplog.at_level("ERROR"):
        error("Test error message")  # Log an ERROR message
    # Check that the message appears in the captured logs
    assert "Test error message" in caplog.text
