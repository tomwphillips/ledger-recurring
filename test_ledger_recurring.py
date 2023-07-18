import tempfile
from datetime import date, datetime

from ledger_recurring import main


def test_monthly_transaction(tmp_path):
    config_file = tempfile.TemporaryFile()
    config_file.write(
        b"""
- name: mortgage
  rule:
    frequency: monthly
    start_date: 2023-01-03
  postings:
    - account: assets:current
      amount: 1000
    - account: liabilities:mortgage
      amount: -1000
"""
    )
    config_file.seek(0)

    output_file = tempfile.TemporaryFile("r+")
    main(config_file, output_file, datetime(2023, 2, 1), datetime(2023, 2, 28))

    output_file.seek(0)
    assert (
        output_file.read()
        == """2023-02-03 mortgage
\tassets:current\t1000
\tliabilities:mortgage\t-1000
"""
    )
